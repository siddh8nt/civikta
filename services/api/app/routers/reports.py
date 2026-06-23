"""Citizen report intake endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services
from app.pipeline import get_pipeline
from app.pipeline.base import ComplaintPipeline
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.duplicate import DuplicateResult
from app.schemas.report import (
    AnalyzeResult,
    MediaAttach,
    ReportDraftCreate,
    SubmitDecision,
    SubmitResult,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _require_report(services: Services, report_id: str):
    report = services.reports.get(report_id)
    if not report:
        raise HTTPException(404, "report not found")
    return report


@router.post("/draft")
async def create_draft(
    payload: ReportDraftCreate,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    report = services.reports.create_draft(user.uid, payload)
    return {"report_id": report.id}


@router.post("/{report_id}/media")
async def attach_media(
    report_id: str, media: MediaAttach, services: Services = Depends(get_services)
) -> dict:
    _require_report(services, report_id)
    m = services.reports.attach_media(report_id, media)
    return {"media_id": m.id, "storage_url": m.storage_url}


@router.post("/{report_id}/analyze", response_model=AnalyzeResult)
async def analyze(
    report_id: str,
    services: Services = Depends(get_services),
    pipeline: ComplaintPipeline = Depends(get_pipeline),
) -> AnalyzeResult:
    report = _require_report(services, report_id)
    return await pipeline.analyze(report)


@router.post("/{report_id}/check-duplicate", response_model=DuplicateResult)
async def check_duplicate(
    report_id: str, services: Services = Depends(get_services)
) -> DuplicateResult:
    report = _require_report(services, report_id)
    analysis = (
        ComplaintAnalysis(**report.ai_raw)
        if report.ai_raw
        else await services.ai_triage.analyze(ComplaintAnalysisInput(text=report.raw_description))
    )
    return await services.duplicates.find_duplicates(analysis, report.latitude, report.longitude)


@router.post("/{report_id}/submit", response_model=SubmitResult)
async def submit(
    report_id: str,
    decision: SubmitDecision,
    services: Services = Depends(get_services),
    pipeline: ComplaintPipeline = Depends(get_pipeline),
) -> SubmitResult:
    report = _require_report(services, report_id)
    return await pipeline.submit(report, decision)


@router.get("/mine")
async def my_reports(
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> list:
    return services.repo.list_reports_by_user(user.uid)
