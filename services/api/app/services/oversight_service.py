"""Oversight service — accountability metrics + predictive anomaly alerts.

The anomaly alerts (PRD §10.4) are the proactive-AI feature: per-ward baseline vs
current-week rate, with a Gemini-written headline via the LLM seam.

NOTE: full oversight layer is intentionally thin for now — to be expanded after
the citizen app is built. See project memory: oversight & resolution layer gap.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from app.llm.base import LLMClient
from app.repositories.base import Repository

_OPEN = ["submitted", "pending_verification", "assigned", "in_progress", "reopened"]


class OversightService:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    def summary(self) -> dict:
        issues = self.repo.list_issues()
        now = datetime.now(timezone.utc)
        by_authority: dict[str, int] = defaultdict(int)
        open_count = unresolved_7d = reopened = 0
        for i in issues:
            if i.status in _OPEN:
                open_count += 1
                by_authority[i.primary_authority_slug or "unrouted"] += 1
                if (now - i.created_at).days > 7:
                    unresolved_7d += 1
            if i.status == "reopened":
                reopened += 1
        return {
            "total_issues": len(issues),
            "open_issues": open_count,
            "unresolved_over_7d": unresolved_7d,
            "reopened_issues": reopened,
            "open_by_authority": dict(by_authority),
            "most_corroborated": [
                {"id": i.id, "title": i.title, "corroboration_count": i.corroboration_count,
                 "urgency_score": i.urgency_score}
                for i in sorted(issues, key=lambda x: x.corroboration_count, reverse=True)[:5]
            ],
        }

    def hotspots(self) -> list[dict]:
        buckets: dict[tuple, list] = defaultdict(list)
        for i in self.repo.list_issues(statuses=_OPEN):
            buckets[(i.ward_no, i.ward_name, i.locality_name)].append(i)
        out = []
        for (ward_no, ward_name, locality), items in buckets.items():
            out.append({
                "ward_no": ward_no, "ward_name": ward_name, "locality_name": locality,
                "open_count": len(items),
                "total_corroborations": sum(i.corroboration_count for i in items),
                "max_urgency": max((i.urgency_score for i in items), default=0),
            })
        return sorted(out, key=lambda h: (h["open_count"], h["total_corroborations"]), reverse=True)

    async def anomaly_alerts(self) -> list[dict]:
        """Predictive panel (PRD §10.4). Flags wards/categories spiking vs baseline.

        With seed data there is no multi-week history, so this uses corroboration
        density + unresolved age as a proxy spike signal and asks the LLM to write
        the headline. Swap the proxy for real rolling-window counts once you have
        historical data.
        """
        now = datetime.now(timezone.utc)
        ward_cat: dict[tuple, list] = defaultdict(list)
        for i in self.repo.list_issues(statuses=_OPEN):
            ward_cat[(i.ward_no, i.ward_name, i.issue_category_slug)].append(i)

        alerts: list[dict] = []
        for (ward_no, ward_name, category), items in ward_cat.items():
            total_corr = sum(i.corroboration_count for i in items)
            oldest_days = max(((now - i.created_at).days for i in items), default=0)
            # proxy spike heuristic
            if total_corr < 5 and oldest_days < 7:
                continue
            severity = "critical" if total_corr >= 10 else "alert" if total_corr >= 5 else "watch"
            headline = await self.llm.summarize(
                f"Ward {ward_name} shows {len(items)} open {category} issues with "
                f"{total_corr} corroborations, oldest {oldest_days} days unresolved. "
                f"Write a one-line oversight alert headline."
            )
            alerts.append({
                "ward_no": ward_no, "ward_name": ward_name, "category_slug": category,
                "severity": severity, "headline": headline,
                "metrics": {"open_count": len(items), "total_corroborations": total_corr,
                            "oldest_unresolved_days": oldest_days},
            })
        order = {"critical": 0, "alert": 1, "watch": 2}
        return sorted(alerts, key=lambda a: order.get(a["severity"], 3))
