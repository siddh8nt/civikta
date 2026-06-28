"""Issue taxonomy + asset ontology.

Three-level hierarchy:
  L1  category_slug  (citizen-facing, 7+1 buckets)
  L2  subcategory    (internal routing aid — stored in issue_subcategory_slug)
  L3  issue_type_slug (the actual classification unit, 55 types)

`CATEGORY_BY_TYPE` and `SUBCATEGORY_BY_TYPE` let the AI triage and routing
engine snap a raw description to the correct branch of the taxonomy.
"""

from __future__ import annotations

# ── L1: citizen-facing categories ────────────────────────────────────────────
CATEGORIES: dict[str, str] = {
    "Roads & Streets":                  "roads_streets",
    "Water / Sewer / Drainage":         "water_sewer_drainage",
    "Garbage & Sanitation":             "garbage_sanitation",
    "Streetlights & Electrical":        "lights_electrical",
    "Public Safety Hazard":             "public_safety",
    "Parks / Public Spaces":            "parks_public_space",
    "Animals / Pollution / Other":      "animals_other",
}

# ── L3 → L1: type slug to category slug ──────────────────────────────────────
CATEGORY_BY_TYPE: dict[str, str] = {

    # ── Roads & Streets ──────────────────────────────────────────────────────
    "pothole_local_road":           "roads_streets",
    "pothole_major_road":           "roads_streets",
    "road_surface_crack":           "roads_streets",
    "road_depression":              "roads_streets",
    "road_collapse":                "roads_streets",
    "road_obstruction_debris":      "roads_streets",
    "fallen_tree_road":             "roads_streets",
    "broken_footpath":              "roads_streets",
    "footpath_missing_ramp":        "roads_streets",
    "vehicle_on_footpath":          "roads_streets",
    "traffic_signal_failure":       "roads_streets",
    "missing_road_sign":            "roads_streets",
    "road_divider_damaged":         "roads_streets",
    "bus_shelter_damaged":          "roads_streets",
    "road_obstruction":             "roads_streets",    # legacy slug — keep

    # ── Water / Sewer / Drainage ─────────────────────────────────────────────
    "sewer_overflow":               "water_sewer_drainage",
    "no_water_supply":              "water_sewer_drainage",
    "contaminated_water":           "water_sewer_drainage",
    "pipeline_leakage":             "water_sewer_drainage",
    "overflowing_water_tank":       "water_sewer_drainage",
    "broken_public_tap":            "water_sewer_drainage",
    "clogged_local_drain":          "water_sewer_drainage",
    "open_drain_cover_missing":     "water_sewer_drainage",
    "waterlogging":                 "water_sewer_drainage",
    "major_flooding":               "water_sewer_drainage",
    "stagnant_water":               "water_sewer_drainage",
    "water_body_pollution":         "water_sewer_drainage",

    # ── Garbage & Sanitation ─────────────────────────────────────────────────
    "garbage_not_collected":        "garbage_sanitation",
    "overflowing_garbage":          "garbage_sanitation",
    "illegal_dumping":              "garbage_sanitation",
    "construction_debris_dump":     "garbage_sanitation",
    "dead_animal":                  "garbage_sanitation",
    "garbage_burning":              "garbage_sanitation",
    "missing_public_dustbin":       "garbage_sanitation",
    "street_uncleaned":             "garbage_sanitation",
    "public_toilet_dirty":          "garbage_sanitation",
    "public_toilet_locked":         "garbage_sanitation",
    "public_toilet_no_water":       "garbage_sanitation",
    "public_toilet_sewage":         "garbage_sanitation",

    # ── Streetlights & Electrical ────────────────────────────────────────────
    "streetlight_not_working":      "lights_electrical",
    "streetlights_stretch_dark":    "lights_electrical",
    "streetlight_flickering":       "lights_electrical",
    "exposed_wire":                 "lights_electrical",
    "leaning_electric_pole":        "lights_electrical",
    "sparking_junction_box":        "lights_electrical",
    "broken_lamp_pole":             "lights_electrical",

    # ── Public Safety ────────────────────────────────────────────────────────
    "open_manhole":                 "public_safety",
    "broken_manhole_cover":         "public_safety",
    "structural_hazard":            "public_safety",
    "open_trench":                  "public_safety",
    "slip_hazard":                  "public_safety",
    "electrical_hazard_public":     "public_safety",
    "unsafe_structure":             "public_safety",

    # ── Parks & Public Space (incl. encroachment) ────────────────────────────
    "park_maintenance_issue":       "parks_public_space",
    "tree_hazard":                  "parks_public_space",
    "broken_play_equipment":        "parks_public_space",
    "park_lighting_failure":        "parks_public_space",
    "broken_bench":                 "parks_public_space",
    "broken_public_fixture":        "parks_public_space",
    "footpath_encroachment":        "parks_public_space",
    "road_encroachment_material":   "parks_public_space",
    "illegal_structure_public_land": "parks_public_space",
    "drain_encroachment":           "parks_public_space",

    # ── Animals / Pollution / Other ──────────────────────────────────────────
    "stray_dog_issue":              "animals_other",
    "cattle_nuisance":              "animals_other",
    "animal_nuisance":              "animals_other",
    "mosquito_breeding":            "animals_other",
    "construction_dust_pollution":  "animals_other",
    "noise_pollution":              "animals_other",
    "complaint_unactioned":         "animals_other",
    "false_closure_reported":       "animals_other",
    "chronic_issue_hotspot":        "animals_other",
    "missed_routine_service":       "animals_other",
}

# ── L3 → L2: type slug to subcategory slug ───────────────────────────────────
SUBCATEGORY_BY_TYPE: dict[str, str] = {
    # Roads
    "pothole_local_road":           "road_surface_damage",
    "pothole_major_road":           "road_surface_damage",
    "road_surface_crack":           "road_surface_damage",
    "road_depression":              "road_surface_damage",
    "road_collapse":                "road_surface_damage",
    "road_obstruction_debris":      "road_obstruction",
    "fallen_tree_road":             "road_obstruction",
    "road_obstruction":             "road_obstruction",
    "broken_footpath":              "footpath_access",
    "footpath_missing_ramp":        "footpath_access",
    "vehicle_on_footpath":          "footpath_access",
    "footpath_encroachment":        "footpath_access",
    "traffic_signal_failure":       "signage_signals",
    "missing_road_sign":            "signage_signals",
    "road_divider_damaged":         "signage_signals",
    "bus_shelter_damaged":          "commuter_infra",
    "road_encroachment_material":   "road_obstruction",
    # Water/Sewer
    "sewer_overflow":               "sewer_overflow",
    "pipeline_leakage":             "water_leakage",
    "overflowing_water_tank":       "water_leakage",
    "broken_public_tap":            "water_leakage",
    "no_water_supply":              "supply_disruption",
    "contaminated_water":           "water_quality",
    "clogged_local_drain":          "drain_blockage",
    "open_drain_cover_missing":     "drain_safety",
    "waterlogging":                 "waterlogging",
    "major_flooding":               "flooding",
    "stagnant_water":               "vector_hazard",
    "water_body_pollution":         "pollution",
    # Sanitation
    "garbage_not_collected":        "collection_failure",
    "overflowing_garbage":          "collection_failure",
    "illegal_dumping":              "illegal_dumping",
    "construction_debris_dump":     "illegal_dumping",
    "dead_animal":                  "hazardous_waste",
    "garbage_burning":              "burning_waste",
    "missing_public_dustbin":       "public_bin_infra",
    "street_uncleaned":             "street_cleanliness",
    "public_toilet_dirty":          "toilet_cleanliness",
    "public_toilet_locked":         "toilet_functionality",
    "public_toilet_no_water":       "toilet_functionality",
    "public_toilet_sewage":         "toilet_cleanliness",
    # Electrical
    "streetlight_not_working":      "streetlight_failure",
    "streetlights_stretch_dark":    "streetlight_failure",
    "streetlight_flickering":       "streetlight_failure",
    "broken_lamp_pole":             "lighting_infra_damage",
    "exposed_wire":                 "electrical_hazard",
    "leaning_electric_pole":        "electrical_hazard",
    "sparking_junction_box":        "electrical_hazard",
    # Safety
    "open_manhole":                 "manholes_openings",
    "broken_manhole_cover":         "manholes_openings",
    "structural_hazard":            "structural_hazard",
    "open_trench":                  "excavation_hazard",
    "slip_hazard":                  "slip_trip_hazard",
    "electrical_hazard_public":     "electrical_hazard",
    "unsafe_structure":             "structural_hazard",
    # Parks
    "park_maintenance_issue":       "park_maintenance",
    "tree_hazard":                  "tree_management",
    "broken_play_equipment":        "equipment_damage",
    "park_lighting_failure":        "park_lighting",
    "broken_bench":                 "seating_fixtures",
    "broken_public_fixture":        "seating_fixtures",
    "illegal_structure_public_land": "encroachment",
    "drain_encroachment":           "encroachment",
    # Animals/Other
    "stray_dog_issue":              "stray_dogs",
    "cattle_nuisance":              "cattle_nuisance",
    "animal_nuisance":              "other_animals",
    "mosquito_breeding":            "vector_hazard",
    "construction_dust_pollution":  "air_pollution",
    "noise_pollution":              "noise_pollution",
    "complaint_unactioned":         "service_failure",
    "false_closure_reported":       "service_failure",
    "chronic_issue_hotspot":        "service_failure",
    "missed_routine_service":       "service_failure",
}

ISSUE_TYPES: list[str] = list(CATEGORY_BY_TYPE.keys())

# ── Asset types ───────────────────────────────────────────────────────────────
ASSET_TYPES: list[str] = [
    # Roads
    "local_lane", "colony_road", "arterial_road", "collector_road",
    "flyover", "underpass", "service_road", "national_highway",
    # Pedestrian
    "footpath", "pedestrian_crossing", "road_row",
    # Water/Sewer
    "water_pipeline", "sewer_line", "manhole",
    # Drainage
    "local_open_drain", "roadside_storm_drain", "trunk_drain", "nallah",
    # Sanitation
    "community_bin", "garbage_blackspot", "public_toilet",
    # Parks / Public Space
    "park", "dda_park", "play_area", "tree", "public_bench",
    "public_space", "dda_land", "public_land",
    # Electrical
    "streetlight_pole", "junction_box", "transformer_area",
    # Other
    "footpath_row", "bus_shelter",
]

# ── Impact tag vocabulary ─────────────────────────────────────────────────────
IMPACT_TAGS: list[str] = [
    "blocks_pedestrian",
    "blocks_traffic",
    "accident_risk",
    "flood_risk",
    "health_hazard",
    "women_safety_risk",
    "school_zone_risk",
    "hospital_zone_risk",
    "night_visibility_risk",
    "elderly_accessibility_risk",
    "children_at_risk",
    "public_transport_affected",
]


def category_for_type(issue_type_slug: str | None) -> str | None:
    if not issue_type_slug:
        return None
    return CATEGORY_BY_TYPE.get(issue_type_slug)


def subcategory_for_type(issue_type_slug: str | None) -> str | None:
    if not issue_type_slug:
        return None
    return SUBCATEGORY_BY_TYPE.get(issue_type_slug)
