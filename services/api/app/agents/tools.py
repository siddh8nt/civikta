"""Agent-ready tool wrappers (PRD §20.3).

Each deterministic capability is exposed here as a uniform async `Tool` with a
JSON-schema input. The current DeterministicPipeline calls services directly; the
FUTURE AgenticPipeline hands this exact tool list to an ADK/Gemini loop. Because
the tools already exist and are tested, building the agent is just wiring — no
service changes.

`Tool.to_function_schema()` emits an ADK/OpenAI-style function declaration so
registration with the model is one line each.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.core.deps import Services
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import GeoPoint
from app.schemas.routing import RoutingInput


@dataclass
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[[BaseModel], Awaitable[Any]]

    async def __call__(self, payload: dict | BaseModel) -> Any:
        data = payload if isinstance(payload, self.input_model) else self.input_model(
            **(payload.model_dump() if isinstance(payload, BaseModel) else payload)
        )
        return await self.handler(data)

    def to_function_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_model.model_json_schema(),
        }


class EmbedScoreInput(BaseModel):
    text: str
    issue_id: str


def build_tools(services: Services) -> dict[str, Tool]:
    async def _geo(p: GeoPoint):
        return services.geo.resolve(p.latitude, p.longitude)

    async def _routing(p: RoutingInput):
        return services.routing.route(p)

    async def _analyze(p: ComplaintAnalysisInput):
        return await services.ai_triage.analyze(p)

    async def _duplicates(p: ComplaintAnalysisInput):
        analysis = await services.ai_triage.analyze(p)
        return await services.duplicates.find_duplicates(analysis, p.latitude or 0, p.longitude or 0)

    async def _embed_score(p: EmbedScoreInput):
        from app.services.duplicate_detection_service import _cosine

        issue = services.repo.get_issue(p.issue_id)
        if not issue or not issue.public_summary:
            return {"similarity": 0.0}
        a = await services.llm.embed(p.text)
        b = issue.summary_embedding or await services.llm.embed(issue.public_summary)
        return {"similarity": _cosine(a, b)}

    tools = [
        Tool("resolve_delhi_geography",
             "Resolve lat/lng to Delhi local body / ward / locality.", GeoPoint, _geo),
        Tool("lookup_routing_candidates",
             "Deterministically map issue+asset+location hints to authorities.",
             RoutingInput, _routing),
        Tool("analyze_complaint",
             "Classify a complaint into a structured civic issue.",
             ComplaintAnalysisInput, _analyze),
        Tool("duplicate_issue_search",
             "Find nearby open issues this report might corroborate.",
             ComplaintAnalysisInput, _duplicates),
        Tool("embed_and_score_similarity",
             "Cosine similarity between a text and an existing issue's summary embedding.",
             EmbedScoreInput, _embed_score),
    ]
    return {t.name: t for t in tools}
