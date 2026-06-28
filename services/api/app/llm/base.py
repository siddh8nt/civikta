"""LLM contract. Both StubLLMClient and the future GeminiClient implement this.

`analyze_complaint` is the multimodal triage call (PRD §20.2). `embed` produces a
768-dim vector for semantic duplicate scoring (Vertex text-embedding-004).
`summarize` powers authority case briefs + oversight cluster summaries.
"""

from __future__ import annotations

from typing import Protocol

from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput

EMBEDDING_DIM = 768


class LLMClient(Protocol):
    async def analyze_complaint(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis: ...
    async def validate_images(self, image_data: list[str]) -> dict: ...
    async def embed(self, text: str) -> list[float]: ...
    async def summarize(self, prompt: str) -> str: ...
