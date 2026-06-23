"""Duplicate detection contract (PRD §25). Spatial gate first, then weighted scoring."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DuplicateCandidate(BaseModel):
    issue_id: str
    title: str | None = None
    distance_m: float
    issue_type_slug: str | None = None
    status: str | None = None
    corroboration_count: int = 0
    score: float = Field(0.0, ge=0, le=1)
    score_breakdown: dict = {}


class DuplicateResult(BaseModel):
    """Returned to the citizen flow to decide whether to show the CV prompt."""

    has_candidate: bool = False
    best_candidate: DuplicateCandidate | None = None
    candidates: list[DuplicateCandidate] = Field(default_factory=list)
    # 'none' < threshold_medium <= 'possible' < threshold_high <= 'strong'
    recommendation: str = "none"  # none / possible / strong
