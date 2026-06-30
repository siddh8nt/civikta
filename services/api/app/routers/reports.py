"""Citizen report intake endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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


class _ValidateImagesBody(BaseModel):
    image_data: list[str]


@router.post("/validate-images", summary="Validate issue photos with Gemini Vision")
async def validate_images(
    payload: _ValidateImagesBody,
    services: Services = Depends(get_services),
) -> dict:
    """
    Accepts base64-encoded images and runs them through **Gemini Vision** to check:
    - Image is clear and relevant (not blurry, not a selfie, not irrelevant)
    - At least one image shows a civic infrastructure problem
    - Returns a quality score and pass/fail per image

    Called by the citizen app before allowing the user to proceed to draft creation.
    """
    return await services.llm.validate_images(payload.image_data)


@router.post("/draft", summary="Create a new issue draft")
async def create_draft(
    payload: ReportDraftCreate,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    report = services.reports.create_draft(user.uid, payload)
    return {"report_id": report.id}


@router.post("/{report_id}/media", summary="Attach a photo or video to the draft")
async def attach_media(
    report_id: str, media: MediaAttach, services: Services = Depends(get_services)
) -> dict:
    _require_report(services, report_id)
    m = services.reports.attach_media(report_id, media)
    return {"media_id": m.id, "storage_url": m.storage_url}


@router.post("/{report_id}/analyze", response_model=AnalyzeResult, summary="Run Gemini AI analysis on the draft")
async def analyze(
    report_id: str,
    services: Services = Depends(get_services),
    pipeline: ComplaintPipeline = Depends(get_pipeline),
) -> AnalyzeResult:
    """
    Runs the **Gemini AI triage pipeline** on the draft report:
    - Classifies issue type (pothole, sewage, streetlight, encroachment, etc.)
    - Assigns severity: `low | medium | high | critical`
    - Extracts structured metadata (affected area, estimated impact radius)
    - Determines the correct authority slug for routing (e.g. `mcd`, `djb`, `pwd`)
    - Computes initial urgency score

    This is the core AI step. Results are stored on the draft for the duplicate check and submission steps.
    """
    report = _require_report(services, report_id)
    return await pipeline.analyze(report)


@router.post("/{report_id}/check-duplicate", response_model=DuplicateResult, summary="Check for existing duplicate issues nearby")
async def check_duplicate(
    report_id: str, services: Services = Depends(get_services)
) -> DuplicateResult:
    """
    Searches for existing issues within proximity that match the same type and description.
    Uses Gemini embeddings + geospatial filtering to find semantic duplicates.
    Returns `is_duplicate`, a confidence score, and the matched issue ID if found.
    If a duplicate is found, the citizen is offered to **corroborate** the existing report instead of filing a new one.
    """
    report = _require_report(services, report_id)
    analysis = (
        ComplaintAnalysis(**report.ai_raw)
        if report.ai_raw
        else await services.ai_triage.analyze(ComplaintAnalysisInput(text=report.raw_description))
    )
    return await services.duplicates.find_duplicates(analysis, report.latitude, report.longitude)


@router.post("/{report_id}/submit", response_model=SubmitResult, summary="Submit the report and route it to the responsible authority")
async def submit(
    report_id: str,
    decision: SubmitDecision,
    services: Services = Depends(get_services),
    pipeline: ComplaintPipeline = Depends(get_pipeline),
) -> SubmitResult:
    """
    Final submission step. Converts the draft into a live issue:
    1. Confirms authority routing (from the AI analysis step)
    2. Sets SLA deadline based on authority and severity
    3. Persists the issue to Supabase with full metadata
    4. Issue becomes visible in the authority's dashboard queue and the citizen feed

    `decision` can include `corroborate_existing_id` to merge with a duplicate instead of creating a new issue.
    """
    report = _require_report(services, report_id)
    return await pipeline.submit(report, decision)


@router.get("/mine", summary="List all issues filed by the current citizen")
async def my_reports(
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> list:
    return services.repo.list_reports_by_user(user.uid)
