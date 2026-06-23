"""Supabase repository — FUTURE implementation.

To enable: `pip install supabase`, set CIVIKTA_REPO=supabase + SUPABASE_URL /
SUPABASE_SERVICE_KEY, then implement each method against the tables in
infra/sql/schema.sql. The spatial methods (`issues_near`, `issues_in_viewport`)
become PostGIS queries (ST_DWithin / && bbox); duplicate semantic scoring uses
the pgvector `summary_embedding` column.

Every method must satisfy the same `Repository` protocol as MemoryRepository, so
no service code changes when you switch over.
"""

from __future__ import annotations

from app.core.config import Settings


class SupabaseRepository:
    def __init__(self, settings: Settings) -> None:
        if not (settings.supabase_url and settings.supabase_service_key):
            raise RuntimeError(
                "CIVIKTA_REPO=supabase requires SUPABASE_URL and SUPABASE_SERVICE_KEY."
            )
        self.settings = settings
        # from supabase import create_client
        # self.client = create_client(settings.supabase_url, settings.supabase_service_key)
        raise NotImplementedError(
            "SupabaseRepository is a stub. Implement against infra/sql/schema.sql, "
            "or use CIVIKTA_REPO=memory for now."
        )
