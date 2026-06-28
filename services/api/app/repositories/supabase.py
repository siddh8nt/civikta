"""Supabase repository — full implementation.

Implements the Repository protocol against Supabase Postgres via postgrest-py.
Spatial queries (issues_near, issues_in_viewport) use bounding-box pre-filter
in SQL + precise haversine in Python — no PostGIS extension required.
Upgrade path: add `location geography(Point,4326)` column + ST_DWithin RPC.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import uuid
from datetime import datetime
from typing import Any

from supabase import Client, create_client

from app.core.config import Settings
from app.core.geoutil import haversine_m
from app.models.authority import AuthorityRecord
from app.models.issue import IssueEventRecord, IssueRecord
from app.models.issue_report import IssueMediaRecord, IssueReportRecord
from app.models.routing_rule import RoutingRuleRecord


def _clean(d: dict) -> dict:
    """Remove fields that must not be sent to the DB (in-memory-only / too large)."""
    d.pop("image_data", None)
    d.pop("summary_embedding", None)
    # Remove None values so we don't overwrite existing DB fields with NULL on partial updates
    return {k: v for k, v in d.items() if v is not None}


def _dump(model) -> dict:
    """Pydantic model → DB-safe dict (datetimes serialised, junk stripped)."""
    return _clean(model.model_dump(mode="json"))


class SupabaseRepository:
    def __init__(self, settings: Settings) -> None:
        if not (settings.supabase_url and settings.supabase_service_key):
            raise RuntimeError(
                "CIVIKTA_REPO=supabase requires SUPABASE_URL and SUPABASE_SERVICE_KEY in .env"
            )
        self._client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
        self._bucket = settings.supabase_storage_bucket
        self._seeded = False

    # ── Issues ────────────────────────────────────────────────────────────────

    def add_issue(self, issue: IssueRecord) -> IssueRecord:
        self._client.table("issues").insert(_dump(issue)).execute()
        return issue

    def get_issue(self, issue_id: str) -> IssueRecord | None:
        res = self._client.table("issues").select("*").eq("id", issue_id).maybe_single().execute()
        if res.data:
            return IssueRecord(**res.data)
        # Prefix/short-code lookup (CIV-XXXXXXXX → first 8 chars)
        res2 = self._client.table("issues").select("*").ilike("id", f"{issue_id}%").limit(1).execute()
        return IssueRecord(**res2.data[0]) if res2.data else None

    def update_issue(self, issue: IssueRecord) -> IssueRecord:
        data = _dump(issue)
        data.pop("id", None)
        data.pop("created_at", None)
        self._client.table("issues").update(data).eq("id", issue.id).execute()
        return issue

    def list_issues(
        self,
        *,
        statuses: list[str] | None = None,
        primary_authority_slug: str | None = None,
        ward_no: int | None = None,
        issue_type_slug: str | None = None,
    ) -> list[IssueRecord]:
        q = self._client.table("issues").select("*")
        if statuses:
            q = q.in_("status", statuses)
        if primary_authority_slug:
            q = q.eq("primary_authority_slug", primary_authority_slug)
        if ward_no is not None:
            q = q.eq("ward_no", ward_no)
        if issue_type_slug:
            q = q.eq("issue_type_slug", issue_type_slug)
        res = q.order("created_at", desc=True).execute()
        return [IssueRecord(**r) for r in res.data]

    def issues_near(
        self,
        lat: float,
        lng: float,
        radius_m: float,
        *,
        statuses: list[str] | None = None,
        issue_type_slug: str | None = None,
    ) -> list[tuple[IssueRecord, float]]:
        # Bounding box pre-filter (1° ≈ 111 km)
        pad = radius_m / 111_000
        q = (
            self._client.table("issues")
            .select("*")
            .gte("latitude", lat - pad)
            .lte("latitude", lat + pad)
            .gte("longitude", lng - pad)
            .lte("longitude", lng + pad)
        )
        if statuses:
            q = q.in_("status", statuses)
        if issue_type_slug:
            q = q.eq("issue_type_slug", issue_type_slug)
        res = q.execute()

        out: list[tuple[IssueRecord, float]] = []
        for row in res.data:
            if row.get("latitude") is None or row.get("longitude") is None:
                continue
            dist = haversine_m(lat, lng, row["latitude"], row["longitude"])
            if dist <= radius_m:
                out.append((IssueRecord(**row), dist))
        return sorted(out, key=lambda t: t[1])

    def issues_in_viewport(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float,
        *,
        statuses: list[str] | None = None,
        issue_category_slug: str | None = None,
    ) -> list[IssueRecord]:
        q = (
            self._client.table("issues")
            .select("*")
            .gte("latitude", min_lat)
            .lte("latitude", max_lat)
            .gte("longitude", min_lng)
            .lte("longitude", max_lng)
        )
        if statuses:
            q = q.in_("status", statuses)
        if issue_category_slug:
            q = q.eq("issue_category_slug", issue_category_slug)
        res = q.execute()
        return [IssueRecord(**r) for r in res.data]

    # ── Reports ───────────────────────────────────────────────────────────────

    def add_report(self, report: IssueReportRecord) -> IssueReportRecord:
        self._client.table("issue_reports").insert(_dump(report)).execute()
        return report

    def get_report(self, report_id: str) -> IssueReportRecord | None:
        res = self._client.table("issue_reports").select("*").eq("id", report_id).maybe_single().execute()
        return IssueReportRecord(**res.data) if res.data else None

    def update_report(self, report: IssueReportRecord) -> IssueReportRecord:
        data = _dump(report)
        data.pop("id", None)
        data.pop("created_at", None)
        self._client.table("issue_reports").update(data).eq("id", report.id).execute()
        return report

    def list_reports_by_user(self, user_id: str) -> list[IssueReportRecord]:
        res = (
            self._client.table("issue_reports")
            .select("*")
            .eq("created_by", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [IssueReportRecord(**r) for r in res.data]

    def list_reports_for_issue(self, issue_id: str) -> list[IssueReportRecord]:
        issue = self.get_issue(issue_id)
        original_report_id = issue.original_report_id if issue else None

        filter_str = f"merged_into_issue_id.eq.{issue_id}"
        if original_report_id:
            filter_str += f",id.eq.{original_report_id}"

        res = (
            self._client.table("issue_reports")
            .select("*")
            .or_(filter_str)
            .order("created_at")
            .execute()
        )
        return [IssueReportRecord(**r) for r in res.data]

    # ── Media ─────────────────────────────────────────────────────────────────

    def add_media(self, media: IssueMediaRecord) -> IssueMediaRecord:
        self._client.table("issue_media").insert(_dump(media)).execute()
        return media

    def list_media_for_report(self, report_id: str) -> list[IssueMediaRecord]:
        res = self._client.table("issue_media").select("*").eq("report_id", report_id).execute()
        return [IssueMediaRecord(**r) for r in res.data]

    def list_media_for_issue(self, issue_id: str) -> list[IssueMediaRecord]:
        issue = self.get_issue(issue_id)
        original_report_id = issue.original_report_id if issue else None

        filter_str = f"merged_into_issue_id.eq.{issue_id}"
        if original_report_id:
            filter_str += f",id.eq.{original_report_id}"

        reports_res = (
            self._client.table("issue_reports")
            .select("id")
            .or_(filter_str)
            .execute()
        )
        report_ids = [r["id"] for r in reports_res.data]
        if not report_ids:
            return []
        res = self._client.table("issue_media").select("*").in_("report_id", report_ids).execute()
        return [IssueMediaRecord(**r) for r in res.data]

    def upload_image_data(self, data_url: str, path: str) -> str:
        """Upload a base64 data URL to Supabase Storage; return the public URL."""
        try:
            header, b64 = data_url.split(",", 1)
            # header looks like "data:image/jpeg;base64"
            mime = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
            ext = mimetypes.guess_extension(mime) or ".jpg"
            if ext == ".jpe":
                ext = ".jpg"
        except Exception:
            b64 = data_url
            mime = "image/jpeg"
            ext = ".jpg"

        file_bytes = base64.b64decode(b64)
        file_path = f"{path}{ext}" if not path.endswith(ext) else path

        self._client.storage.from_(self._bucket).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": mime, "upsert": "true"},
        )
        return self._client.storage.from_(self._bucket).get_public_url(file_path)

    # ── Events ────────────────────────────────────────────────────────────────

    def add_event(self, event: IssueEventRecord) -> IssueEventRecord:
        self._client.table("issue_events").insert(_dump(event)).execute()
        return event

    def list_events(self, issue_id: str) -> list[IssueEventRecord]:
        res = (
            self._client.table("issue_events")
            .select("*")
            .eq("issue_id", issue_id)
            .order("created_at")
            .execute()
        )
        return [IssueEventRecord(**r) for r in res.data]

    # ── Reference ─────────────────────────────────────────────────────────────

    def list_authorities(self) -> list[AuthorityRecord]:
        res = self._client.table("authorities").select("*").execute()
        return [AuthorityRecord(**r) for r in res.data]

    def get_authority(self, slug: str) -> AuthorityRecord | None:
        res = self._client.table("authorities").select("*").eq("slug", slug).maybe_single().execute()
        return AuthorityRecord(**res.data) if res.data else None

    def list_routing_rules(self) -> list[RoutingRuleRecord]:
        res = self._client.table("routing_rules").select("*").execute()
        return [RoutingRuleRecord(**r) for r in res.data]

    # ── Users ─────────────────────────────────────────────────────────────────

    def upsert_user(self, user_id: str, data: dict) -> dict:
        data["id"] = user_id
        data["updated_at"] = datetime.utcnow().isoformat()
        res = (
            self._client.table("users")
            .upsert(data, on_conflict="id")
            .execute()
        )
        return res.data[0] if res.data else data

    def get_user(self, user_id: str) -> dict | None:
        res = self._client.table("users").select("*").eq("id", user_id).limit(1).execute()
        return res.data[0] if res.data else None

    def get_user_by_phone(self, phone: str) -> dict | None:
        res = self._client.table("users").select("*").eq("phone", phone).limit(1).execute()
        return res.data[0] if res.data else None

    # ── Seeding ───────────────────────────────────────────────────────────────

    def seed_demo(self) -> None:
        """No-op for Supabase — seed via 02_seed_demo.sql in Supabase SQL editor."""
        pass
