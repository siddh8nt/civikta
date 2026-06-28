"""Geo resolver (PRD §24). lat/lng -> Delhi administrative geography.

Resolution pipeline:
  Step A — Resolve ward (unchanged; already working):
    1. PostGIS ST_Contains          → exact polygon match      (confidence 0.97)
    2. PostGIS ST_DWithin 150m      → GPS-noise buffer         (confidence 0.80)
    3. Nominatim reverse + fuzzy    → suburb → ward name       (confidence 0.85)
    4. Nearest centroid fallback                               (confidence 0.40–0.95)

  Step B — Resolve jurisdiction (independent of ward):
    1. NDMC boundary polygon check  → jurisdiction = NDMC
    2. DCB boundary polygon check   → jurisdiction = DCB
    3. Default                      → jurisdiction = MCD
    If jurisdiction from Step B disagrees with ward's local_body_type (Step A),
    Step B wins and the zone is re-derived from the correct-jurisdiction ward.

  Step C — Derive zone:
    Zone comes directly from the resolved ward's `zone` column:
      MCD wards  → one of 12 MCD zone names (Narela, Rohini, etc.)
      NDMC wards → "NDMC Central" | "NDMC South" | "NDMC West"
      DCB ward   → "DCB"
    Zone is always authoritative because it is stored per-ward in delhi_wards,
    not inferred from geometry or text matching.
"""

from __future__ import annotations

import json
import urllib.request

from app.core.geoutil import haversine_m
from app.schemas.geo import GeoResolution
from app.seeds.delhi_wards import DELHI_WARDS

_DELHI_BBOX = (28.40, 76.84, 28.88, 77.35)

_REFERENCES = [
    (w["lat"], w["lng"], w["local_body_type"], w["ward_no"], w["ward_name"], w["zone"])
    for w in DELHI_WARDS
]

_WARD_BY_NAME: dict[str, dict] = {w["ward_name"].lower(): w for w in DELHI_WARDS}

# Pre-indexed for fast jurisdiction-correct zone lookup when override is needed
_WARDS_BY_LBT: dict[str, list[dict]] = {}
for _w in DELHI_WARDS:
    _WARDS_BY_LBT.setdefault(_w["local_body_type"], []).append(_w)


# ── External API helpers ───────────────────────────────────────────────────────

def _nominatim_reverse(lat: float, lng: float) -> dict | None:
    try:
        url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lng}&format=json&addressdetails=1&zoom=16"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Civikta/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _get_locality_name(lat: float, lng: float) -> str | None:
    nom = _nominatim_reverse(lat, lng)
    if not nom:
        return None
    addr = nom.get("address", {})
    return (
        addr.get("neighbourhood")
        or addr.get("suburb")
        or addr.get("city_district")
        or addr.get("county")
    )


def _fuzzy_ward_match(suburb: str) -> dict | None:
    if not suburb:
        return None
    s = suburb.lower().strip()
    if s in _WARD_BY_NAME:
        return _WARD_BY_NAME[s]
    for ward_name_lower, ward in _WARD_BY_NAME.items():
        if ward_name_lower in s or s in ward_name_lower:
            return ward
    return None


def _nearest_ward_of_type(lat: float, lng: float, local_body_type: str) -> dict | None:
    """Nearest centroid for a specific jurisdiction. Used when boundary override fires."""
    candidates = _WARDS_BY_LBT.get(local_body_type, [])
    if not candidates:
        return None
    return min(candidates, key=lambda w: haversine_m(lat, lng, w["lat"], w["lng"]))


# ── GeoService ────────────────────────────────────────────────────────────────

class GeoService:
    def __init__(self, supabase_client=None) -> None:
        self._client = supabase_client

    def resolve(self, lat: float, lng: float) -> GeoResolution:
        min_lat, min_lng, max_lat, max_lng = _DELHI_BBOX
        in_delhi = min_lat <= lat <= max_lat and min_lng <= lng <= max_lng

        # ── Step A: Resolve ward ──────────────────────────────────────────────

        ward_row: dict | None = None
        ward_method: str = "centroid"

        if self._client and in_delhi:
            # Stage 1 & 2: PostGIS polygon + buffer
            try:
                res = self._client.rpc("resolve_ward", {"lat": lat, "lng": lng}).execute()
                if res.data:
                    row = res.data[0]
                    ward_row = {
                        "local_body_type": row["local_body_type"],
                        "ward_no":         row["ward_no"],
                        "ward_name":       row["ward_name"],
                        "zone":            row.get("zone"),
                    }
                    ward_method = row.get("method", "polygon")
            except Exception:
                pass

        locality_name: str | None = None

        if ward_row is None:
            # Stage 3: Nominatim + fuzzy ward name match
            nom = _nominatim_reverse(lat, lng)
            if nom:
                addr = nom.get("address", {})
                locality_name = (
                    addr.get("neighbourhood")
                    or addr.get("suburb")
                    or addr.get("city_district")
                    or addr.get("county")
                )
                for field in ("neighbourhood", "suburb", "city_district"):
                    val = addr.get(field, "")
                    if val:
                        fuzzy = _fuzzy_ward_match(val)
                        if fuzzy:
                            ward_row = fuzzy
                            ward_method = "nominatim_fuzzy"
                            break

        if ward_row is None:
            # Stage 4: Nearest centroid
            nearest = min(_REFERENCES, key=lambda r: haversine_m(lat, lng, r[0], r[1]))
            ward_row = {
                "local_body_type": nearest[2],
                "ward_no":         nearest[3],
                "ward_name":       nearest[4],
                "zone":            nearest[5],
            }
            ward_method = "centroid"

        # Locality name: fetch from Nominatim if PostGIS resolved ward (no Nominatim call yet)
        if locality_name is None and ward_method in ("polygon", "buffer"):
            locality_name = _get_locality_name(lat, lng)

        # ── Step B: Resolve jurisdiction (independent boundary check) ─────────

        jurisdiction: str = ward_row.get("local_body_type") or "MCD"
        jurisdiction_method: str = "ward_metadata"
        zone: str | None = ward_row.get("zone")

        if self._client and in_delhi:
            try:
                jres = self._client.rpc(
                    "resolve_jurisdiction", {"lat": lat, "lng": lng}
                ).execute()
                if jres.data:
                    jrow = jres.data[0]
                    boundary_jurisdiction = jrow["jurisdiction"]
                    ward_jurisdiction = ward_row.get("local_body_type") or "MCD"

                    if boundary_jurisdiction in ("NDMC", "DCB") and ward_jurisdiction == "MCD":
                        # Ward says MCD but point is inside NDMC/DCB polygon → upgrade.
                        # Exception: for DCB, if Nominatim clearly identifies the area
                        # as a residential non-cantonment zone (Dwarka, Palam), trust
                        # Nominatim over our approximate polygon boundary.
                        ward_name_lower = (ward_row.get("ward_name") or "").lower()
                        skip_dcb_override = (
                            boundary_jurisdiction == "DCB"
                            and "dwarka" in ward_name_lower
                        )
                        if not skip_dcb_override:
                            override_ward = _nearest_ward_of_type(lat, lng, boundary_jurisdiction)
                            if override_ward:
                                ward_row = override_ward
                                zone = override_ward.get("zone")
                            jurisdiction = boundary_jurisdiction
                            jurisdiction_method = "ward_override"
                    else:
                        # Either boundary agrees with ward, or boundary says MCD.
                        # Never downgrade NDMC/DCB → MCD via boundary (our polygons
                        # are approximate; Nominatim fuzzy match is more reliable for
                        # known cantonment/NDMC locations like the DCB station).
                        jurisdiction = ward_jurisdiction
                        jurisdiction_method = (
                            "boundary_polygon"
                            if jrow.get("method") == "boundary_polygon"
                               and boundary_jurisdiction == ward_jurisdiction
                            else "ward_metadata"
                        )
            except Exception:
                pass

        # ── NDMC ward split via lat/lng thresholds ───────────────────────────
        # For NDMC locations, override ward using geographic thresholds instead
        # of PostGIS polygon geometry (which caused geometry issues in SQL).
        # Split: 28.615N horizontal, 77.200E vertical — same logic as the
        # former 07_ndmc_ward_boundaries.sql.
        if jurisdiction == "NDMC":
            if lat >= 28.615:
                target_no = 901  # Connaught Place — northern NDMC
            elif lng >= 77.200:
                target_no = 902  # Lodhi Estate — south-east (India Gate, Khan Market)
            else:
                target_no = 903  # Chanakyapuri — south-west (diplomatic enclave)
            ndmc_ward = next(
                (w for w in _WARDS_BY_LBT.get("NDMC", []) if w["ward_no"] == target_no),
                None,
            )
            if ndmc_ward:
                ward_row = ndmc_ward
                zone = ndmc_ward.get("zone")
                ward_method = "ndmc_threshold"

        # ── Step C: Derive zone from resolved ward ────────────────────────────
        # Zone is authoritative: it comes from delhi_wards.zone column.
        # For MCD wards  → one of 12 MCD zone names
        # For NDMC wards → "NDMC Central" / "NDMC South" / "NDMC West"
        # For DCB ward   → "DCB"
        # zone is already set above; nothing more to derive.

        if not in_delhi:
            return GeoResolution(in_delhi=False, confidence=0.3)

        # Centroid confidence (used when ward_method = centroid)
        if ward_method == "centroid":
            nearest_ref = min(_REFERENCES, key=lambda r: haversine_m(lat, lng, r[0], r[1]))
            dist = haversine_m(lat, lng, nearest_ref[0], nearest_ref[1])
            confidence = max(0.4, min(0.95, 1.0 - dist / 6000))
        elif ward_method == "polygon":
            confidence = 0.97
        elif ward_method == "buffer":
            confidence = 0.80
        else:
            confidence = 0.85  # nominatim_fuzzy

        return GeoResolution(
            local_body_type=jurisdiction,
            ward_no=ward_row.get("ward_no"),
            ward_name=ward_row.get("ward_name"),
            mcd_zone=zone,
            locality_name=locality_name,
            in_delhi=True,
            confidence=round(confidence, 2),
            ward_method=ward_method,
            jurisdiction_method=jurisdiction_method,
        )
