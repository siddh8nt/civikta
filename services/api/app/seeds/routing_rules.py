"""Routing rules (mirrors infra/sql/seeds/routing_rules.sql).

Lower rule_priority wins first. None = wildcard.
"""

from __future__ import annotations

from app.models.routing_rule import RoutingRuleRecord


def _r(**kw) -> RoutingRuleRecord:
    return RoutingRuleRecord(**kw)


ROUTING_RULES: list[RoutingRuleRecord] = [
    # Water / sewer -> DJB (any local body)
    _r(issue_type_slug="sewer_overflow", primary_authority_slug="djb",
       secondary_authority_slug="mcd_sanitation", rule_priority=10, confidence_score=0.95,
       notes="Sewer = DJB; co-tag local sanitation"),
    _r(issue_type_slug="no_water_supply", primary_authority_slug="djb",
       rule_priority=10, confidence_score=0.95),
    _r(issue_type_slug="contaminated_water", primary_authority_slug="djb",
       rule_priority=10, confidence_score=0.95),

    # Major road / corridor -> PWD
    _r(issue_type_slug="pothole_major_road", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=20, confidence_score=0.9),
    _r(issue_type_slug="waterlogging", road_class="arterial", primary_authority_slug="pwd",
       secondary_authority_slug="ifcd", rule_priority=20, confidence_score=0.85),

    # Trunk drain -> IFCD
    _r(issue_type_slug="clogged_local_drain", asset_type_slug="trunk_drain", drain_type="trunk",
       primary_authority_slug="ifcd", rule_priority=20, confidence_score=0.9),

    # Local body engineering: local roads / drains / footpaths / lights
    _r(local_body_type="MCD", issue_type_slug="pothole_local_road",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="pothole_local_road",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="DCB", issue_type_slug="pothole_local_road",
       primary_authority_slug="dcb_civic", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="clogged_local_drain",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="clogged_local_drain",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="broken_footpath",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="streetlight_not_working",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="NDMC", issue_type_slug="streetlight_not_working",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.8),

    # Sanitation
    _r(local_body_type="MCD", issue_type_slug="garbage_not_collected",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.9),
    _r(local_body_type="NDMC", issue_type_slug="garbage_not_collected",
       primary_authority_slug="ndmc_sanitation", rule_priority=50, confidence_score=0.9),
    _r(local_body_type="MCD", issue_type_slug="overflowing_garbage",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.9),
    _r(local_body_type="MCD", issue_type_slug="illegal_dumping",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.85),

    # Parks by owner
    _r(local_body_type="MCD", issue_type_slug="park_maintenance_issue", asset_type_slug="park",
       primary_authority_slug="mcd_horticulture", rule_priority=50, confidence_score=0.85),
    _r(issue_type_slug="park_maintenance_issue", asset_type_slug="park", land_owner_hint="dda",
       primary_authority_slug="dda", rule_priority=40, confidence_score=0.85, notes="DDA parks"),
    _r(local_body_type="MCD", issue_type_slug="tree_hazard", asset_type_slug="tree",
       primary_authority_slug="mcd_horticulture", rule_priority=50, confidence_score=0.8),

    # Animals / public health
    _r(local_body_type="MCD", issue_type_slug="stray_dog_issue",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="dead_animal",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.85),

    # Encroachment / obstruction
    _r(issue_type_slug="footpath_encroachment", primary_authority_slug="mcd_engineering",
       secondary_authority_slug="delhi_police", rule_priority=60, confidence_score=0.7,
       notes="Co-tag police if obstruction"),
    _r(issue_type_slug="road_obstruction", primary_authority_slug="mcd_engineering",
       secondary_authority_slug="delhi_police", rule_priority=60, confidence_score=0.7),

    # Catch-all fallbacks
    _r(local_body_type="MCD", primary_authority_slug="mcd_engineering",
       rule_priority=200, confidence_score=0.4, notes="MCD default"),
    _r(local_body_type="NDMC", primary_authority_slug="ndmc_civil",
       rule_priority=200, confidence_score=0.4, notes="NDMC default"),
    _r(local_body_type="DCB", primary_authority_slug="dcb_civic",
       rule_priority=200, confidence_score=0.4, notes="DCB default"),
]
