"""Routing rules (mirrors infra/sql/03_routing_rules.sql).

Decision logic (lower rule_priority wins first):
  Priority 10  — infrastructure owner regardless of local body (DJB, PWD arterial)
  Priority 20  — asset-class overrides (trunk drain → IFCD, NH → NHAI)
  Priority 40  — land-owner overrides (DDA parks, DDA land)
  Priority 50  — local-body-specific default for common types
  Priority 60  — enforcement co-tags (police secondary)
  Priority 200 — catch-all fallback per local body

None = wildcard (matches any value).
"""

from __future__ import annotations

from app.models.routing_rule import RoutingRuleRecord


def _r(**kw) -> RoutingRuleRecord:
    return RoutingRuleRecord(**kw)


ROUTING_RULES: list[RoutingRuleRecord] = [

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 10 — Infrastructure owners (DJB, PWD arterial, IFCD trunk)
    # These fire before any local-body-specific rules.
    # ══════════════════════════════════════════════════════════════════════════

    # Water / Sewer — always DJB
    _r(issue_type_slug="sewer_overflow",
       primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
       rule_priority=10, confidence_score=0.95,
       notes="DJB owns all underground sewer infrastructure"),
    _r(issue_type_slug="pipeline_leakage",
       primary_authority_slug="djb", rule_priority=10, confidence_score=0.95),
    _r(issue_type_slug="no_water_supply",
       primary_authority_slug="djb", rule_priority=10, confidence_score=0.95),
    _r(issue_type_slug="contaminated_water",
       primary_authority_slug="djb", rule_priority=10, confidence_score=0.95),
    _r(issue_type_slug="overflowing_water_tank",
       primary_authority_slug="djb", rule_priority=10, confidence_score=0.9),
    _r(issue_type_slug="broken_public_tap",
       primary_authority_slug="djb", rule_priority=10, confidence_score=0.9),
    _r(issue_type_slug="water_body_pollution",
       primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
       rule_priority=10, confidence_score=0.85),

    # Open manhole / broken cover — DJB (sewer chamber) + MCD engineering
    _r(issue_type_slug="open_manhole",
       primary_authority_slug="djb", secondary_authority_slug="mcd_engineering",
       rule_priority=10, confidence_score=0.9,
       notes="Manhole cover = DJB; road restoration = MCD engineering"),
    _r(issue_type_slug="broken_manhole_cover",
       primary_authority_slug="djb", secondary_authority_slug="mcd_engineering",
       rule_priority=10, confidence_score=0.9),

    # Public toilet sewage — DJB (sewer connection)
    _r(issue_type_slug="public_toilet_sewage",
       primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
       rule_priority=10, confidence_score=0.85),

    # Arterial road potholes / damage — PWD
    _r(issue_type_slug="pothole_major_road", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=10, confidence_score=0.9),
    _r(issue_type_slug="road_depression", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=10, confidence_score=0.9),
    _r(issue_type_slug="road_collapse", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=10, confidence_score=0.9),
    _r(issue_type_slug="road_divider_damaged", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=10, confidence_score=0.85),
    _r(issue_type_slug="missing_road_sign", road_class="arterial",
       primary_authority_slug="pwd", rule_priority=10, confidence_score=0.85),

    # Waterlogging on arterial corridors — PWD + IFCD
    _r(issue_type_slug="waterlogging", road_class="arterial",
       primary_authority_slug="pwd", secondary_authority_slug="ifcd",
       rule_priority=10, confidence_score=0.85),

    # National highway — NHAI
    _r(issue_type_slug="pothole_major_road", road_class="national_highway",
       primary_authority_slug="nhai", rule_priority=5, confidence_score=0.9),
    _r(issue_type_slug="road_obstruction_debris", road_class="national_highway",
       primary_authority_slug="nhai", rule_priority=5, confidence_score=0.85),

    # Traffic signals — Delhi Police Traffic (enforcement)
    _r(issue_type_slug="traffic_signal_failure",
       primary_authority_slug="delhi_police", rule_priority=10, confidence_score=0.85,
       notes="Traffic signals are managed by Delhi Police Traffic Wing"),

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 20 — Asset-class overrides
    # ══════════════════════════════════════════════════════════════════════════

    # Trunk drain / nallah — IFCD
    _r(issue_type_slug="clogged_local_drain", drain_type="trunk",
       primary_authority_slug="ifcd", rule_priority=20, confidence_score=0.9),
    _r(issue_type_slug="clogged_local_drain", asset_type_slug="trunk_drain",
       primary_authority_slug="ifcd", rule_priority=20, confidence_score=0.9),
    _r(issue_type_slug="clogged_local_drain", asset_type_slug="nallah",
       primary_authority_slug="ifcd", rule_priority=20, confidence_score=0.9),
    _r(issue_type_slug="major_flooding",
       primary_authority_slug="ifcd", secondary_authority_slug="pwd",
       rule_priority=20, confidence_score=0.85,
       notes="Trunk drain / Yamuna flood infrastructure = IFCD"),
    _r(issue_type_slug="stagnant_water", drain_type="trunk",
       primary_authority_slug="ifcd", rule_priority=20, confidence_score=0.8),

    # Fallen tree blocking road — MCD horticulture first
    _r(issue_type_slug="fallen_tree_road",
       primary_authority_slug="mcd_horticulture", secondary_authority_slug="mcd_engineering",
       rule_priority=20, confidence_score=0.9,
       notes="Horticulture clears tree; engineering restores road surface"),

    # Open drain cover — DJB if sewer drain, else MCD engineering
    _r(issue_type_slug="open_drain_cover_missing", drain_type="sewer",
       primary_authority_slug="djb", rule_priority=20, confidence_score=0.85),

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 40 — Land-owner overrides (DDA, PWD land)
    # ══════════════════════════════════════════════════════════════════════════

    # DDA parks
    _r(issue_type_slug="park_maintenance_issue", land_owner_hint="dda",
       primary_authority_slug="dda", rule_priority=40, confidence_score=0.88,
       notes="DDA owns and maintains DDA parks"),
    _r(issue_type_slug="broken_play_equipment", land_owner_hint="dda",
       primary_authority_slug="dda", rule_priority=40, confidence_score=0.85),
    _r(issue_type_slug="park_lighting_failure", land_owner_hint="dda",
       primary_authority_slug="dda", secondary_authority_slug="mcd_engineering",
       rule_priority=40, confidence_score=0.8),
    _r(issue_type_slug="illegal_structure_public_land", land_owner_hint="dda",
       primary_authority_slug="dda", rule_priority=40, confidence_score=0.85,
       notes="Encroachment on DDA land → DDA enforcement"),
    _r(issue_type_slug="illegal_dumping", land_owner_hint="dda",
       primary_authority_slug="mcd_sanitation", secondary_authority_slug="dda",
       rule_priority=40, confidence_score=0.82),

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 50 — Local-body-specific defaults for common issue types
    # ══════════════════════════════════════════════════════════════════════════

    # Roads (local) — by local body
    _r(local_body_type="MCD", issue_type_slug="pothole_local_road",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="pothole_local_road",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="DCB", issue_type_slug="pothole_local_road",
       primary_authority_slug="dcb_civic", rule_priority=50, confidence_score=0.85),

    _r(local_body_type="MCD", issue_type_slug="road_surface_crack",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="road_depression",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="road_collapse",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="road_obstruction_debris",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="bus_shelter_damaged",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="NDMC", issue_type_slug="bus_shelter_damaged",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.75),

    # Footpaths — by local body
    _r(local_body_type="MCD", issue_type_slug="broken_footpath",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="NDMC", issue_type_slug="broken_footpath",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="footpath_missing_ramp",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="road_divider_damaged",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="MCD", issue_type_slug="missing_road_sign",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),

    # Local drains — by local body
    _r(local_body_type="MCD", issue_type_slug="clogged_local_drain",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="clogged_local_drain",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="open_drain_cover_missing",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="waterlogging",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8,
       notes="Local colony waterlogging = MCD engineering"),
    _r(local_body_type="MCD", issue_type_slug="stagnant_water",
       primary_authority_slug="mcd_sanitation", secondary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="drain_encroachment",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),

    # Sanitation — by local body
    _r(local_body_type="MCD", issue_type_slug="garbage_not_collected",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.92),
    _r(local_body_type="NDMC", issue_type_slug="garbage_not_collected",
       primary_authority_slug="ndmc_sanitation", rule_priority=50, confidence_score=0.92),
    _r(local_body_type="DCB", issue_type_slug="garbage_not_collected",
       primary_authority_slug="dcb_civic", rule_priority=50, confidence_score=0.9),
    _r(local_body_type="MCD", issue_type_slug="overflowing_garbage",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.9),
    _r(local_body_type="MCD", issue_type_slug="illegal_dumping",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="construction_debris_dump",
       primary_authority_slug="mcd_sanitation", secondary_authority_slug="pwd",
       rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="dead_animal",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.88),
    _r(local_body_type="MCD", issue_type_slug="garbage_burning",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="missing_public_dustbin",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="street_uncleaned",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.88),
    _r(local_body_type="NDMC", issue_type_slug="street_uncleaned",
       primary_authority_slug="ndmc_sanitation", rule_priority=50, confidence_score=0.88),
    _r(local_body_type="MCD", issue_type_slug="public_toilet_dirty",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="public_toilet_locked",
       primary_authority_slug="mcd_sanitation", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="public_toilet_no_water",
       primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
       rule_priority=50, confidence_score=0.8),

    # Streetlights — by local body
    _r(local_body_type="MCD", issue_type_slug="streetlight_not_working",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="NDMC", issue_type_slug="streetlight_not_working",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="DCB", issue_type_slug="streetlight_not_working",
       primary_authority_slug="dcb_civic", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="streetlights_stretch_dark",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.82),
    _r(local_body_type="MCD", issue_type_slug="streetlight_flickering",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="broken_lamp_pole",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.82),
    _r(local_body_type="MCD", issue_type_slug="exposed_wire",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75,
       notes="Report to DISCOM (BSES/Tata Power) as well; MCD as civic first responder"),
    _r(local_body_type="MCD", issue_type_slug="leaning_electric_pole",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="MCD", issue_type_slug="sparking_junction_box",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="NDMC", issue_type_slug="exposed_wire",
       primary_authority_slug="ndmc_civil", rule_priority=50, confidence_score=0.75),

    # Public Safety — by local body
    _r(local_body_type="MCD", issue_type_slug="structural_hazard",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="open_trench",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="slip_hazard",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="MCD", issue_type_slug="unsafe_structure",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.78),
    _r(local_body_type="MCD", issue_type_slug="electrical_hazard_public",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),

    # Parks — by local body
    _r(local_body_type="MCD", issue_type_slug="park_maintenance_issue",
       primary_authority_slug="mcd_horticulture", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="park_maintenance_issue",
       primary_authority_slug="ndmc_horticulture", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="tree_hazard",
       primary_authority_slug="mcd_horticulture", secondary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.85),
    _r(local_body_type="NDMC", issue_type_slug="tree_hazard",
       primary_authority_slug="ndmc_horticulture", rule_priority=50, confidence_score=0.85),
    _r(local_body_type="MCD", issue_type_slug="broken_play_equipment",
       primary_authority_slug="mcd_horticulture", rule_priority=50, confidence_score=0.82),
    _r(local_body_type="MCD", issue_type_slug="broken_bench",
       primary_authority_slug="mcd_horticulture", rule_priority=50, confidence_score=0.78),
    _r(local_body_type="MCD", issue_type_slug="broken_public_fixture",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),
    _r(local_body_type="MCD", issue_type_slug="park_lighting_failure",
       primary_authority_slug="mcd_horticulture", secondary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.8),
    _r(local_body_type="MCD", issue_type_slug="illegal_structure_public_land",
       primary_authority_slug="mcd_engineering", rule_priority=50, confidence_score=0.75),

    # Animals / Public Health — by local body
    _r(local_body_type="MCD", issue_type_slug="stray_dog_issue",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.87),
    _r(local_body_type="MCD", issue_type_slug="cattle_nuisance",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.82),
    _r(local_body_type="MCD", issue_type_slug="animal_nuisance",
       primary_authority_slug="mcd_public_health", rule_priority=50, confidence_score=0.78),
    _r(local_body_type="MCD", issue_type_slug="mosquito_breeding",
       primary_authority_slug="mcd_public_health", secondary_authority_slug="djb",
       rule_priority=50, confidence_score=0.82),

    # Civic service failure — oversight escalation
    _r(issue_type_slug="complaint_unactioned",
       primary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.5,
       notes="Escalate to oversight dashboard; re-route to original authority"),
    _r(issue_type_slug="false_closure_reported",
       primary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.5,
       notes="Flag for oversight review; bump urgency score"),
    _r(issue_type_slug="chronic_issue_hotspot",
       primary_authority_slug="mcd_engineering",
       rule_priority=50, confidence_score=0.5,
       notes="Chronic = 3+ reports same location in 90 days; auto-escalate"),
    _r(issue_type_slug="missed_routine_service",
       primary_authority_slug="mcd_sanitation",
       rule_priority=50, confidence_score=0.6),

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 60 — Enforcement co-tags (police as secondary)
    # ══════════════════════════════════════════════════════════════════════════

    _r(issue_type_slug="footpath_encroachment",
       primary_authority_slug="mcd_engineering", secondary_authority_slug="delhi_police",
       rule_priority=60, confidence_score=0.72,
       notes="MCD clears encroachment; police support for hawker/vehicle removal"),
    _r(issue_type_slug="road_encroachment_material",
       primary_authority_slug="mcd_engineering", secondary_authority_slug="delhi_police",
       rule_priority=60, confidence_score=0.72),
    _r(issue_type_slug="vehicle_on_footpath",
       primary_authority_slug="delhi_police", secondary_authority_slug="mcd_engineering",
       rule_priority=60, confidence_score=0.82,
       notes="Vehicle removal = police enforcement primary"),
    _r(issue_type_slug="road_obstruction",
       primary_authority_slug="mcd_engineering", secondary_authority_slug="delhi_police",
       rule_priority=60, confidence_score=0.7),
    _r(issue_type_slug="noise_pollution",
       primary_authority_slug="delhi_police",
       rule_priority=60, confidence_score=0.75,
       notes="Noise complaints are law enforcement matters; also tag pollution cell"),
    _r(issue_type_slug="construction_dust_pollution",
       primary_authority_slug="mcd_engineering",
       rule_priority=60, confidence_score=0.7),

    # ══════════════════════════════════════════════════════════════════════════
    # PRIORITY 200 — Catch-all fallbacks per local body
    # ══════════════════════════════════════════════════════════════════════════

    _r(local_body_type="MCD",  primary_authority_slug="mcd_engineering",
       rule_priority=200, confidence_score=0.4, notes="MCD default"),
    _r(local_body_type="NDMC", primary_authority_slug="ndmc_civil",
       rule_priority=200, confidence_score=0.4, notes="NDMC default"),
    _r(local_body_type="DCB",  primary_authority_slug="dcb_civic",
       rule_priority=200, confidence_score=0.4, notes="DCB default"),
]
