"""Deterministic routing engine (PRD §22, §30).

Matches a RoutingInput against routing_rules, lowest rule_priority first. A rule
matches when every non-null field on the rule equals the input. This is the
authoritative router — the LLM never decides the final authority.
"""

from __future__ import annotations

from app.models.routing_rule import RoutingRuleRecord
from app.repositories.base import Repository
from app.schemas.routing import RoutingInput, RoutingResult

_FIELDS = (
    "local_body_type", "issue_type_slug", "asset_type_slug",
    "road_class", "drain_type", "land_owner_hint",
)


def _rule_matches(rule: RoutingRuleRecord, inp: RoutingInput) -> bool:
    for field in _FIELDS:
        rule_val = getattr(rule, field)
        if rule_val is None:
            continue  # wildcard
        if getattr(inp, field) != rule_val:
            return False
    return True


def _specificity(rule: RoutingRuleRecord) -> int:
    return sum(1 for f in _FIELDS if getattr(rule, f) is not None)


class RoutingService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def route(self, inp: RoutingInput) -> RoutingResult:
        candidates = [r for r in self.repo.list_routing_rules() if _rule_matches(r, inp)]
        if not candidates:
            return RoutingResult(confidence=0.0, reason={"matched": False})

        # lowest priority first; tie-break on more specific rule
        candidates.sort(key=lambda r: (r.rule_priority, -_specificity(r)))
        best = candidates[0]
        return RoutingResult(
            primary_authority_slug=best.primary_authority_slug,
            secondary_authority_slug=best.secondary_authority_slug,
            confidence=best.confidence_score,
            rule_id=best.id,
            reason={
                "matched": True,
                "rule_priority": best.rule_priority,
                "notes": best.notes,
                "input": inp.model_dump(exclude_none=True),
            },
        )
