"""Oversight dashboard endpoints (PRD §31.3, §10.4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import Services, get_services

router = APIRouter(prefix="/api/oversight", tags=["oversight"])


@router.get("/summary", summary="City-wide issue statistics for the oversight dashboard")
async def summary(services: Services = Depends(get_services)) -> dict:
    """
    Returns aggregate stats for the oversight dashboard:
    total issues, open/resolved/escalated counts, breakdown by authority and severity,
    average resolution time, and SLA compliance rate across all departments.
    """
    return services.oversight.summary()


@router.get("/hotspots", summary="Geographic hotspot clusters of civic issues")
async def hotspots(services: Services = Depends(get_services)) -> list[dict]:
    """
    Identifies geographic clusters where multiple related issues are concentrated.
    Each hotspot includes: centre coordinates, issue count, dominant issue type, and affected ward.
    Powers the heatmap overlay on the oversight map view.
    """
    return services.oversight.hotspots()


@router.get("/alerts", summary="AI-generated anomaly alerts and proactive warnings")
async def alerts(services: Services = Depends(get_services)) -> list[dict]:
    """
    **Proactive AI monitoring** — Gemini analyses patterns in the issue data and surfaces anomalies before they become crises:
    - Sudden spike in a particular issue type in one ward
    - Authority with unusually high SLA breach rate
    - Repeated issues at the same location (infrastructure failure pattern)

    Returns a list of alerts with severity, description, and recommended action.
    """
    return await services.oversight.anomaly_alerts()
