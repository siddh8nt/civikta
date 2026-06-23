"""Oversight dashboard endpoints (PRD §31.3, §10.4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import Services, get_services

router = APIRouter(prefix="/api/oversight", tags=["oversight"])


@router.get("/summary")
async def summary(services: Services = Depends(get_services)) -> dict:
    return services.oversight.summary()


@router.get("/hotspots")
async def hotspots(services: Services = Depends(get_services)) -> list[dict]:
    return services.oversight.hotspots()


@router.get("/alerts")
async def alerts(services: Services = Depends(get_services)) -> list[dict]:
    """Predictive anomaly alerts (proactive AI, PRD §10.4)."""
    return await services.oversight.anomaly_alerts()
