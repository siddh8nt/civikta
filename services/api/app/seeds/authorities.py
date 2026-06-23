"""Authority master (mirrors infra/sql/seeds/authorities.sql)."""

from __future__ import annotations

from app.models.authority import AuthorityRecord

AUTHORITIES: list[AuthorityRecord] = [
    AuthorityRecord(slug="mcd_sanitation", authority_name="MCD - Sanitation",
                    authority_family="municipal", local_body_scope="MCD"),
    AuthorityRecord(slug="mcd_engineering", authority_name="MCD - Engineering",
                    authority_family="municipal", local_body_scope="MCD"),
    AuthorityRecord(slug="mcd_horticulture", authority_name="MCD - Horticulture",
                    authority_family="municipal", local_body_scope="MCD"),
    AuthorityRecord(slug="mcd_public_health", authority_name="MCD - Public Health",
                    authority_family="municipal", local_body_scope="MCD"),
    AuthorityRecord(slug="ndmc_sanitation", authority_name="NDMC - Sanitation",
                    authority_family="municipal", local_body_scope="NDMC"),
    AuthorityRecord(slug="ndmc_civil", authority_name="NDMC - Civil",
                    authority_family="municipal", local_body_scope="NDMC"),
    AuthorityRecord(slug="ndmc_horticulture", authority_name="NDMC - Horticulture",
                    authority_family="municipal", local_body_scope="NDMC"),
    AuthorityRecord(slug="dcb_civic", authority_name="Delhi Cantonment Board",
                    authority_family="municipal", local_body_scope="DCB"),
    AuthorityRecord(slug="djb", authority_name="Delhi Jal Board",
                    authority_family="service_specific"),
    AuthorityRecord(slug="pwd", authority_name="Public Works Department",
                    authority_family="service_specific"),
    AuthorityRecord(slug="ifcd", authority_name="Irrigation & Flood Control",
                    authority_family="service_specific"),
    AuthorityRecord(slug="dda", authority_name="Delhi Development Authority",
                    authority_family="service_specific"),
    AuthorityRecord(slug="delhi_police", authority_name="Delhi Police",
                    authority_family="enforcement"),
    AuthorityRecord(slug="nhai", authority_name="National Highways Authority of India",
                    authority_family="service_specific"),
]
