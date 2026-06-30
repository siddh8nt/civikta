"""Geo resolve endpoint — lat/lng → Delhi ward + zone + jurisdiction."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import Services, get_services

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/resolve", summary="Resolve GPS coordinates to Delhi ward, zone, and responsible authority")
async def resolve(
    lat: float = Query(..., description="Latitude (decimal degrees, WGS84)"),
    lng: float = Query(..., description="Longitude (decimal degrees, WGS84)"),
    svc: Services = Depends(get_services),
) -> dict:
    """
    Core jurisdiction resolution engine. Given a GPS point, returns:
    - **ward_no / ward_name**: one of Delhi's 272 municipal wards
    - **local_body_type**: `MCD | NDMC | DCB` — which municipal body governs this location
    - **zone**: MCD administrative zone (e.g. South, Rohini, Shahdara North) — used to route to the correct MCD zone officer
    - **locality_name**: nearest named locality
    - **in_delhi**: whether the point falls within NCT Delhi boundaries

    This endpoint is called automatically when the citizen pins a location, and its output determines which authority receives the issue.

    Try it: `lat=28.6139, lng=77.2090` (Connaught Place → NDMC)
    """
    res = svc.geo.resolve(lat, lng)
    return {
        "ward_no":          res.ward_no,
        "ward_name":        res.ward_name,
        "local_body_type":  res.local_body_type,   # MCD | NDMC | DCB (frontend contract)
        "zone":             res.mcd_zone,
        "locality_name":    res.locality_name,
        "in_delhi":         res.in_delhi,
        "confidence":       res.confidence,
        "debug": {
            "input":               {"lat": lat, "lng": lng},
            "ward_method":         res.ward_method,
            "jurisdiction_method": res.jurisdiction_method,
        },
    }
