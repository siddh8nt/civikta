"""Routing rule record. Mirrors the `routing_rules` table (PRD §23.5)."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field


class RoutingRuleRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    local_body_type: str | None = None
    issue_type_slug: str | None = None
    asset_type_slug: str | None = None
    road_class: str | None = None
    drain_type: str | None = None
    land_owner_hint: str | None = None
    primary_authority_slug: str = ""
    secondary_authority_slug: str | None = None
    escalation_authority_slug: str | None = None   # oversight escalation path
    rule_priority: int = 100
    confidence_score: float = 0.8
    notes: str | None = None
