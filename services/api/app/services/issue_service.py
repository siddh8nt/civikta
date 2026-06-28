"""Issue service — the canonical public object (PRD §6, §8.5).

Creates issues from an original report + analysis + geo + routing, and assembles
the issue detail (media + timeline). Routing is passed in already-computed
(deterministic); this service never decides the authority itself.
"""

from __future__ import annotations

from app.llm.base import LLMClient
from app.models.issue import IssueEventRecord, IssueRecord
from app.models.issue_report import IssueReportRecord
from app.repositories.base import Repository
from app.schemas.ai import ComplaintAnalysis
from app.schemas.common import EventType
from app.schemas.geo import GeoResolution
from app.seeds.issue_types import subcategory_for_type
from app.schemas.issue import IssueDetail, IssueSummary, TimelineEvent
from app.schemas.routing import RoutingResult
from app.services.urgency_score_service import UrgencyScoreService


class IssueService:
    def __init__(self, repo: Repository, urgency: UrgencyScoreService, llm: LLMClient) -> None:
        self.repo = repo
        self.urgency = urgency
        self.llm = llm

    async def create_from_report(
        self,
        report: IssueReportRecord,
        analysis: ComplaintAnalysis,
        geo: GeoResolution,
        routing: RoutingResult,
    ) -> IssueRecord:
        issue = IssueRecord(
            original_report_id=report.id,
            created_by=report.created_by,
            title=analysis.title,
            canonical_description=report.raw_description,
            public_summary=analysis.summary,
            status="submitted",
            latitude=report.latitude,
            longitude=report.longitude,
            local_body_type=geo.local_body_type,
            revenue_district=geo.revenue_district,
            mcd_zone=geo.mcd_zone,
            ward_no=geo.ward_no,
            ward_name=geo.ward_name,
            locality_name=geo.locality_name,
            landmark=geo.landmark,
            issue_category_slug=analysis.issue_category,
            issue_subcategory_slug=subcategory_for_type(analysis.issue_type),
            issue_type_slug=analysis.issue_type,
            asset_type_slug=analysis.asset_type,
            severity=analysis.severity.value,
            obstruction_flag=analysis.obstruction_flag,
            health_hazard_flag=analysis.health_hazard_flag,
            public_safety_flag=analysis.public_safety_flag,
            road_class=analysis.road_class,
            drain_type=analysis.drain_type,
            land_owner_hint=analysis.land_owner_hint,
            ai_summary=analysis.ai_summary or analysis.summary,
            ai_confidence=analysis.confidence,
            primary_authority_slug=routing.primary_authority_slug,
            secondary_authority_slug=routing.secondary_authority_slug,
            routing_confidence=routing.confidence,
            routing_reason=routing.reason,
        )
        issue.summary_embedding = await self.llm.embed(issue.public_summary or issue.title or "")
        issue.urgency_score = self.urgency.compute(issue)

        # Denormalize cover image so feed never needs a media join
        first_media = self.repo.list_media_for_report(report.id)
        if first_media:
            issue.cover_media_url = first_media[0].storage_url

        # Insert issue BEFORE updating the report — issue_reports.merged_into_issue_id has a FK → issues.id
        self.repo.add_issue(issue)

        # Now safe to link the original report to its canonical issue
        report.merged_into_issue_id = issue.id
        report.report_role = "original"
        report.merge_decision = "forced_new"
        self.repo.update_report(report)
        self._event(issue.id, EventType.created, "citizen")
        self._event(issue.id, EventType.classified, "system",
                    {"issue_type": analysis.issue_type, "confidence": analysis.confidence})
        if routing.primary_authority_slug:
            issue.status = "assigned"
            self.repo.update_issue(issue)
            self._event(issue.id, EventType.assigned, "system",
                        {"authority": routing.primary_authority_slug})
        return issue

    def get(self, issue_id: str) -> IssueRecord | None:
        return self.repo.get_issue(issue_id)

    def get_detail(self, issue_id: str) -> IssueDetail | None:
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return None
        media = self.repo.list_media_for_issue(issue_id)
        events = self.repo.list_events(issue_id)
        return IssueDetail(
            **_issue_base_fields(issue),
            id=issue.id,
            reporter_id=issue.created_by,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            canonical_description=issue.canonical_description,
            routing_confidence=issue.routing_confidence,
            routing_reason=issue.routing_reason,
            ai_summary=issue.ai_summary,
            ai_confidence=issue.ai_confidence,
            last_corroborated_at=issue.last_corroborated_at,
            media_urls=[m.storage_url for m in media] or ([issue.cover_media_url] if issue.cover_media_url else []),
            timeline=[
                TimelineEvent(event_type=e.event_type, actor_type=e.actor_type,
                              created_at=e.created_at, payload=e.payload)
                for e in events
            ],
        )

    def to_summary(self, issue: IssueRecord, distance_m: float | None = None) -> IssueSummary:
        return IssueSummary(
            **_issue_base_fields(issue),
            id=issue.id,
            created_at=issue.created_at,
            cover_media_url=issue.cover_media_url,
            distance_m=round(distance_m, 1) if distance_m is not None else None,
        )

    def request_escalation(self, issue_id: str, citizen_uid: str) -> bool:
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return False
        self._event(issue_id, EventType.escalated_to_oversight, "citizen",
                    {"requested_by": citizen_uid,
                     "reason": "Citizen flagged authority non-response — Vertex AI escalation agent notified"})
        return True

    def _event(self, issue_id: str, event_type: EventType, actor_type: str,
               payload: dict | None = None) -> None:
        self.repo.add_event(IssueEventRecord(
            issue_id=issue_id, event_type=event_type.value,
            actor_type=actor_type, payload=payload or {},
        ))


def _issue_base_fields(issue: IssueRecord) -> dict:
    return dict(
        title=issue.title,
        public_summary=issue.public_summary,
        status=issue.status,
        latitude=issue.latitude,
        longitude=issue.longitude,
        local_body_type=issue.local_body_type,
        mcd_zone=issue.mcd_zone,
        ward_no=issue.ward_no,
        ward_name=issue.ward_name,
        locality_name=issue.locality_name,
        issue_category_slug=issue.issue_category_slug,
        issue_type_slug=issue.issue_type_slug,
        asset_type_slug=issue.asset_type_slug,
        severity=issue.severity,
        urgency_score=issue.urgency_score,
        corroboration_count=issue.corroboration_count,
        total_report_count=issue.total_report_count,
        primary_authority_slug=issue.primary_authority_slug,
        secondary_authority_slug=issue.secondary_authority_slug,
    )
