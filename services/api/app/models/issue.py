"""Persisted record shapes for the canonical issue + its timeline.

These mirror the `issues` / `issue_events` tables in infra/sql/schema.sql.
Repositories read/write these; services operate on them.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid4())


class IssueRecord(BaseModel):
    id: str = Field(default_factory=_uuid)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    original_report_id: str | None = None
    created_by: str | None = None

    title: str | None = None
    canonical_description: str | None = None
    public_summary: str | None = None

    status: str = "submitted"
    status_reason: str | None = None

    latitude: float | None = None
    longitude: float | None = None

    local_body_type: str | None = None
    revenue_district: str | None = None
    tehsil_subdivision: str | None = None
    mcd_zone: str | None = None
    ward_no: int | None = None
    ward_name: str | None = None
    locality_name: str | None = None
    landmark: str | None = None

    issue_category_slug: str | None = None
    issue_subcategory_slug: str | None = None    # taxonomy L2
    issue_type_slug: str | None = None
    asset_type_slug: str | None = None

    severity: str = "medium"
    urgency_score: float = 1.0
    corroboration_count: int = 0
    total_report_count: int = 1
    total_evidence_count: int = 0
    last_corroborated_at: datetime | None = None

    obstruction_flag: bool = False
    health_hazard_flag: bool = False
    public_safety_flag: bool = False
    impact_tags: list[str] = Field(default_factory=list)
    persistence_type: str = "new"               # new | recurring | chronic
    false_closure_suspected: bool = False

    road_class: str | None = None
    drain_type: str | None = None
    land_owner_hint: str | None = None

    ai_summary: str | None = None
    ai_confidence: float | None = None
    summary_embedding: list[float] | None = None

    primary_authority_slug: str | None = None
    secondary_authority_slug: str | None = None
    routing_confidence: float | None = None
    routing_reason: dict = Field(default_factory=dict)

    cover_media_url: str | None = None


class IssueEventRecord(BaseModel):
    id: str = Field(default_factory=_uuid)
    issue_id: str
    actor_type: str = "system"
    actor_id: str | None = None
    event_type: str = "created"
    payload: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
