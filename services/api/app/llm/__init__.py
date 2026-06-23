"""LLM seam factory. Stub by default (no API key). Set CIVIKTA_LLM=gemini to use
Gemini via a Google AI Studio key."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import LLMKind, get_settings
from app.llm.base import LLMClient
from app.llm.stub import StubLLMClient


@lru_cache
def get_llm_client() -> LLMClient:
    settings = get_settings()
    if settings.civikta_llm is LLMKind.gemini:
        from app.llm.gemini import GeminiClient

        return GeminiClient(settings)
    return StubLLMClient()
