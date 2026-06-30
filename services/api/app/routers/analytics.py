"""Analytics chatbot endpoint — Gemini function-calling loop for oversight intelligence."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class HistoryTurn(BaseModel):
    role: str   # "user" | "assistant"
    text: str


class AnalyticsQuery(BaseModel):
    question: str
    context: dict = {}
    history: list[HistoryTurn] = []


class AnalyticsResponse(BaseModel):
    answer: str
    tool_calls: list[dict] = []
    suggested_questions: list[str] = []


@router.post("/query", response_model=AnalyticsResponse, summary="Ask a natural-language question about Delhi's civic data (Gemini)")
async def analytics_query(
    body: AnalyticsQuery,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> AnalyticsResponse:
    """
    **AI-powered analytics chatbot** for oversight officers. Accepts a plain-English question and returns a structured answer using Gemini function-calling.

    Gemini decides which data queries to run (by ward, authority, severity, date range, etc.), executes them against the live Supabase database, and synthesises a human-readable answer with supporting data.

    Example questions:
    - *"Which ward has the most unresolved potholes this month?"*
    - *"How many DJB issues have breached SLA in the last 7 days?"*
    - *"Show me a breakdown of critical issues by authority"*

    Returns `answer` (text), `tool_calls` (what Gemini queried), and `suggested_questions` for follow-up.
    Supports multi-turn conversation via the `history` field.
    """
    history = [{"role": t.role, "text": t.text} for t in body.history]
    result = await services.analytics.query(body.question, body.context, history=history)
    return AnalyticsResponse(**result)
