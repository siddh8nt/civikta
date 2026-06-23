"""Routing engine contract (PRD §30). Deterministic — never LLM-decided."""

from __future__ import annotations

from pydantic import BaseModel


class RoutingInput(BaseModel):
    local_body_type: str | None = None
    issue_type_slug: str | None = None
    asset_type_slug: str | None = None
    road_class: str | None = None
    drain_type: str | None = None
    land_owner_hint: str | None = None


class RoutingResult(BaseModel):
    primary_authority_slug: str | None = None
    secondary_authority_slug: str | None = None
    confidence: float = 0.0
    rule_id: str | None = None
    reason: dict = {}
