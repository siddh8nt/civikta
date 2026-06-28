"""Citizen report contracts — the raw input layer (PRD §6, §8.4)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.ai import ComplaintAnalysis
from app.schemas.duplicate import DuplicateResult
from app.schemas.geo import GeoResolution


class ReportDraftCreate(BaseModel):
    raw_title: str | None = None
    raw_description: str | None = None
    category_hint: str | None = None
    latitude: float
    longitude: float
    media_urls: list[str] = Field(default_factory=list)
    image_data: list[str] = Field(default_factory=list)  # base64 data-URLs from citizen camera
    audio_data: str | None = None                        # base64 data-URL of voice recording


class MediaAttach(BaseModel):
    media_type: str = "image"   # image / video / audio
    storage_url: str
    thumbnail_url: str | None = None


class AnalyzeResult(BaseModel):
    """Output of the analyze step: AI classification + geo + duplicate check."""

    report_id: str
    analysis: ComplaintAnalysis
    geo: GeoResolution
    duplicates: DuplicateResult


class SubmitDecision(BaseModel):
    """Citizen's choice on the Community Verification screen (PRD §8.4 Step 5a)."""

    # if corroborate=True, merges into target_issue_id; otherwise creates a new issue
    corroborate: bool = False
    target_issue_id: str | None = None
    still_unresolved: bool = False
    affected_too: bool = False


class CorroborateRequest(BaseModel):
    """Public issue actions: 'I'm affected too' / 'still unresolved' / add evidence."""

    still_unresolved: bool = False
    affected_too: bool = False
    media_urls: list[str] = Field(default_factory=list)
    note: str | None = None


class SubmitResult(BaseModel):
    """Outcome of finalizing a report (new issue or corroboration)."""

    outcome: str          # created / corroborated
    issue_id: str
    status: str
