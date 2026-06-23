"""Health + config introspection (handy for verifying which seams are active)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/config")
async def config(settings: Settings = Depends(get_settings)) -> dict:
    """Shows the active seam selection — confirms stub vs real wiring at a glance."""
    return {
        "pipeline": settings.civikta_pipeline.value,
        "llm": settings.civikta_llm.value,
        "repository": settings.civikta_repo.value,
        "auth": settings.civikta_auth.value,
    }
