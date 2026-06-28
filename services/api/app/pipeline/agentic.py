"""Agentic complaint pipeline (PRD §20, §21).

This pipeline is opt-in via CIVIKTA_PIPELINE=agentic. It wires the existing
agent-ready tools into the analyze step while preserving the deterministic
submit path, because routing must remain rule-based.

If the tool path fails for any reason, analyze falls back to the deterministic
pipeline so enabling this seam does not break report intake.
"""

from __future__ import annotations

import logging

from app.agents.tools import build_tools
from app.core.deps import Services
from app.models.issue_report import IssueReportRecord
from app.pipeline.deterministic import DeterministicPipeline
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import EventType
from app.schemas.report import AnalyzeResult, SubmitDecision, SubmitResult

log = logging.getLogger(__name__)


class AgenticPipeline:
    def __init__(self, services: Services) -> None:
        self.s = services
        self.tools = build_tools(services)
        self._deterministic = DeterministicPipeline(services)

    async def analyze(self, report: IssueReportRecord) -> AnalyzeResult:
        """Analyze a draft report through the agent tool surface.

        The current implementation uses a conservative fixed tool plan:
        resolve geography -> classify complaint -> search duplicates. That keeps
        the behavior close to the reference pipeline while exercising the same
        tool contracts a future model-directed loop can call dynamically.
        """
        try:
            return await self._tool_planned_analyze(report)
        except Exception as exc:
            log.exception("AgenticPipeline analyze failed; falling back to deterministic: %s", exc)
            return await self._deterministic.analyze(report)

    async def _tool_planned_analyze(self, report: IssueReportRecord) -> AnalyzeResult:
        media = self.s.repo.list_media_for_report(report.id)
        audio_media = [m for m in media if m.media_type == "audio"]
        image_media = [m for m in media if m.media_type != "audio"]

        geo = await self.tools["resolve_delhi_geography"]({
            "latitude": report.latitude,
            "longitude": report.longitude,
        })

        inp = ComplaintAnalysisInput(
            text=report.raw_description or report.raw_title,
            media_urls=[m.storage_url for m in image_media],
            audio_urls=[m.storage_url for m in audio_media],
            image_data=report.image_data,
            latitude=report.latitude,
            longitude=report.longitude,
            local_body_type=geo.local_body_type,
        )

        analysis = await self.tools["analyze_complaint"](inp)
        if not isinstance(analysis, ComplaintAnalysis):
            analysis = ComplaintAnalysis.model_validate(analysis)
        self.s.reports.apply_analysis(report, analysis)

        duplicates = await self.s.duplicates.find_duplicates(
            analysis, report.latitude, report.longitude
        )
        if duplicates.best_candidate:
            cand_id = duplicates.best_candidate.issue_id
            report.duplicate_confidence = duplicates.best_candidate.score
            report.duplicate_candidate_issue_id = cand_id
            self.s.repo.update_report(report)
            self.s.issues._event(
                cand_id,
                EventType.duplicate_candidate_found,
                "system",
                {"report_id": report.id, "score": duplicates.best_candidate.score},
            )
            self.s.issues._event(
                cand_id,
                EventType.community_verification_prompt_shown,
                "system",
                {"report_id": report.id},
            )

        return AnalyzeResult(
            report_id=report.id,
            analysis=analysis,
            geo=geo,
            duplicates=duplicates,
        )

    async def submit(self, report: IssueReportRecord, decision: SubmitDecision) -> SubmitResult:
        # Routing stays deterministic in every pipeline.
        return await self._deterministic.submit(report, decision)