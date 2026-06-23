"""Authority master record. Mirrors the `authorities` table."""

from __future__ import annotations

from pydantic import BaseModel


class AuthorityRecord(BaseModel):
    slug: str
    authority_name: str
    department_name: str | None = None
    authority_family: str
    local_body_scope: str | None = None
