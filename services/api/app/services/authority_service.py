"""Authority service — operator queue + status workflow (PRD §9, §28)."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

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
              ward_no: int | None = None, severity: str | None = None,
              sort: str = "urgency") -> list[IssueSummary]:
        items = self.repo.list_issues(
            statuses=[status] if status else None,
            primary_authority_slug=authority_slug,
            ward_no=ward_no,
        )
        if severity:
            items = [i for i in items if i.severity == severity]
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
        
        # Handle re-routing: update primary_authority_slug when transferring to another authority
        if update.reroute_to_authority:
            issue.primary_authority_slug = update.reroute_to_authority
        
        self.repo.update_issue(issue)

        # ── Primary status event ───────────────────────────────────────────────
        event_type = {
            "verified":    EventType.verified,
            "resolved":    EventType.resolved,
            "reopened":    EventType.reopened,
            "in_progress": EventType.authority_acknowledged,
        }.get(update.status.value, EventType.assigned)

        status_payload: dict = {
            "status": update.status.value,
            "reason": update.status_reason,
            "proof": update.proof_media_urls,
        }

        # Attach proof image to resolved event payload
        if update.proof_image_data:
            status_payload["proof_image_data"] = update.proof_image_data

        # For in_progress: attach update title/description
        if update.status.value == "in_progress":
            if update.update_title:
                status_payload["update_title"] = update.update_title
            if update.update_description:
                status_payload["update_description"] = update.update_description
            if update.proof_image_data:
                status_payload["update_image_data"] = update.proof_image_data

        self.repo.add_event(IssueEventRecord(
            issue_id=issue_id, actor_type="authority", actor_id=actor_id,
            event_type=event_type.value,
            payload=status_payload,
        ))

        # ── Reroute event (when transferring to another authority) ─────────────
        if update.reroute_to_authority:
            self.repo.add_event(IssueEventRecord(
                issue_id=issue_id, actor_type="authority", actor_id=actor_id,
                event_type=EventType.rerouted.value,
                payload={
                    "to": update.reroute_to_authority,
                    "reason": update.status_reason,
                },
            ))

        # ── In-progress update event (separate richer event) ───────────────────
        if update.status.value == "in_progress" and update.update_title:
            self.repo.add_event(IssueEventRecord(
                issue_id=issue_id, actor_type="authority", actor_id=actor_id,
                event_type=EventType.in_progress_update.value,
                payload={
                    "title": update.update_title,
                    "description": update.update_description,
                    "image_data": update.proof_image_data,
                },
            ))

        # ── Deadline event ─────────────────────────────────────────────────────
        if update.deadline_iso:
            self.repo.add_event(IssueEventRecord(
                issue_id=issue_id, actor_type="authority", actor_id=actor_id,
                event_type=EventType.deadline_set.value,
                payload={"deadline": update.deadline_iso, "set_at": datetime.now(timezone.utc).isoformat()},
            ))

        return self.issues.get_detail(issue_id)

    def get_escalations(self) -> list[IssueSummary]:
        """Issues that need oversight escalation:
        - Still 'submitted' (no authority action) for >1h, OR
        - 'resolved' but still_unresolved corroboration count ≥ 100.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        all_issues = self.repo.list_issues()

        escalated = []
        for issue in all_issues:
            # Untouched submitted issues past 1h
            if issue.status == "submitted" and issue.created_at < cutoff:
                escalated.append(issue)
                continue
            # Resolved issues with heavy "still unresolved" pushback
            if issue.status == "resolved" and issue.corroboration_count >= 100:
                escalated.append(issue)

        escalated.sort(key=lambda i: i.urgency_score, reverse=True)
        return [self.issues.to_summary(i) for i in escalated]
