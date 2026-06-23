"""Authority service — operator queue + status workflow (PRD §9, §28).

NOTE: the deeper resolution workflow (escalation, reroute, cross-authority
handoff, SLA) is intentionally thin for now — to be designed after the citizen
app is built. See project memory: oversight & resolution layer gap.
"""

from __future__ import annotations

from app.models.issue import IssueEventRecord
from app.repositories.base import Repository
from app.schemas.common import EventType
from app.schemas.issue import IssueDetail, IssueSummary, StatusUpdate
from app.services.issue_service import IssueService

_SORTS = {
    "urgency": lambda i: i.urgency_score,
    "corroboration": lambda i: i.corroboration_count,
    "recent": lambda i: i.created_at.timestamp(),
}


class AuthorityService:
    def __init__(self, repo: Repository, issues: IssueService) -> None:
        self.repo = repo
        self.issues = issues

    def queue(self, authority_slug: str | None = None, *, status: str | None = None,
              ward_no: int | None = None, sort: str = "urgency") -> list[IssueSummary]:
        items = self.repo.list_issues(
            statuses=[status] if status else None,
            primary_authority_slug=authority_slug,
            ward_no=ward_no,
        )
        key = _SORTS.get(sort, _SORTS["urgency"])
        items.sort(key=key, reverse=True)
        return [self.issues.to_summary(i) for i in items]

    def get_detail(self, issue_id: str) -> IssueDetail | None:
        return self.issues.get_detail(issue_id)

    def update_status(self, issue_id: str, update: StatusUpdate,
                      actor_id: str | None = None) -> IssueDetail | None:
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return None
        issue.status = update.status.value
        issue.status_reason = update.status_reason
        self.repo.update_issue(issue)

        event_type = {
            "verified": EventType.verified,
            "resolved": EventType.resolved,
            "reopened": EventType.reopened,
        }.get(update.status.value, EventType.assigned)
        self.repo.add_event(IssueEventRecord(
            issue_id=issue_id, actor_type="authority", actor_id=actor_id,
            event_type=event_type.value,
            payload={"status": update.status.value, "reason": update.status_reason,
                     "proof": update.proof_media_urls},
        ))
        return self.issues.get_detail(issue_id)
