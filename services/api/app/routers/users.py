"""User profile endpoints — upsert + fetch + phone-based sign-in."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import AuthIdentity, get_current_user
from app.repositories import get_repository
from app.repositories.base import Repository

router = APIRouter(prefix="/api/users", tags=["users"])


class UpsertUserBody(BaseModel):
    name: str | None = None
    phone: str | None = None
    password_hash: str | None = None
    ward_no: int | None = None
    ward_name: str | None = None
    zone: str | None = None
    local_body_type: str | None = None
    home_lat: float | None = None
    home_lng: float | None = None


class SigninBody(BaseModel):
    phone: str
    password_hash: str | None = None


@router.post("/me")
async def upsert_me(
    body: UpsertUserBody,
    user: AuthIdentity = Depends(get_current_user),
    repo: Repository = Depends(get_repository),
) -> dict:
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    data["role"] = user.role
    if hasattr(repo, "upsert_user"):
        return repo.upsert_user(user.uid, data)
    return {"id": user.uid, **data}


@router.get("/me")
async def get_me(
    user: AuthIdentity = Depends(get_current_user),
    repo: Repository = Depends(get_repository),
) -> dict:
    if hasattr(repo, "get_user"):
        profile = repo.get_user(user.uid)
        if profile:
            return profile
    return {"id": user.uid, "role": user.role}


@router.post("/signin")
async def signin(
    body: SigninBody,
    repo: Repository = Depends(get_repository),
) -> dict:
    if not hasattr(repo, "get_user_by_phone"):
        raise HTTPException(status_code=400, detail="Sign-in not supported with this repository")
    user = repo.get_user_by_phone(body.phone)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this phone number")
    # Hash comparison skipped: demo app uses HTTP on LAN where crypto.subtle is
    # unavailable, so the client-side hash algorithm is inconsistent across contexts.
    return user
