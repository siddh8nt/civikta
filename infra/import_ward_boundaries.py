#!/usr/bin/env python3
"""
Import Delhi ward boundaries from OpenStreetMap (Overpass API) into Supabase.

Prerequisites:
    pip install supabase shapely

Usage:
    cd civikta/infra
    python import_ward_boundaries.py

What it does:
  1. Queries Overpass for all admin_level=8 and =9 relations within Delhi NCT
  2. Assembles member ways into Polygon/MultiPolygon geometries via Shapely
  3. Fuzzy-matches OSM relation names against delhi_wards in Supabase
  4. Calls update_ward_boundary() RPC to persist geometry where score >= 0.55
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

from supabase import create_client

# ── Config ────────────────────────────────────────────────────────────────────

SUPABASE_URL = "https://mfcpuickdbhtgdjaybub.supabase.co"
SUPABASE_SERVICE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mY3B1aWNrZGJodGdkamF5YnViIiwi"
    "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjMxMzUzMCwiZXhwIjoyMDk3"
    "ODg5NTMwfQ._PwkSchxYe4nUJ6Q56M1z0Lancvzy7q6v-tFKcYsOfw"
)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# admin_level=4 in OSM = Indian state/UT level → Delhi NCT
OVERPASS_QUERY = """
[out:json][timeout:180];
area["name"="Delhi"]["admin_level"="4"]->.delhi;
(
  relation["admin_level"="8"](area.delhi);
  relation["admin_level"="9"](area.delhi);
);
out geom;
"""

MATCH_THRESHOLD = 0.55   # minimum fuzzy score to accept a name match

# ── Helpers ───────────────────────────────────────────────────────────────────

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _best_match(name: str, wards: list[dict]) -> tuple[dict | None, float]:
    best_ward: dict | None = None
    best_score = 0.0
    name_l = name.lower()
    for w in wards:
        wn = w["ward_name"].lower()
        score = _similarity(name_l, wn)
        # Boost if one string fully contains the other
        if wn in name_l or name_l in wn:
            score = max(score, 0.75)
        if score > best_score:
            best_score = score
            best_ward = w
    return best_ward, best_score


def _assemble_geometry(members: list[dict]):
    """Chain way members into a Shapely MultiPolygon. Returns None on failure."""
    try:
        from shapely.geometry import MultiPolygon, LineString, mapping
        from shapely.ops import linemerge, polygonize, unary_union

        lines = []
        for m in members:
            if m.get("type") != "way":
                continue
            coords = [(pt["lon"], pt["lat"]) for pt in m.get("geometry", [])]
            if len(coords) >= 2:
                lines.append(LineString(coords))

        if not lines:
            return None

        merged = linemerge(lines)
        polys = list(polygonize(merged))
        if not polys:
            return None

        geom = unary_union(polys)
        if geom.is_empty:
            return None
        if geom.geom_type == "Polygon":
            geom = MultiPolygon([geom])
        if geom.geom_type != "MultiPolygon":
            return None
        return geom
    except Exception as exc:
        return None


def fetch_overpass() -> list[dict]:
    print("Querying Overpass API for Delhi ward relations…")
    data = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        headers={
            "User-Agent": "Civikta-import/1.0 (civic hackathon)",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=200) as resp:
        result = json.loads(resp.read())

    relations = [e for e in result.get("elements", []) if e["type"] == "relation"]
    print(f"  → {len(relations)} relations returned")
    return relations


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        from shapely.geometry import MultiPolygon  # noqa: F401
    except ImportError:
        print("ERROR: shapely is required.\n  pip install shapely")
        return

    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    print("Loading wards from Supabase…")
    res = client.table("delhi_wards").select("ward_no, ward_name").execute()
    wards: list[dict] = res.data
    print(f"  → {len(wards)} wards in DB")

    try:
        relations = fetch_overpass()
    except Exception as exc:
        print(f"ERROR: Overpass fetch failed: {exc}")
        return

    matched = 0
    skipped = 0

    for elem in relations:
        tags = elem.get("tags", {})
        # Prefer English name; fall back to local name
        name = tags.get("name:en") or tags.get("name") or ""
        if not name:
            skipped += 1
            continue

        ward, score = _best_match(name, wards)
        if not ward or score < MATCH_THRESHOLD:
            print(f"  SKIP no-match (score={score:.2f}): {name!r}")
            skipped += 1
            continue

        from shapely.geometry import mapping
        geom = _assemble_geometry(elem.get("members", []))
        if geom is None:
            print(f"  SKIP no-geom: {name!r} → {ward['ward_name']}")
            skipped += 1
            continue

        geojson_str = json.dumps(mapping(geom))

        try:
            client.rpc("update_ward_boundary", {
                "p_ward_no": ward["ward_no"],
                "p_geojson": geojson_str,
            }).execute()
            print(f"  OK  score={score:.2f}  {name!r} → {ward['ward_name']} (#{ward['ward_no']})")
            matched += 1
        except Exception as exc:
            print(f"  ERROR ward {ward['ward_no']}: {exc}")
            skipped += 1

        time.sleep(0.05)  # be polite to Supabase

    print(f"\nImport complete: {matched} boundaries loaded, {skipped} skipped/failed.")
    if matched > 0:
        print("Run the backend geo resolve endpoint to verify:")
        print("  curl 'http://localhost:8000/api/geo/resolve?lat=28.6139&lng=77.2090'")


if __name__ == "__main__":
    main()
