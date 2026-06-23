"""Geo resolver (PRD §24). lat/lng -> Delhi administrative geography.

STUB: nearest-centroid lookup over a small reference set, no PostGIS needed.
FUTURE: implement against `delhi_boundaries` with ST_Contains point-in-polygon
(see SupabaseRepository). Same `GeoResolution` contract either way.
"""

from __future__ import annotations

from app.core.geoutil import haversine_m
from app.schemas.geo import GeoResolution

# Delhi rough bounding box
_DELHI_BBOX = (28.40, 76.84, 28.88, 77.35)  # min_lat, min_lng, max_lat, max_lng

# reference centroids: (lat, lng, local_body, ward_no, ward_name, locality)
_REFERENCES = [
    (28.5677, 77.2433, "MCD", 42, "Lajpat Nagar", "Lajpat Nagar"),
    (28.6315, 77.2167, "NDMC", 1, "Connaught Place", "Connaught Place"),
    (28.6519, 77.1909, "MCD", 76, "Karol Bagh", "Karol Bagh"),
    (28.7050, 77.1180, "MCD", 24, "Rohini", "Rohini"),
    (28.5823, 77.0500, "MCD", 127, "Dwarka", "Dwarka"),
    (28.5494, 77.2001, "MCD", 150, "Hauz Khas", "Hauz Khas"),
    (28.6692, 77.4538, "MCD", 200, "Anand Vihar", "Anand Vihar"),
    (28.5921, 77.0460, "DCB", 1, "Delhi Cantonment", "Delhi Cantt"),
]


class GeoService:
    def resolve(self, lat: float, lng: float) -> GeoResolution:
        min_lat, min_lng, max_lat, max_lng = _DELHI_BBOX
        in_delhi = min_lat <= lat <= max_lat and min_lng <= lng <= max_lng

        nearest = min(_REFERENCES, key=lambda r: haversine_m(lat, lng, r[0], r[1]))
        dist = haversine_m(lat, lng, nearest[0], nearest[1])
        # confidence drops with distance from the nearest known centroid
        confidence = max(0.3, min(0.9, 1.0 - dist / 8000))

        return GeoResolution(
            local_body_type=nearest[2] if in_delhi else None,
            ward_no=nearest[3] if in_delhi else None,
            ward_name=nearest[4] if in_delhi else None,
            locality_name=nearest[5] if in_delhi else None,
            in_delhi=in_delhi,
            confidence=round(confidence, 2),
        )
