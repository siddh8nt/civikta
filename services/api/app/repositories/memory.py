"""In-memory repository. Zero external dependencies — makes the whole API runnable
for local dev and demos. Not durable; restarts clear data (then re-seed)."""

from __future__ import annotations

from app.core.geoutil import haversine_m
from app.models.authority import AuthorityRecord
from app.models.issue import IssueEventRecord, IssueRecord
from app.models.issue_report import IssueMediaRecord, IssueReportRecord
from app.models.routing_rule import RoutingRuleRecord


class MemoryRepository:
    def __init__(self) -> None:
        self._issues: dict[str, IssueRecord] = {}
        self._reports: dict[str, IssueReportRecord] = {}
        self._media: dict[str, IssueMediaRecord] = {}
        self._events: list[IssueEventRecord] = []
        self._authorities: dict[str, AuthorityRecord] = {}
        self._routing_rules: list[RoutingRuleRecord] = []
        self._seeded = False

    # --- issues ---
    def add_issue(self, issue: IssueRecord) -> IssueRecord:
        self._issues[issue.id] = issue
        return issue

    def get_issue(self, issue_id: str) -> IssueRecord | None:
        return self._issues.get(issue_id)

    def update_issue(self, issue: IssueRecord) -> IssueRecord:
        self._issues[issue.id] = issue
        return issue

    def list_issues(self, *, statuses=None, primary_authority_slug=None,
                    ward_no=None, issue_type_slug=None) -> list[IssueRecord]:
        out = list(self._issues.values())
        if statuses:
            out = [i for i in out if i.status in statuses]
        if primary_authority_slug:
            out = [i for i in out if i.primary_authority_slug == primary_authority_slug]
        if ward_no is not None:
            out = [i for i in out if i.ward_no == ward_no]
        if issue_type_slug:
            out = [i for i in out if i.issue_type_slug == issue_type_slug]
        return sorted(out, key=lambda i: i.created_at, reverse=True)

    def issues_near(self, lat, lng, radius_m, *, statuses=None,
                    issue_type_slug=None) -> list[tuple[IssueRecord, float]]:
        results: list[tuple[IssueRecord, float]] = []
        for issue in self._issues.values():
            if issue.latitude is None or issue.longitude is None:
                continue
            if statuses and issue.status not in statuses:
                continue
            if issue_type_slug and issue.issue_type_slug != issue_type_slug:
                continue
            dist = haversine_m(lat, lng, issue.latitude, issue.longitude)
            if dist <= radius_m:
                results.append((issue, dist))
        return sorted(results, key=lambda t: t[1])

    def issues_in_viewport(self, min_lat, min_lng, max_lat, max_lng, *,
                           statuses=None, issue_category_slug=None) -> list[IssueRecord]:
        out = []
        for issue in self._issues.values():
            if issue.latitude is None or issue.longitude is None:
                continue
            if not (min_lat <= issue.latitude <= max_lat and min_lng <= issue.longitude <= max_lng):
                continue
            if statuses and issue.status not in statuses:
                continue
            if issue_category_slug and issue.issue_category_slug != issue_category_slug:
                continue
            out.append(issue)
        return out

    # --- reports ---
    def add_report(self, report: IssueReportRecord) -> IssueReportRecord:
        self._reports[report.id] = report
        return report

    def get_report(self, report_id: str) -> IssueReportRecord | None:
        return self._reports.get(report_id)

    def update_report(self, report: IssueReportRecord) -> IssueReportRecord:
        self._reports[report.id] = report
        return report

    def list_reports_by_user(self, user_id: str) -> list[IssueReportRecord]:
        out = [r for r in self._reports.values() if r.created_by == user_id]
        return sorted(out, key=lambda r: r.created_at, reverse=True)

    def list_reports_for_issue(self, issue_id: str) -> list[IssueReportRecord]:
        issue = self._issues.get(issue_id)
        original_report_id = issue.original_report_id if issue else None
        out = [
            r for r in self._reports.values()
            if r.merged_into_issue_id == issue_id or r.id == original_report_id
        ]
        return sorted(out, key=lambda r: r.created_at)

    # --- media ---
    def add_media(self, media: IssueMediaRecord) -> IssueMediaRecord:
        self._media[media.id] = media
        return media

    def list_media_for_report(self, report_id: str) -> list[IssueMediaRecord]:
        return [m for m in self._media.values() if m.report_id == report_id]

    def list_media_for_issue(self, issue_id: str) -> list[IssueMediaRecord]:
        report_ids = {r.id for r in self.list_reports_for_issue(issue_id)}
        return [m for m in self._media.values() if m.report_id in report_ids]

    # --- events ---
    def add_event(self, event: IssueEventRecord) -> IssueEventRecord:
        self._events.append(event)
        return event

    def list_events(self, issue_id: str) -> list[IssueEventRecord]:
        out = [e for e in self._events if e.issue_id == issue_id]
        return sorted(out, key=lambda e: e.created_at)

    # --- reference ---
    def list_authorities(self) -> list[AuthorityRecord]:
        return list(self._authorities.values())

    def get_authority(self, slug: str) -> AuthorityRecord | None:
        return self._authorities.get(slug)

    def list_routing_rules(self) -> list[RoutingRuleRecord]:
        return list(self._routing_rules)

    # --- seeding ---
    def seed_demo(self) -> None:
        if self._seeded:
            return
        from app.seeds.authorities import AUTHORITIES
        from app.seeds.demo_issues import build_demo_issues
        from app.seeds.routing_rules import ROUTING_RULES

        for a in AUTHORITIES:
            self._authorities[a.slug] = a
        self._routing_rules = list(ROUTING_RULES)

        for issue, report, media_list, events in build_demo_issues():
            self.add_issue(issue)
            self.add_report(report)
            for m in media_list:
                self.add_media(m)
            for e in events:
                self.add_event(e)

        self._seeded = True
