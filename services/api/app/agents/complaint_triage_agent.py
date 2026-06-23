"""Complaint triage agent — FUTURE (PRD §20).

The ADK/Gemini agent that powers AgenticPipeline.analyze. Sketch of the intended
shape so the wiring is obvious when google-adk + a Gemini key are available.

The tools (app/agents/tools.py) and the structured output contract
(app/schemas/ai.py::ComplaintAnalysis) already exist. Building this is:
  - define the system instruction (developed/tested in Google AI Studio)
  - register tool function schemas
  - run the loop until the model emits a final ComplaintAnalysis
"""

from __future__ import annotations

from app.agents.tools import Tool
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput

SYSTEM_INSTRUCTION = """You are CIVIKTA's civic-complaint triage agent for Delhi.
Given a citizen complaint (text + images + location), classify it into a structured
civic issue. Use tools to resolve geography and check for nearby duplicate issues.
Never invent the final routing authority — that is decided deterministically
downstream. Return only the structured ComplaintAnalysis."""


class ComplaintTriageAgent:
    def __init__(self, tools: dict[str, Tool], model: str) -> None:
        self.tools = tools
        self.model = model

    async def run(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
        # TODO(agent): ADK loop — feed SYSTEM_INSTRUCTION + inp, let the model call
        # self.tools[...] iteratively, then parse the final ComplaintAnalysis.
        raise NotImplementedError("Implement the ADK tool-calling loop here.")
