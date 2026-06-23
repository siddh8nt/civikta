"""Complaint pipeline contract.

Two phases mirror the citizen flow (PRD §21):
  analyze  -> AI classify + geo resolve + duplicate check (drives the CV screen)
  submit   -> finalize as a NEW issue or a CORROBORATION, per citizen's decision

Routing inside `submit` is ALWAYS deterministic, in every pipeline
implementation. The agent may drive `analyze`, never the final authority routing.
"""

from __future__ import annotations

from typing import Protocol

from app.models.issue_report import IssueReportRecord
from app.schemas.report import AnalyzeResult, SubmitDecision, SubmitResult


class ComplaintPipeline(Protocol):
    async def analyze(self, report: IssueReportRecord) -> AnalyzeResult: ...
    async def submit(self, report: IssueReportRecord, decision: SubmitDecision) -> SubmitResult: ...
