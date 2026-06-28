"""Central configuration. Every external dependency is selected here via a seam flag.

The defaults (`stub` / `memory` / `deterministic`) let the whole API run with no
API keys and no database. Flip a flag in `.env` to swap in a real implementation
once you've written it — no caller code changes.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineKind(str, Enum):
    deterministic = "deterministic"
    agentic = "agentic"


class LLMKind(str, Enum):
    stub = "stub"
    gemini = "gemini"


class RepoKind(str, Enum):
    memory = "memory"
    supabase = "supabase"


class AuthKind(str, Enum):
    stub = "stub"
    firebase = "firebase"
    supabase = "supabase"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    # --- seam selectors ---
    civikta_pipeline: PipelineKind = PipelineKind.deterministic
    civikta_llm: LLMKind = LLMKind.stub
    civikta_repo: RepoKind = RepoKind.memory
    civikta_auth: AuthKind = AuthKind.stub

    civikta_cors_origins: str = "http://localhost:3000"

    # --- Gemini / Google AI Studio (free tier) ---
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    vertex_embedding_model: str = "text-embedding-004"

    # --- Vertex AI / Google Agent Platform (GCP credits, no rate limits) ---
    gcp_project: str | None = None
    gcp_location: str = "us-central1"

    # --- Supabase ---
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    supabase_storage_bucket: str = "civikta-media"

    # --- Firebase ---
    firebase_project_id: str | None = None
    google_application_credentials: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.civikta_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
