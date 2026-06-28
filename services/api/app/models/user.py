from __future__ import annotations
from pydantic import BaseModel


class UserRecord(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    role: str = "citizen"
    ward_no: int | None = None
    ward_name: str | None = None
    zone: str | None = None
    local_body_type: str | None = None
    home_lat: float | None = None
    home_lng: float | None = None
    authority_slug: str | None = None
    is_demo: bool = False
