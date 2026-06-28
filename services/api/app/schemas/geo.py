"""Geo resolver contract (PRD §24). lat/lng -> Delhi administrative geography."""

from __future__ import annotations

from pydantic import BaseModel


class GeoResolution(BaseModel):
    # ── Core fields (persisted to issues table) ───────────────────────────────
    local_body_type: str | None = None    # MCD | NDMC | DCB  (jurisdiction)
    revenue_district: str | None = None
    tehsil_subdivision: str | None = None
    mcd_zone: str | None = None           # MCD zone name, or NDMC zone, or "DCB"
    ward_no: int | None = None
    ward_name: str | None = None
    locality_name: str | None = None
    landmark: str | None = None
    in_delhi: bool = True
    confidence: float = 0.5

    # ── Debug / provenance fields (not persisted, API-only) ──────────────────
    # ward_method: how the ward was resolved
    #   "polygon"          — ST_Contains matched a boundary polygon
    #   "buffer"           — ST_DWithin 150m matched (GPS noise / border point)
    #   "nominatim_fuzzy"  — Nominatim reverse → fuzzy ward name match
    #   "centroid"         — nearest centroid fallback
    ward_method: str | None = None

    # jurisdiction_method: how local_body_type was determined
    #   "boundary_polygon" — resolved via jurisdiction_boundaries polygon table
    #   "ward_metadata"    — taken directly from resolved ward's local_body_type
    #   "ward_override"    — boundary polygon disagreed with ward; boundary won
    jurisdiction_method: str | None = None
