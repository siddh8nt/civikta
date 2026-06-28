"""Authority master (mirrors infra/sql/02_seed_demo.sql + 03_routing_rules.sql)."""

from __future__ import annotations

from app.models.authority import AuthorityRecord

AUTHORITIES: list[AuthorityRecord] = [
    # ── MCD ──────────────────────────────────────────────────────────────────
    AuthorityRecord(
        slug="mcd_sanitation", authority_name="MCD - Sanitation Department",
        authority_family="municipal", local_body_scope="MCD",
        category_slugs=["garbage_sanitation", "animals_other"],
        sla_target_hours=24, contact_portal_url="https://mcdonline.nic.in",
    ),
    AuthorityRecord(
        slug="mcd_engineering", authority_name="MCD - Engineering Department",
        authority_family="municipal", local_body_scope="MCD",
        category_slugs=["roads_streets", "lights_electrical", "public_safety", "parks_public_space"],
        sla_target_hours=72, contact_portal_url="https://mcdonline.nic.in",
    ),
    AuthorityRecord(
        slug="mcd_horticulture", authority_name="MCD - Horticulture Department",
        authority_family="municipal", local_body_scope="MCD",
        category_slugs=["parks_public_space"],
        sla_target_hours=72, contact_portal_url="https://mcdonline.nic.in",
    ),
    AuthorityRecord(
        slug="mcd_public_health", authority_name="MCD - Public Health & Veterinary",
        authority_family="municipal", local_body_scope="MCD",
        category_slugs=["garbage_sanitation", "animals_other"],
        sla_target_hours=24, contact_portal_url="https://mcdonline.nic.in",
    ),

    # ── NDMC ─────────────────────────────────────────────────────────────────
    AuthorityRecord(
        slug="ndmc_sanitation", authority_name="NDMC - Sanitation",
        authority_family="municipal", local_body_scope="NDMC",
        category_slugs=["garbage_sanitation"],
        sla_target_hours=24, contact_portal_url="https://ndmc.gov.in",
    ),
    AuthorityRecord(
        slug="ndmc_civil", authority_name="NDMC - Civil & Engineering",
        authority_family="municipal", local_body_scope="NDMC",
        category_slugs=["roads_streets", "lights_electrical", "public_safety", "water_sewer_drainage"],
        sla_target_hours=72, contact_portal_url="https://ndmc.gov.in",
    ),
    AuthorityRecord(
        slug="ndmc_horticulture", authority_name="NDMC - Horticulture",
        authority_family="municipal", local_body_scope="NDMC",
        category_slugs=["parks_public_space"],
        sla_target_hours=72, contact_portal_url="https://ndmc.gov.in",
    ),

    # ── Delhi Cantonment Board ────────────────────────────────────────────────
    AuthorityRecord(
        slug="dcb_civic", authority_name="Delhi Cantonment Board",
        authority_family="municipal", local_body_scope="DCB",
        category_slugs=["roads_streets", "garbage_sanitation", "lights_electrical"],
        sla_target_hours=72,
    ),

    # ── Service-specific bodies ───────────────────────────────────────────────
    AuthorityRecord(
        slug="djb", authority_name="Delhi Jal Board",
        department_name="Water Supply & Sewerage",
        authority_family="service_specific",
        category_slugs=["water_sewer_drainage"],
        sla_target_hours=12, contact_portal_url="https://djb.gov.in",
    ),
    AuthorityRecord(
        slug="pwd", authority_name="Public Works Department",
        department_name="Roads, Bridges & Public Buildings",
        authority_family="service_specific",
        category_slugs=["roads_streets"],
        sla_target_hours=72, contact_portal_url="https://pwd.delhi.gov.in",
    ),
    AuthorityRecord(
        slug="ifcd", authority_name="Irrigation & Flood Control Department",
        department_name="Storm Drains & Flood Infrastructure",
        authority_family="service_specific",
        category_slugs=["water_sewer_drainage"],
        sla_target_hours=48, contact_portal_url="https://ifc.delhi.gov.in",
    ),
    AuthorityRecord(
        slug="dda", authority_name="Delhi Development Authority",
        department_name="Land, Housing & Parks",
        authority_family="service_specific",
        category_slugs=["parks_public_space"],
        sla_target_hours=168, contact_portal_url="https://dda.gov.in",
    ),

    # ── Enforcement ──────────────────────────────────────────────────────────
    AuthorityRecord(
        slug="delhi_police", authority_name="Delhi Police",
        authority_family="enforcement",
        category_slugs=["public_safety", "animals_other"],
        sla_target_hours=4, contact_portal_url="https://delhipolice.gov.in",
    ),

    # ── National ─────────────────────────────────────────────────────────────
    AuthorityRecord(
        slug="nhai", authority_name="National Highways Authority of India",
        authority_family="service_specific",
        category_slugs=["roads_streets"],
        sla_target_hours=168, contact_portal_url="https://nhai.gov.in",
    ),
]
