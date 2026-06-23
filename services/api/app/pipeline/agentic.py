"""Agentic complaint pipeline — FUTURE implementation (PRD §20, §21).

This is where the multi-step ADK/Gemini agent loop lives. The plan:

  1. Build the tool list:  tools = build_tools(self.s)  (already implemented)
  2. Register each tool's `to_function_schema()` with a Gemini model via ADK.
  3. Run the agent loop for `analyze`: the model receives the complaint + media,
     decides which tools to call (analyze_complaint, resolve_delhi_geography,
     duplicate_issue_search, embed_and_score_similarity), inspects results, and
     resolves ambiguity before returning a final ComplaintAnalysis + geo +
     duplicate result.
  4. `submit` reuses the deterministic logic verbatim — routing MUST stay
     deterministic regardless of pipeline.

Until implemented, `analyze` raises so the misconfiguration is obvious; the
default pipeline stays deterministic. Flip CIVIKTA_PIPELINE=agentic only after
filling this in.
"""

from __future__ import annotations

from app.agents.tools import build_tools
from app.core.deps import Services
from app.models.issue_report import IssueReportRecord
from app.pipeline.deterministic import DeterministicPipeline
from app.schemas.report import AnalyzeResult, SubmitDecision, SubmitResult


class AgenticPipeline:
    def __init__(self, services: Services) -> None:
        self.s = services
        self.tools = build_tools(services)              # agent-ready, already tested
        self._deterministic = DeterministicPipeline(services)

    async def analyze(self, report: IssueReportRecord) -> AnalyzeResult:
        # TODO(agent): run the ADK/Gemini tool-calling loop over self.tools here.
        raise NotImplementedError(
            "AgenticPipeline.analyze is not wired yet. Implement the ADK loop, or set "
            "CIVIKTA_PIPELINE=deterministic. Tools are ready in app/agents/tools.py."
        )

    async def submit(self, report: IssueReportRecord, decision: SubmitDecision) -> SubmitResult:
        # routing stays deterministic in every pipeline
        return await self._deterministic.submit(report, decision)
