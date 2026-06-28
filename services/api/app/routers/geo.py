"""Geo resolve endpoint — lat/lng → Delhi ward + zone + jurisdiction."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import Services, get_services

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/resolve")
async def resolve(
    lat: float = Query(...),
    lng: float = Query(...),
    svc: Services = Depends(get_services),
) -> dict:
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
