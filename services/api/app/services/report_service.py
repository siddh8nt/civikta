"""Report service — the raw citizen-submission layer (PRD §6, §8.4)."""

from __future__ import annotations

from app.models.issue_report import IssueMediaRecord, IssueReportRecord
from app.repositories.base import Repository
from app.schemas.ai import ComplaintAnalysis
from app.schemas.report import MediaAttach, ReportDraftCreate


class ReportService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def create_draft(self, user_id: str, payload: ReportDraftCreate) -> IssueReportRecord:
        report = IssueReportRecord(
            created_by=user_id,
            raw_title=payload.raw_title,
            raw_description=payload.raw_description,
            latitude=payload.latitude,
            longitude=payload.longitude,
            merge_decision="pending",
        )
        self.repo.add_report(report)
        for url in payload.media_urls:
            self.repo.add_media(IssueMediaRecord(report_id=report.id, storage_url=url))
        return report

    def attach_media(self, report_id: str, media: MediaAttach) -> IssueMediaRecord:
        return self.repo.add_media(IssueMediaRecord(
            report_id=report_id, media_type=media.media_type,
            storage_url=media.storage_url, thumbnail_url=media.thumbnail_url,
        ))

    def apply_analysis(self, report: IssueReportRecord,
                       analysis: ComplaintAnalysis) -> IssueReportRecord:
        report.issue_category_slug = analysis.issue_category
        report.issue_type_slug = analysis.issue_type
        report.asset_type_slug = analysis.asset_type
        report.ai_summary = analysis.summary
        report.ai_confidence = analysis.confidence
        report.ai_raw = analysis.model_dump()
        return self.repo.update_report(report)

    def get(self, report_id: str) -> IssueReportRecord | None:
        return self.repo.get_report(report_id)
