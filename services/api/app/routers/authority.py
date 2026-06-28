"""Authority dashboard endpoints (PRD §31.2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services
from app.schemas.issue import IssueDetail, IssueSummary, StatusUpdate

router = APIRouter(prefix="/api/authority", tags=["authority"])


@router.get("/issues", response_model=list[IssueSummary])
async def authority_queue(
    authority: str | None = Query(None, description="authority slug"),
    status: str | None = Query(None),
    ward_no: int | None = Query(None),
    severity: str | None = Query(None, description="low | medium | high | critical"),
    sort: str = Query("urgency", description="urgency | corroboration | recent"),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    return services.authority.queue(authority, status=status, ward_no=ward_no, severity=severity, sort=sort)


@router.get("/issues/{issue_id}", response_model=IssueDetail)
async def authority_issue(issue_id: str, services: Services = Depends(get_services)) -> IssueDetail:
    detail = services.authority.get_detail(issue_id)
    if not detail:
        raise HTTPException(404, "issue not found")
    return detail


@router.post("/issues/{issue_id}/status", response_model=IssueDetail)
async def update_status(
    issue_id: str,
    update: StatusUpdate,
    user: AuthIdentity = Depends(get_current_user),
    services: Services = Depends(get_services),
) -> IssueDetail:
    detail = services.authority.update_status(issue_id, update, actor_id=user.uid)
    if not detail:
        raise HTTPException(404, "issue not found")
    return detail


@router.get("/escalations", response_model=list[IssueSummary])
async def get_escalations(services: Services = Depends(get_services)) -> list[IssueSummary]:
    """Issues that have breached their deadline or have mass false-resolution disputes."""
    return services.authority.get_escalations()
