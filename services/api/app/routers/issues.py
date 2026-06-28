"""Public issue endpoints (PRD §31.1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services
from app.schemas.issue import IssueDetail
from app.schemas.report import CorroborateRequest

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/{issue_id}", response_model=IssueDetail)
async def get_issue(issue_id: str, services: Services = Depends(get_services)) -> IssueDetail:
    detail = services.issues.get_detail(issue_id)
    if not detail:
        raise HTTPException(404, "issue not found")
    return detail


@router.post("/{issue_id}/request-escalation")
async def request_escalation(
    issue_id: str,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    ok = services.issues.request_escalation(issue_id, user.uid)
    if not ok:
        raise HTTPException(404, "issue not found")
    return {"status": "escalation_requested"}


@router.post("/{issue_id}/corroborate")
async def corroborate(
    issue_id: str,
    req: CorroborateRequest,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> dict:
    """Public actions: 'I'm affected too' / 'still unresolved' / add evidence."""
    issue = services.corroboration.public_corroborate(issue_id, user.uid, req)
    if not issue:
        raise HTTPException(404, "issue not found")
    return {
        "issue_id": issue.id,
        "corroboration_count": issue.corroboration_count,
        "urgency_score": issue.urgency_score,
    }
