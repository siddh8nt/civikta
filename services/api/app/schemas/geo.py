"""Geo resolver contract (PRD §24). lat/lng -> Delhi administrative geography."""

from __future__ import annotations

from pydantic import BaseModel


class GeoResolution(BaseModel):
    local_body_type: str | None = None      # MCD / NDMC / DCB
    revenue_district: str | None = None
    tehsil_subdivision: str | None = None
    mcd_zone: str | None = None
    ward_no: int | None = None
    ward_name: str | None = None
    locality_name: str | None = None
    landmark: str | None = None
    in_delhi: bool = True
    confidence: float = 0.5
