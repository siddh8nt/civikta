"""Auth seam.

StubAuth       — trusts X-Demo-User / X-Demo-Role headers (authority/oversight portals).
SupabaseAuth   — verifies Supabase JWT for citizen requests; falls back to demo headers
                 for authority/oversight portals that don't send a JWT.
FirebaseAuth   — future placeholder.
"""

from __future__ import annotations

from typing import Protocol

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import AuthKind, Settings, get_settings


class AuthIdentity(BaseModel):
    uid: str
    role: str = "citizen"
    name: str | None = None


class AuthProvider(Protocol):
    async def authenticate(self, authorization: str | None, demo_user: str | None,
                           demo_role: str | None) -> AuthIdentity: ...


class StubAuth:
    async def authenticate(self, authorization, demo_user, demo_role) -> AuthIdentity:
        return AuthIdentity(
            uid=demo_user or "demo-citizen",
            role=demo_role or "citizen",
            name="Demo User",
        )


class SupabaseAuth:
    def __init__(self, settings: Settings):
        from supabase import create_client
        self._client = create_client(settings.supabase_url, settings.supabase_service_key)

    async def authenticate(self, authorization, demo_user, demo_role) -> AuthIdentity:
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]
            try:
                resp = self._client.auth.get_user(token)
                user = resp.user
                if not user:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                return AuthIdentity(uid=str(user.id), role="citizen")
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        # No JWT — fall back to demo headers for authority/oversight portals
        return AuthIdentity(
            uid=demo_user or "demo-citizen",
            role=demo_role or "citizen",
        )


class FirebaseAuth:
    async def authenticate(self, authorization, demo_user, demo_role) -> AuthIdentity:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="FirebaseAuth not wired yet.",
        )


def get_auth_provider(settings: Settings = Depends(get_settings)) -> AuthProvider:
    if settings.civikta_auth is AuthKind.supabase:
        return SupabaseAuth(settings)
    if settings.civikta_auth is AuthKind.firebase:
        return FirebaseAuth()
    return StubAuth()


async def get_current_user(
    authorization: str | None = Header(default=None),
    x_demo_user: str | None = Header(default=None),
    x_demo_role: str | None = Header(default=None),
    provider: AuthProvider = Depends(get_auth_provider),
) -> AuthIdentity:
    return await provider.authenticate(authorization, x_demo_user, x_demo_role)
