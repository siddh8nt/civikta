"""AI triage contract (PRD §20.2). The LLM seam produces exactly this shape,
whether it's the offline stub or real Gemini."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import Severity


class ComplaintAnalysis(BaseModel):
    title: str
    summary: str
    ai_summary: str | None = None        # internal triage summary for authority dashboard
    issue_category: str                  # category slug, e.g. water_sewer_drainage
    issue_type: str                      # type slug, e.g. sewer_overflow
    asset_type: str | None = None
    severity: Severity = Severity.medium
    obstruction_flag: bool = False
    health_hazard_flag: bool = False
    public_safety_flag: bool = False
    road_class: str | None = None
    drain_type: str | None = None
    land_owner_hint: str | None = None
    # AI-derived routing (Gemini encodes all routing rules in its prompt)
    primary_authority_slug: str | None = None
    secondary_authority_slug: str | None = None
    routing_confidence: float | None = None
    routing_reason: dict | None = None
    confidence: float = Field(0.5, ge=0, le=1)
    needs_manual_review: bool = False


class ComplaintAnalysisInput(BaseModel):
    """What the LLM seam receives."""

    text: str | None = None
    media_urls: list[str] = Field(default_factory=list)   # image / video storage URLs
    audio_urls: list[str] = Field(default_factory=list)   # raw audio storage URLs (Supabase)
    image_data: list[str] = Field(default_factory=list)   # base64 data-URLs from citizen camera
    category_hint: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    local_body_type: str | None = None  # MCD | NDMC | DCB — passed from geo-resolution
