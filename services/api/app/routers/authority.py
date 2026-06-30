"""Authority dashboard endpoints (PRD §31.2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import AuthIdentity, get_current_user
from app.core.deps import Services, get_services
from app.schemas.issue import IssueDetail, IssueSummary, StatusUpdate

router = APIRouter(prefix="/api/authority", tags=["authority"])


@router.get("/issues", response_model=list[IssueSummary], summary="Get the prioritised issue queue for an authority")
async def authority_queue(
    authority: str | None = Query(None, description="authority slug — e.g. mcd, ndmc, djb, pwd, ifcd, dda, police, nhai"),
    status: str | None = Query(None, description="submitted | in_progress | resolved | rejected | reopened"),
    ward_no: int | None = Query(None),
    severity: str | None = Query(None, description="low | medium | high | critical"),
    sort: str = Query("urgency", description="urgency | corroboration | recent"),
    services: Services = Depends(get_services),
) -> list[IssueSummary]:
    """
    Returns the filtered, sorted issue queue for a government authority department.

    **Urgency score** is a composite of: severity weight × corroboration count × SLA deadline proximity.
    Higher score = needs attention sooner.

    Authority slugs: `mcd`, `ndmc`, `dcb`, `djb`, `pwd`, `ifcd`, `dda`, `police`, `nhai`
    """
    return services.authority.queue(authority, status=status, ward_no=ward_no, severity=severity, sort=sort)


@router.get("/issues/{issue_id}", response_model=IssueDetail, summary="Get full issue detail for an authority officer")
async def authority_issue(issue_id: str, services: Services = Depends(get_services)) -> IssueDetail:
    detail = services.authority.get_detail(issue_id)
    if not detail:
        raise HTTPException(404, "issue not found")
    return detail


@router.post("/issues/{issue_id}/status", response_model=IssueDetail, summary="Update issue status (in_progress / resolved / rejected)")
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


@router.get("/escalations", response_model=list[IssueSummary], summary="Get issues that have breached SLA or been disputed by citizens")
async def get_escalations(services: Services = Depends(get_services)) -> list[IssueSummary]:
    """
    Returns issues that require urgent authority attention:
    - **SLA breach**: deadline has passed without resolution
    - **Citizen dispute**: issue was marked resolved but citizens corroborated it as still unresolved
    These appear in the red escalation banner on the authority dashboard.
    """
    return services.authority.get_escalations()
