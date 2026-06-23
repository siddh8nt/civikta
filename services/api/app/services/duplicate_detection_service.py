"""Duplicate / corroboration detection (PRD §25).

Spatial gate first (cheap), then weighted similarity scoring. The semantic
dimension uses embeddings from the LLM seam (stub or Vertex). Returns a
DuplicateResult the citizen flow uses to decide whether to show the Community
Verification prompt — never auto-merges.
"""

from __future__ import annotations

import math

from app.llm.base import LLMClient
from app.repositories.base import Repository
from app.schemas.ai import ComplaintAnalysis
from app.schemas.duplicate import DuplicateCandidate, DuplicateResult

# candidate retrieval radius by issue type (metres)
_RADIUS_POINT = 50.0
_RADIUS_LANE = 100.0
_RADIUS_AREA = 150.0
_LANE_TYPES = {"broken_footpath", "footpath_encroachment", "pothole_local_road",
               "clogged_local_drain", "road_obstruction"}
_AREA_TYPES = {"waterlogging"}

# scoring weights (sum = 1.0)
_W_SPATIAL = 0.35
_W_TYPE = 0.25
_W_SEMANTIC = 0.25
_W_ASSET = 0.10
_W_RECENCY = 0.05

# open-ish statuses a new report could corroborate
_OPEN_STATUSES = ["submitted", "pending_verification", "assigned", "in_progress", "reopened"]

_THRESHOLD_POSSIBLE = 0.50
_THRESHOLD_STRONG = 0.75


def _radius_for(issue_type: str | None) -> float:
    if issue_type in _AREA_TYPES:
        return _RADIUS_AREA
    if issue_type in _LANE_TYPES:
        return _RADIUS_LANE
    return _RADIUS_POINT


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(1.0, (dot / (na * nb) + 1) / 2))  # map [-1,1] -> [0,1]


class DuplicateDetectionService:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    async def find_duplicates(
        self, analysis: ComplaintAnalysis, lat: float, lng: float
    ) -> DuplicateResult:
        radius = _radius_for(analysis.issue_type)
        nearby = self.repo.issues_near(lat, lng, radius, statuses=_OPEN_STATUSES)
        if not nearby:
            return DuplicateResult(has_candidate=False, recommendation="none")

        new_embedding = await self.llm.embed(analysis.summary or analysis.title)

        candidates: list[DuplicateCandidate] = []
        for issue, dist in nearby:
            spatial = 1.0 - (dist / radius)
            type_match = 1.0 if issue.issue_type_slug == analysis.issue_type else 0.2
            asset_match = (
                1.0 if issue.asset_type_slug == analysis.asset_type
                else 0.5 if not issue.asset_type_slug and not analysis.asset_type
                else 0.3
            )

            # lazily embed the candidate summary if missing (stub demo data)
            if issue.summary_embedding is None and issue.public_summary:
                issue.summary_embedding = await self.llm.embed(issue.public_summary)
                self.repo.update_issue(issue)
            semantic = _cosine(new_embedding, issue.summary_embedding or [])

            recency = 1.0 if issue.last_corroborated_at else 0.5

            score = (
                _W_SPATIAL * spatial
                + _W_TYPE * type_match
                + _W_SEMANTIC * semantic
                + _W_ASSET * asset_match
                + _W_RECENCY * recency
            )
            candidates.append(DuplicateCandidate(
                issue_id=issue.id, title=issue.title, distance_m=round(dist, 1),
                issue_type_slug=issue.issue_type_slug, status=issue.status,
                corroboration_count=issue.corroboration_count, score=round(score, 3),
                score_breakdown={
                    "spatial": round(spatial, 3), "type": type_match,
                    "semantic": round(semantic, 3), "asset": asset_match, "recency": recency,
                },
            ))

        candidates.sort(key=lambda c: c.score, reverse=True)
        best = candidates[0]
        recommendation = (
            "strong" if best.score >= _THRESHOLD_STRONG
            else "possible" if best.score >= _THRESHOLD_POSSIBLE
            else "none"
        )
        return DuplicateResult(
            has_candidate=recommendation != "none",
            best_candidate=best if recommendation != "none" else None,
            candidates=candidates[:5],
            recommendation=recommendation,
        )
