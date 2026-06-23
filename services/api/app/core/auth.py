"""Auth seam.

`AuthProvider` is the contract. `StubAuth` (default) trusts demo headers so the
app is usable with no Firebase project. `FirebaseAuth` (future) verifies a real
Firebase ID token — write it, set CIVIKTA_AUTH=firebase, done.
"""

from __future__ import annotations

from typing import Protocol

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import AuthKind, Settings, get_settings


class AuthIdentity(BaseModel):
    uid: str
    role: str = "citizen"  # citizen / authority / oversight / admin
    name: str | None = None


class AuthProvider(Protocol):
    async def authenticate(self, authorization: str | None, demo_user: str | None,
                           demo_role: str | None) -> AuthIdentity: ...


class StubAuth:
    """Trusts `X-Demo-User` / `X-Demo-Role` headers; falls back to a fixed demo citizen."""

    async def authenticate(self, authorization, demo_user, demo_role) -> AuthIdentity:
        return AuthIdentity(
            uid=demo_user or "demo-citizen",
            role=demo_role or "citizen",
            name="Demo User",
        )


class FirebaseAuth:
    """Future: verify Firebase ID token via firebase-admin and map UID -> user."""

    async def authenticate(self, authorization, demo_user, demo_role) -> AuthIdentity:
        # TODO(firebase): firebase_admin.auth.verify_id_token(token)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="FirebaseAuth not wired yet. Set CIVIKTA_AUTH=stub for local dev.",
        )


def get_auth_provider(settings: Settings = Depends(get_settings)) -> AuthProvider:
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
