"""Public feed + map service (PRD §29). Canonical issues only — corroborating
reports never appear as separate feed entries; they boost the canonical issue."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.issue import IssueRecord
from app.repositories.base import Repository
from app.schemas.issue import IssueSummary
from app.services.issue_service import IssueService

_SEVERITY = {"low": 1.0, "medium": 2.0, "high": 4.0, "critical": 6.0}


def _recency(issue: IssueRecord) -> float:
    age_days = (datetime.now(timezone.utc) - issue.created_at).total_seconds() / 86400
    return max(0.0, 1.0 - age_days / 14)  # decays over ~2 weeks


def _feed_score(issue: IssueRecord, distance_m: float | None, radius_m: float) -> float:
    proximity = (1.0 - min(distance_m, radius_m) / radius_m) if distance_m is not None else 0.5
    severity = _SEVERITY.get(issue.severity, 2.0) / 6.0
    corroboration = min(issue.corroboration_count, 10) / 10.0
    penalty = 2.0 if issue.status == "resolved" else 0.0
    return 3.0 * proximity + 1.0 * severity + 2.0 * corroboration + 1.0 * _recency(issue) - penalty


class FeedService:
    def __init__(self, repo: Repository, issues: IssueService) -> None:
        self.repo = repo
        self.issues = issues

    def nearby(self, lat: float, lng: float, radius_m: float = 3000.0,
               issue_type_slug: str | None = None, limit: int = 50) -> list[IssueSummary]:
        results = self.repo.issues_near(lat, lng, radius_m, issue_type_slug=issue_type_slug)
        ranked = sorted(results, key=lambda t: _feed_score(t[0], t[1], radius_m), reverse=True)
        return [self.issues.to_summary(issue, dist) for issue, dist in ranked[:limit]]

    def viewport(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float,
                 issue_category_slug: str | None = None) -> list[IssueSummary]:
        issues = self.repo.issues_in_viewport(
            min_lat, min_lng, max_lat, max_lng, issue_category_slug=issue_category_slug
        )
        return [self.issues.to_summary(i) for i in issues]
