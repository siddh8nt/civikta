"""Urgency scoring engine (PRD §27). Pure, explainable, recomputed on changes."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.issue import IssueRecord

_SEVERITY_WEIGHT = {"low": 1.0, "medium": 2.0, "high": 4.0, "critical": 6.0}


def _corroboration_weight(count: int) -> float:
    # first 5 @ +0.5, next 10 @ +0.25, further diminishing @ +0.1
    w = 0.0
    w += 0.5 * min(count, 5)
    w += 0.25 * min(max(count - 5, 0), 10)
    w += 0.1 * max(count - 15, 0)
    return w


def _duration_weight(created_at: datetime) -> float:
    age_days = (datetime.now(timezone.utc) - created_at).total_seconds() / 86400
    if age_days > 7:
        return 2.0
    if age_days > 3:
        return 1.0
    return 0.0


class UrgencyScoreService:
    def compute(self, issue: IssueRecord, *, still_unresolved_count: int = 0) -> float:
        score = 1.0  # base
        score += _SEVERITY_WEIGHT.get(issue.severity, 2.0)
        score += _corroboration_weight(issue.corroboration_count)
        score += _duration_weight(issue.created_at)
        if issue.public_safety_flag:
            score += 2.0
        if issue.health_hazard_flag:
            score += 2.0
        score += 0.75 * still_unresolved_count  # recency-growth signal
        return round(score, 2)

    def breakdown(self, issue: IssueRecord, *, still_unresolved_count: int = 0) -> dict:
        return {
            "base": 1.0,
            "severity": _SEVERITY_WEIGHT.get(issue.severity, 2.0),
            "corroboration": round(_corroboration_weight(issue.corroboration_count), 2),
            "duration": _duration_weight(issue.created_at),
            "public_safety": 2.0 if issue.public_safety_flag else 0.0,
            "health_hazard": 2.0 if issue.health_hazard_flag else 0.0,
            "still_unresolved": round(0.75 * still_unresolved_count, 2),
            "total": self.compute(issue, still_unresolved_count=still_unresolved_count),
        }
