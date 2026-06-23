"""Repository seam factory.

Returns the in-memory repository by default (runs with no database). Set
CIVIKTA_REPO=supabase once you've implemented SupabaseRepository.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import RepoKind, get_settings
from app.repositories.base import Repository
from app.repositories.memory import MemoryRepository


@lru_cache
def get_repository() -> Repository:
    settings = get_settings()
    if settings.civikta_repo is RepoKind.supabase:
        from app.repositories.supabase import SupabaseRepository

        return SupabaseRepository(settings)
    repo = MemoryRepository()
    repo.seed_demo()
    return repo
