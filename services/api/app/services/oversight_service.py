"""Oversight service — accountability metrics + anomaly alerts.

All endpoints are now rule-based and cached — no LLM calls on page load.
The dashboard loads instantly; the Analytics Agent handles deep AI queries.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any

from app.llm.base import LLMClient
from app.repositories.base import Repository

_OPEN = ["submitted", "pending_verification", "assigned", "in_progress", "reopened"]
_CLOSED = ["resolved", "closed"]
_SLA_HOURS = {"critical": 24, "high": 72, "medium": 168, "low": 336}

_AUTHORITY_NAMES: dict[str, str] = {
    "mcd_sanitation":    "MCD Sanitation",
    "mcd_engineering":   "MCD Engineering",
    "mcd_horticulture":  "MCD Horticulture",
    "mcd_public_health": "MCD Public Health",
    "ndmc_sanitation":   "NDMC Sanitation",
    "ndmc_civil":        "NDMC Civil Works",
    "ndmc_horticulture": "NDMC Horticulture",
    "dcb_civic":         "Delhi Cantonment Board",
    "djb":               "Delhi Jal Board",
    "pwd":               "Public Works Department",
    "ifcd":              "Irrigation & Flood Control",
    "dda":               "Delhi Development Authority",
    "delhi_police":      "Delhi Police",
    "nhai":              "NHAI",
}


class OversightService:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm
        self._cache: dict[str, tuple[Any, datetime]] = {}

    def _cached(self, key: str, ttl_seconds: int, fn):
        """Simple in-process TTL cache. fn() is called on miss."""
        entry = self._cache.get(key)
        if entry:
            value, expires = entry
            if datetime.now(timezone.utc) < expires:
                return value
        value = fn()
        self._cache[key] = (value, datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds))
        return value

    def summary(self) -> dict:
        return self._cached("summary", 60, self._compute_summary)

    def _compute_summary(self) -> dict:
        issues = self.repo.list_issues()
        now = datetime.now(timezone.utc)

        open_count = unresolved_7d = reopened = sla_breached = 0
        total_corr = 0
        by_authority: dict[str, dict] = defaultdict(lambda: {"open": 0, "total": 0, "sla_breached": 0})
        by_severity: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)
        safety_open = 0

        for i in issues:
            total_corr += i.corroboration_count
            if i.status in _OPEN:
                open_count += 1
                auth = i.primary_authority_slug or "unrouted"
                by_authority[auth]["open"] += 1
                by_authority[auth]["total"] += 1
                by_severity[i.severity] += 1
                by_category[i.issue_category_slug or "unknown"] += 1
                if i.public_safety_flag or i.health_hazard_flag:
                    safety_open += 1
                hours_open = (now - i.created_at).total_seconds() / 3600
                if hours_open > _SLA_HOURS.get(i.severity, 168):
                    sla_breached += 1
                    by_authority[auth]["sla_breached"] += 1
                if (now - i.created_at).days > 7:
                    unresolved_7d += 1
            else:
                auth = i.primary_authority_slug or "unrouted"
                by_authority[auth]["total"] += 1
            if i.status == "reopened":
                reopened += 1

        resolved_count = sum(1 for i in issues if i.status in _CLOSED)
        false_closures = sum(1 for i in issues if i.false_closure_suspected)

        # Top authority table: sorted by open count
        auth_table = [
            {
                "slug": slug,
                "name": _AUTHORITY_NAMES.get(slug, slug),
                "open": d["open"],
                "total": d["total"],
                "sla_breached": d["sla_breached"],
                "sla_breach_rate_pct": round(d["sla_breached"] / d["open"] * 100, 1) if d["open"] else 0,
            }
            for slug, d in by_authority.items()
            if slug != "unrouted"
        ]
        auth_table.sort(key=lambda x: x["open"], reverse=True)

        top_corroborated = sorted(
            [i for i in issues if i.status in _OPEN],
            key=lambda x: x.corroboration_count,
            reverse=True,
        )[:5]

        return {
            "total_issues": len(issues),
            "open_issues": open_count,
            "resolved_issues": resolved_count,
            "unresolved_over_7d": unresolved_7d,
            "reopened_issues": reopened,
            "sla_breached_open": sla_breached,
            "sla_breach_rate_pct": round(sla_breached / open_count * 100, 1) if open_count else 0,
            "false_closures": false_closures,
            "safety_flagged_open": safety_open,
            "total_corroborations": total_corr,
            "open_by_severity": dict(by_severity),
            "open_by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "authority_table": auth_table,
            "most_corroborated": [
                {
                    "id": i.id,
                    "title": i.title,
                    "corroboration_count": i.corroboration_count,
                    "urgency_score": i.urgency_score,
                    "ward": i.ward_name,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", ""),
                    "severity": i.severity,
                    "days_open": (now - i.created_at).days,
                }
                for i in top_corroborated
            ],
        }

    def hotspots(self) -> list[dict]:
        return self._cached("hotspots", 120, self._compute_hotspots)

    def _compute_hotspots(self) -> list[dict]:
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
        """Rule-based anomaly detection — instant, no LLM calls on page load.

        Flags ward-category clusters with high corroboration density or stale
        unresolved critical issues. Headlines are generated from templates.
        """
        cached = self._cache.get("alerts")
        if cached:
            value, expires = cached
            if datetime.now(timezone.utc) < expires:
                return value

        result = self._compute_alerts()
        self._cache["alerts"] = (result, datetime.now(timezone.utc) + timedelta(seconds=300))
        return result

    def _compute_alerts(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        ward_cat: dict[tuple, list] = defaultdict(list)
        for i in self.repo.list_issues(statuses=_OPEN):
            ward_cat[(i.ward_no, i.ward_name, i.issue_category_slug)].append(i)

        alerts: list[dict] = []
        for (ward_no, ward_name, category), items in ward_cat.items():
            total_corr = sum(i.corroboration_count for i in items)
            oldest_days = max(((now - i.created_at).days for i in items), default=0)
            critical_count = sum(1 for i in items if i.severity == "critical")
            safety_count = sum(1 for i in items if i.public_safety_flag or i.health_hazard_flag)
            false_closure = sum(1 for i in items if i.false_closure_suspected)

            # Skip low-signal clusters
            if total_corr < 5 and oldest_days < 7 and critical_count == 0:
                continue

            # Rule-based severity
            if critical_count >= 2 or safety_count >= 3 or total_corr >= 15:
                severity = "critical"
            elif critical_count >= 1 or total_corr >= 8 or oldest_days >= 14:
                severity = "alert"
            else:
                severity = "watch"

            # Rule-based headline — instant, no LLM
            cat_label = (category or "civic").replace("_", " ")
            if false_closure:
                headline = (
                    f"{false_closure} {cat_label} issue(s) in {ward_name} suspected as false closures "
                    f"— {total_corr} citizens have corroborated these unresolved problems."
                )
            elif critical_count >= 1:
                headline = (
                    f"{critical_count} critical {cat_label} issue(s) in {ward_name} unresolved "
                    f"for up to {oldest_days} days with {total_corr} citizen corroborations."
                )
            elif oldest_days >= 14:
                headline = (
                    f"{len(items)} {cat_label} issues in {ward_name} unresolved for {oldest_days}+ days "
                    f"— {total_corr} citizens are waiting for action."
                )
            else:
                headline = (
                    f"Spike in {cat_label} complaints from {ward_name}: "
                    f"{len(items)} open issues, {total_corr} corroborations."
                )

            alerts.append({
                "ward_no": ward_no,
                "ward_name": ward_name,
                "category_slug": category,
                "severity": severity,
                "headline": headline,
                "metrics": {
                    "open_count": len(items),
                    "total_corroborations": total_corr,
                    "oldest_unresolved_days": oldest_days,
                    "critical_count": critical_count,
                    "safety_flagged": safety_count,
                    "false_closures": false_closure,
                },
            })

        order = {"critical": 0, "alert": 1, "watch": 2}
        alerts.sort(key=lambda a: (order.get(a["severity"], 3), -a["metrics"]["total_corroborations"]))
        return alerts[:8]  # cap at 8 alerts
