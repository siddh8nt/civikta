"""Public issue endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services
from app.schemas.issue import IssueDetail
from app.schemas.report import CorroborateRequest

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/{issue_id}", response_model=IssueDetail, summary="Get full issue detail including AI analysis and media")
async def get_issue(issue_id: str, services: Services = Depends(get_services)) -> IssueDetail:
    detail = services.issues.get_detail(issue_id)
    if not detail:
        raise HTTPException(404, "issue not found")
    return detail


@router.post("/{issue_id}/request-escalation", summary="Citizen requests escalation when SLA is breached or resolution is disputed")
async def request_escalation(
    issue_id: str,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    ok = services.issues.request_escalation(issue_id, user.uid)
    if not ok:
        raise HTTPException(404, "issue not found")
    return {"status": "escalation_requested"}


@router.post("/{issue_id}/corroborate", summary="Corroborate an existing issue ('I'm affected too' / add evidence)")
async def corroborate(
    issue_id: str,
    req: CorroborateRequest,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    """
    Allows citizens to strengthen an existing report rather than filing a duplicate.
    Corroboration types:
    - **`affected`** — "I'm affected by this too" — increases corroboration count and urgency score
    - **`still_unresolved`** — "This was marked resolved but is still broken" — triggers re-open + escalation
    - **`evidence`** — attaches additional photos to the existing issue

    Each corroboration increases the **urgency score**, pushing the issue higher in the authority's queue.
    Returns the updated corroboration count and urgency score.
    """
    issue = services.corroboration.public_corroborate(issue_id, user.uid, req)
    if not issue:
        raise HTTPException(404, "issue not found")
    return {
        "issue_id": issue.id,
        "corroboration_count": issue.corroboration_count,
        "urgency_score": issue.urgency_score,
    }
