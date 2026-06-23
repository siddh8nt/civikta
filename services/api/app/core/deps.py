"""Dependency container. Assembles every service from the repo + llm seams.

Both the FastAPI routers and the pipeline build on this, so there is exactly one
place that wires dependencies together.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.llm import get_llm_client
from app.llm.base import LLMClient
from app.repositories import get_repository
from app.repositories.base import Repository
from app.services.ai_triage_service import AITriageService
from app.services.authority_service import AuthorityService
from app.services.corroboration_service import CorroborationService
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.services.feed_service import FeedService
from app.services.geo_service import GeoService
from app.services.issue_service import IssueService
from app.services.oversight_service import OversightService
from app.services.report_service import ReportService
from app.services.routing_service import RoutingService
from app.services.urgency_score_service import UrgencyScoreService


@dataclass
class Services:
    repo: Repository
    llm: LLMClient
    ai_triage: AITriageService
    geo: GeoService
    routing: RoutingService
    urgency: UrgencyScoreService
    duplicates: DuplicateDetectionService
    reports: ReportService
    issues: IssueService
    corroboration: CorroborationService
    feed: FeedService
    authority: AuthorityService
    oversight: OversightService


@lru_cache
def get_services() -> Services:
    repo = get_repository()
    llm = get_llm_client()

    urgency = UrgencyScoreService()
    geo = GeoService()
    routing = RoutingService(repo)
    ai_triage = AITriageService(llm)
    duplicates = DuplicateDetectionService(repo, llm)
    reports = ReportService(repo)
    issues = IssueService(repo, urgency, llm)
    corroboration = CorroborationService(repo, urgency)
    feed = FeedService(repo, issues)
    authority = AuthorityService(repo, issues)
    oversight = OversightService(repo, llm)

    return Services(
        repo=repo, llm=llm, ai_triage=ai_triage, geo=geo, routing=routing,
        urgency=urgency, duplicates=duplicates, reports=reports, issues=issues,
        corroboration=corroboration, feed=feed, authority=authority, oversight=oversight,
    )
