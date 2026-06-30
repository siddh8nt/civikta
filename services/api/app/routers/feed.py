"""Public feed + map endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import Services, get_services
from app.schemas.issue import IssueSummary

router = APIRouter(prefix="/api", tags=["feed"])


@router.get("/feed/nearby", response_model=list[IssueSummary], summary="Get civic issues near a GPS location")
async def feed_nearby(
    lat: float = Query(..., description="Latitude (decimal degrees)"),
    lng: float = Query(..., description="Longitude (decimal degrees)"),
    radius: float = Query(3000.0, description="Search radius in metres (default 3 km)"),
    issue_type: str | None = Query(None, description="Filter by issue type slug"),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    """
    Powers the **citizen feed** — returns active issues within `radius` metres of the given GPS point,
    sorted by recency. Used on the home screen to show what's happening in the citizen's neighbourhood.
    """
    return services.feed.nearby(lat, lng, radius, issue_type_slug=issue_type)


@router.get("/map/issues", response_model=list[IssueSummary], summary="Get all issues within a map viewport bounding box")
async def map_issues(
    minLat: float = Query(...), minLng: float = Query(...),
    maxLat: float = Query(...), maxLng: float = Query(...),
    category: str | None = Query(None, description="Filter by category slug"),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    """
    Powers the **interactive map view** — returns all active issues whose coordinates fall within the
    given bounding box. Called whenever the citizen pans or zooms the Google Maps view.
    """
    return services.feed.viewport(minLat, minLng, maxLat, maxLng, issue_category_slug=category)
