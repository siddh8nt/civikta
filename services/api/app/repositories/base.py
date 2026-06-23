"""Repository contract. One cohesive interface for all persistence.

Any backend (in-memory, Supabase, ...) implements this. Services depend only on
this protocol, never on a concrete store.
"""

from __future__ import annotations

from typing import Protocol

from app.models.authority import AuthorityRecord
from app.models.issue import IssueEventRecord, IssueRecord
from app.models.issue_report import IssueMediaRecord, IssueReportRecord
from app.models.routing_rule import RoutingRuleRecord


class Repository(Protocol):
    # --- issues ---
    def add_issue(self, issue: IssueRecord) -> IssueRecord: ...
    def get_issue(self, issue_id: str) -> IssueRecord | None: ...
    def update_issue(self, issue: IssueRecord) -> IssueRecord: ...
    def list_issues(
        self,
        *,
        statuses: list[str] | None = None,
        primary_authority_slug: str | None = None,
        ward_no: int | None = None,
        issue_type_slug: str | None = None,
    ) -> list[IssueRecord]: ...
    def issues_near(
        self,
        lat: float,
        lng: float,
        radius_m: float,
        *,
        statuses: list[str] | None = None,
        issue_type_slug: str | None = None,
    ) -> list[tuple[IssueRecord, float]]: ...
    def issues_in_viewport(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        *,
        statuses: list[str] | None = None,
        issue_category_slug: str | None = None,
    ) -> list[IssueRecord]: ...

    # --- reports ---
    def add_report(self, report: IssueReportRecord) -> IssueReportRecord: ...
    def get_report(self, report_id: str) -> IssueReportRecord | None: ...
    def update_report(self, report: IssueReportRecord) -> IssueReportRecord: ...
    def list_reports_by_user(self, user_id: str) -> list[IssueReportRecord]: ...
    def list_reports_for_issue(self, issue_id: str) -> list[IssueReportRecord]: ...

    # --- media ---
    def add_media(self, media: IssueMediaRecord) -> IssueMediaRecord: ...
    def list_media_for_report(self, report_id: str) -> list[IssueMediaRecord]: ...
    def list_media_for_issue(self, issue_id: str) -> list[IssueMediaRecord]: ...

    # --- events ---
    def add_event(self, event: IssueEventRecord) -> IssueEventRecord: ...
    def list_events(self, issue_id: str) -> list[IssueEventRecord]: ...

    # --- reference ---
    def list_authorities(self) -> list[AuthorityRecord]: ...
    def get_authority(self, slug: str) -> AuthorityRecord | None: ...
    def list_routing_rules(self) -> list[RoutingRuleRecord]: ...
