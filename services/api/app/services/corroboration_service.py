"""Corroboration service (PRD §26). Merges a citizen report into a canonical issue.

Never silent — the caller only invokes this after the citizen confirms on the
Community Verification screen, or via an explicit public issue action.
"""

from __future__ import annotations

from app.models.issue import IssueEventRecord, IssueRecord
from app.models.issue_report import IssueMediaRecord, IssueReportRecord
from app.repositories.base import Repository
from app.schemas.common import EventType
from app.schemas.report import CorroborateRequest
from app.services.urgency_score_service import UrgencyScoreService


class CorroborationService:
    def __init__(self, repo: Repository, urgency: UrgencyScoreService) -> None:
        self.repo = repo
        self.urgency = urgency

    def merge_report(
        self, issue_id: str, report: IssueReportRecord,
        *, still_unresolved: bool = False, affected_too: bool = False,
    ) -> IssueRecord | None:
        """Merge an already-created report (from the submit flow) into an issue."""
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return None

        report.report_role = "corroboration"
        report.merge_decision = "merged"
        report.merged_into_issue_id = issue_id
        report.duplicate_candidate_issue_id = issue_id
        report.still_unresolved_flag = still_unresolved
        report.affected_too_flag = affected_too
        self.repo.update_report(report)

        return self._recompute(issue, new_media=len(self.repo.list_media_for_report(report.id)),
                               still_unresolved=still_unresolved)

    def public_corroborate(
        self, issue_id: str, user_id: str, req: CorroborateRequest,
    ) -> IssueRecord | None:
        """Public issue-page action: 'affected too' / 'still unresolved' / add evidence."""
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return None

        report = IssueReportRecord(
            created_by=user_id,
            raw_description=req.note,
            latitude=issue.latitude,
            longitude=issue.longitude,
            issue_type_slug=issue.issue_type_slug,
            issue_category_slug=issue.issue_category_slug,
            report_role="corroboration",
            merge_decision="merged",
            merged_into_issue_id=issue_id,
            duplicate_candidate_issue_id=issue_id,
            still_unresolved_flag=req.still_unresolved,
            affected_too_flag=req.affected_too,
        )
        self.repo.add_report(report)
        for url in req.media_urls:
            self.repo.add_media(IssueMediaRecord(report_id=report.id, storage_url=url))

        return self._recompute(issue, new_media=len(req.media_urls),
                               still_unresolved=req.still_unresolved)

    def _recompute(self, issue: IssueRecord, *, new_media: int, still_unresolved: bool) -> IssueRecord:
        from datetime import datetime, timezone

        issue.corroboration_count += 1
        issue.total_report_count += 1
        issue.total_evidence_count += new_media
        issue.last_corroborated_at = datetime.now(timezone.utc)

        # count of "still unresolved" confirmations across linked reports
        su_count = sum(
            1 for r in self.repo.list_reports_for_issue(issue.id) if r.still_unresolved_flag
        )
        issue.urgency_score = self.urgency.compute(issue, still_unresolved_count=su_count)
        self.repo.update_issue(issue)

        self._event(issue.id, EventType.issue_corroborated, "citizen",
                    {"corroboration_count": issue.corroboration_count})
        if still_unresolved:
            self._event(issue.id, EventType.still_unresolved_confirmed, "citizen",
                        {"still_unresolved_count": su_count})
        self._event(issue.id, EventType.urgency_score_updated, "system",
                    {"urgency_score": issue.urgency_score})
        return issue

    def _event(self, issue_id: str, event_type: EventType, actor_type: str, payload: dict) -> None:
        self.repo.add_event(IssueEventRecord(
            issue_id=issue_id, event_type=event_type.value, actor_type=actor_type, payload=payload,
        ))
