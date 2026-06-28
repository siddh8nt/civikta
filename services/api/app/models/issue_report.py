"""Persisted record shapes for individual citizen submissions + their media.

Mirrors the `issue_reports` / `issue_media` tables.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid4())


class IssueReportRecord(BaseModel):
    id: str = Field(default_factory=_uuid)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    created_by: str | None = None

    raw_title: str | None = None
    raw_description: str | None = None
    media_summary: str | None = None
    image_data: list[str] = Field(default_factory=list)  # compressed base64 images, in-memory only

    latitude: float | None = None
    longitude: float | None = None

    issue_category_slug: str | None = None
    issue_type_slug: str | None = None
    asset_type_slug: str | None = None

    ai_summary: str | None = None
    ai_confidence: float | None = None
    ai_raw: dict = Field(default_factory=dict)

    duplicate_confidence: float | None = None
    duplicate_candidate_issue_id: str | None = None

    report_role: str = "original"          # original / corroboration
    merge_decision: str | None = None      # pending / merged / forced_new / manual_review
    merged_into_issue_id: str | None = None

    still_unresolved_flag: bool = False
    affected_too_flag: bool = False

    source: str = "citizen_app"


class IssueMediaRecord(BaseModel):
    id: str = Field(default_factory=_uuid)
    report_id: str
    media_type: str = "image"
    storage_url: str
    thumbnail_url: str | None = None
    created_at: datetime = Field(default_factory=_now)
