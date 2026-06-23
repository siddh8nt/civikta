"""Deterministic complaint pipeline (PRD §21). Calls services in a fixed order.

This is the default and the reference behavior. The agentic pipeline will reuse
the same `submit` logic (deterministic routing) and only replace `analyze`.
"""

from __future__ import annotations

from app.core.deps import Services
from app.models.issue_report import IssueReportRecord
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import EventType
from app.schemas.report import AnalyzeResult, SubmitDecision, SubmitResult
from app.schemas.routing import RoutingInput


class DeterministicPipeline:
    def __init__(self, services: Services) -> None:
        self.s = services

    async def analyze(self, report: IssueReportRecord) -> AnalyzeResult:
        media = self.s.repo.list_media_for_report(report.id)
        inp = ComplaintAnalysisInput(
            text=report.raw_description or report.raw_title,
            media_urls=[m.storage_url for m in media],
            latitude=report.latitude,
            longitude=report.longitude,
        )

        # 1. AI triage
        analysis = await self.s.ai_triage.analyze(inp)
        self.s.reports.apply_analysis(report, analysis)

        # 2. Geo resolve
        geo = self.s.geo.resolve(report.latitude, report.longitude)

        # 3. Duplicate detection
        duplicates = await self.s.duplicates.find_duplicates(
            analysis, report.latitude, report.longitude
        )
        if duplicates.best_candidate:
            cand_id = duplicates.best_candidate.issue_id
            report.duplicate_confidence = duplicates.best_candidate.score
            report.duplicate_candidate_issue_id = cand_id
            self.s.repo.update_report(report)
            # log against the candidate issue's timeline (no issue exists for the draft yet)
            self.s.issues._event(cand_id, EventType.duplicate_candidate_found, "system",
                                 {"report_id": report.id, "score": duplicates.best_candidate.score})
            self.s.issues._event(cand_id, EventType.community_verification_prompt_shown, "system",
                                 {"report_id": report.id})

        return AnalyzeResult(report_id=report.id, analysis=analysis, geo=geo, duplicates=duplicates)

    async def submit(self, report: IssueReportRecord, decision: SubmitDecision) -> SubmitResult:
        analysis = ComplaintAnalysis(**report.ai_raw) if report.ai_raw else (
            await self.s.ai_triage.analyze(ComplaintAnalysisInput(text=report.raw_description))
        )
        geo = self.s.geo.resolve(report.latitude, report.longitude)

        # Citizen confirmed corroboration on the Community Verification screen
        if decision.corroborate and decision.target_issue_id:
            issue = self.s.corroboration.merge_report(
                decision.target_issue_id, report,
                still_unresolved=decision.still_unresolved, affected_too=decision.affected_too,
            )
            if issue:
                return SubmitResult(outcome="corroborated", issue_id=issue.id, status=issue.status)

        # Otherwise: deterministic routing -> new canonical issue
        routing = self.s.routing.route(RoutingInput(
            local_body_type=geo.local_body_type,
            issue_type_slug=analysis.issue_type,
            asset_type_slug=analysis.asset_type,
            road_class=analysis.road_class,
            drain_type=analysis.drain_type,
            land_owner_hint=analysis.land_owner_hint,
        ))
        issue = await self.s.issues.create_from_report(report, analysis, geo, routing)
        return SubmitResult(outcome="created", issue_id=issue.id, status=issue.status)
