"""Public feed + map endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import Services, get_services
from app.schemas.issue import IssueSummary

router = APIRouter(prefix="/api", tags=["feed"])


@router.get("/feed/nearby", response_model=list[IssueSummary])
async def feed_nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(3000.0, description="metres"),
    issue_type: str | None = Query(None),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    return services.feed.nearby(lat, lng, radius, issue_type_slug=issue_type)


@router.get("/map/issues", response_model=list[IssueSummary])
async def map_issues(
    minLat: float = Query(...),
    minLng: float = Query(...),
    maxLat: float = Query(...),
    maxLng: float = Query(...),
    category: str | None = Query(None),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    return services.feed.viewport(minLat, minLng, maxLat, maxLng, issue_category_slug=category)
