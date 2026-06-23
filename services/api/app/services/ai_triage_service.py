"""AI triage service — thin wrapper over the LLM seam (PRD §20).

Keeps the rest of the system independent of which model produces the analysis.
"""

from __future__ import annotations

from app.llm.base import LLMClient
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput


class AITriageService:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def analyze(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
        return await self.llm.analyze_complaint(inp)
