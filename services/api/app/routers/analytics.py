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


@router.post("/query", response_model=AnalyticsResponse)
async def analytics_query(
    body: AnalyticsQuery,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> AnalyticsResponse:
    history = [{"role": t.role, "text": t.text} for t in body.history]
    result = await services.analytics.query(body.question, body.context, history=history)
    return AnalyticsResponse(**result)
