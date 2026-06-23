"""Pipeline seam factory — the single most important extension point.

The complaint intake orchestration is a swappable `ComplaintPipeline`. Default is
the deterministic, fixed-order pipeline. Set CIVIKTA_PIPELINE=agentic once the
ADK/Gemini agent loop is implemented — routers don't change.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import PipelineKind, get_settings
from app.core.deps import get_services
from app.pipeline.base import ComplaintPipeline


@lru_cache
def get_pipeline() -> ComplaintPipeline:
    settings = get_settings()
    services = get_services()
    if settings.civikta_pipeline is PipelineKind.agentic:
        from app.pipeline.agentic import AgenticPipeline

        return AgenticPipeline(services)
    from app.pipeline.deterministic import DeterministicPipeline

    return DeterministicPipeline(services)
