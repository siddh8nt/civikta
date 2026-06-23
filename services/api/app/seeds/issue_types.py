"""Issue taxonomy + asset ontology (PRD §14, §15).

`CATEGORY_BY_TYPE` lets the stub LLM and validators map a type slug to its
category. The 18 MVP type slugs and asset slugs live here as the source of truth.
"""

from __future__ import annotations

# citizen-facing categories -> category slug
CATEGORIES: dict[str, str] = {
    "Roads & Streets": "roads_streets",
    "Water / Sewer / Drainage": "water_sewer_drainage",
    "Garbage & Sanitation": "garbage_sanitation",
    "Lights / Electrical": "lights_electrical",
    "Public Safety Hazard": "public_safety",
    "Parks / Encroachment / Public Space": "parks_public_space",
    "Animals / Pollution / Other": "animals_other",
}

# 18 backend issue type slugs -> category slug
CATEGORY_BY_TYPE: dict[str, str] = {
    "garbage_not_collected": "garbage_sanitation",
    "overflowing_garbage": "garbage_sanitation",
    "illegal_dumping": "garbage_sanitation",
    "pothole_local_road": "roads_streets",
    "pothole_major_road": "roads_streets",
    "broken_footpath": "roads_streets",
    "sewer_overflow": "water_sewer_drainage",
    "no_water_supply": "water_sewer_drainage",
    "contaminated_water": "water_sewer_drainage",
    "clogged_local_drain": "water_sewer_drainage",
    "waterlogging": "water_sewer_drainage",
    "streetlight_not_working": "lights_electrical",
    "park_maintenance_issue": "parks_public_space",
    "tree_hazard": "parks_public_space",
    "footpath_encroachment": "parks_public_space",
    "road_obstruction": "public_safety",
    "stray_dog_issue": "animals_other",
    "dead_animal": "animals_other",
}

ISSUE_TYPES: list[str] = list(CATEGORY_BY_TYPE.keys())

ASSET_TYPES: list[str] = [
    "local_lane", "colony_road", "arterial_road", "flyover", "footpath",
    "water_pipeline", "sewer_line", "manhole", "local_open_drain",
    "roadside_storm_drain", "trunk_drain", "community_bin", "garbage_blackspot",
    "park", "tree", "public_toilet", "footpath_row", "road_row", "dda_land",
    "public_space",
]


def category_for_type(issue_type_slug: str | None) -> str | None:
    if not issue_type_slug:
        return None
    return CATEGORY_BY_TYPE.get(issue_type_slug)
