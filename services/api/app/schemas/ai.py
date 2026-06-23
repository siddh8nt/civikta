"""AI triage contract (PRD §20.2). The LLM seam produces exactly this shape,
whether it's the offline stub or real Gemini."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import Severity


class ComplaintAnalysis(BaseModel):
    title: str
    summary: str
    issue_category: str          # category slug, e.g. water_sewer_drainage
    issue_type: str              # type slug, e.g. sewer_overflow
    asset_type: str | None = None
    severity: Severity = Severity.medium
    obstruction_flag: bool = False
    health_hazard_flag: bool = False
    public_safety_flag: bool = False
    road_class: str | None = None
    drain_type: str | None = None
    land_owner_hint: str | None = None
    confidence: float = Field(0.5, ge=0, le=1)
    needs_manual_review: bool = False


class ComplaintAnalysisInput(BaseModel):
    """What the LLM seam receives. Media is passed as URLs, not bytes."""

    text: str | None = None
    media_urls: list[str] = Field(default_factory=list)
    category_hint: str | None = None
    latitude: float | None = None
    longitude: float | None = None
