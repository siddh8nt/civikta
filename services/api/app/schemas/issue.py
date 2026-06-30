"""Canonical issue contracts — the public civic object (PRD §6, §8.5)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import EventType, IssueStatus, Severity


class IssueBase(BaseModel):
    title: str | None = None
    public_summary: str | None = None
    status: IssueStatus = IssueStatus.submitted

    latitude: float | None = None
    longitude: float | None = None

    local_body_type: str | None = None
    mcd_zone: str | None = None
    ward_no: int | None = None
    ward_name: str | None = None
    locality_name: str | None = None

    issue_category_slug: str | None = None
    issue_type_slug: str | None = None
    asset_type_slug: str | None = None

    severity: Severity = Severity.medium
    urgency_score: float = 1.0
    corroboration_count: int = 0
    total_report_count: int = 1

    primary_authority_slug: str | None = None
    secondary_authority_slug: str | None = None


class IssueSummary(IssueBase):
    """Card shape for feed / map / authority queue."""

    id: str
    created_at: datetime
    cover_media_url: str | None = None
    distance_m: float | None = None


class TimelineEvent(BaseModel):
    event_type: EventType
    actor_type: str
    created_at: datetime
    payload: dict = {}


class IssueDetail(IssueBase):
    id: str
    reporter_id: str | None = None
    created_at: datetime
    updated_at: datetime
    canonical_description: str | None = None
    routing_confidence: float | None = None
    routing_reason: dict = {}
    ai_summary: str | None = None
    ai_confidence: float | None = None
    last_corroborated_at: datetime | None = None
    cover_media_url: str | None = None
    media_urls: list[str] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)


class StatusUpdate(BaseModel):
    status: IssueStatus
    status_reason: str | None = None
    proof_media_urls: list[str] = Field(default_factory=list)
    # deadline — ISO-8601 string, stored as timeline event
    deadline_iso: str | None = None
    # in-progress update fields
    update_title: str | None = None
    update_description: str | None = None
    # base64 proof photo for resolved / in-progress updates
    proof_image_data: str | None = None
    # re-routing field — updates primary_authority_slug when transferring to another authority
    reroute_to_authority: str | None = None
