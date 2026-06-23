"""Demo issues so the feed / map / dashboards are non-empty on first run.

Each entry returns (issue, original_report, media, events). Coordinates are real
Delhi localities. Includes a heavily-corroborated issue and a reopened (false
closure) issue for the oversight story.
"""

from __future__ import annotations

from datetime import timedelta

from app.models.issue import IssueEventRecord, IssueRecord, _now
from app.models.issue_report import IssueMediaRecord, IssueReportRecord


def _img(seed: str) -> str:
    return f"https://picsum.photos/seed/{seed}/800/600"


def build_demo_issues():
    now = _now()
    out = []

    def make(issue: IssueRecord, *, desc: str, media_seeds: list[str],
             extra_events: list[tuple[str, str, dict]] | None = None):
        report = IssueReportRecord(
            id=issue.original_report_id,
            created_by=issue.created_by,
            raw_description=desc,
            latitude=issue.latitude,
            longitude=issue.longitude,
            issue_category_slug=issue.issue_category_slug,
            issue_type_slug=issue.issue_type_slug,
            asset_type_slug=issue.asset_type_slug,
            ai_summary=issue.ai_summary,
            ai_confidence=issue.ai_confidence,
            report_role="original",
            created_at=issue.created_at,
        )
        media = [
            IssueMediaRecord(report_id=report.id, storage_url=_img(s), created_at=issue.created_at)
            for s in media_seeds
        ]
        events = [
            IssueEventRecord(issue_id=issue.id, actor_type="citizen", event_type="created",
                             created_at=issue.created_at),
            IssueEventRecord(issue_id=issue.id, actor_type="system", event_type="classified",
                             created_at=issue.created_at + timedelta(seconds=5)),
            IssueEventRecord(issue_id=issue.id, actor_type="system", event_type="assigned",
                             payload={"authority": issue.primary_authority_slug},
                             created_at=issue.created_at + timedelta(seconds=8)),
        ]
        for et, actor, payload in (extra_events or []):
            events.append(IssueEventRecord(issue_id=issue.id, actor_type=actor, event_type=et,
                                           payload=payload, created_at=now))
        out.append((issue, report, media, events))

    # 1) Heavily corroborated sewer overflow — Lajpat Nagar II (MCD, South Delhi)
    i1 = IssueRecord(
        original_report_id="seed-r1", created_by="seed-citizen-1",
        title="Sewer overflow blocking lane near Lajpat Nagar II market",
        public_summary="Sewage overflowing from a choked sewer line, flooding the lane and creating a health hazard.",
        ai_summary="Likely sewer line choke causing overflow into a residential lane.",
        ai_confidence=0.88, status="in_progress",
        latitude=28.5677, longitude=77.2433,
        local_body_type="MCD", ward_no=42, ward_name="Lajpat Nagar", locality_name="Lajpat Nagar II",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="high", urgency_score=8.5,
        corroboration_count=7, total_report_count=8, total_evidence_count=9,
        last_corroborated_at=now - timedelta(hours=3),
        health_hazard_flag=True, drain_type="sewer",
        primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
        routing_confidence=0.95, routing_reason={"rule": "sewer->djb"},
        created_at=now - timedelta(days=3),
    )
    make(i1, desc="Sewage all over the lane for 3 days, terrible smell.",
         media_seeds=["sewer1", "sewer2"],
         extra_events=[("issue_corroborated", "citizen", {"count": 7}),
                       ("urgency_score_updated", "system", {"urgency_score": 8.5})])

    # 2) Pothole on major road — Ring Road (PWD)
    i2 = IssueRecord(
        original_report_id="seed-r2", created_by="seed-citizen-2",
        title="Large pothole on Ring Road near Moolchand",
        public_summary="Deep pothole on the arterial corridor, risk to two-wheelers.",
        ai_summary="Pothole on an arterial road; PWD jurisdiction.",
        ai_confidence=0.82, status="assigned",
        latitude=28.5700, longitude=77.2350,
        local_body_type="MCD", ward_no=42, ward_name="Lajpat Nagar", locality_name="Moolchand",
        issue_category_slug="roads_streets", issue_type_slug="pothole_major_road",
        asset_type_slug="arterial_road", severity="medium", urgency_score=3.0,
        corroboration_count=1, total_report_count=2, total_evidence_count=2,
        road_class="arterial", public_safety_flag=True,
        primary_authority_slug="pwd", routing_confidence=0.9,
        created_at=now - timedelta(days=1, hours=4),
    )
    make(i2, desc="Big pothole, almost fell off my scooter.", media_seeds=["pothole1"])

    # 3) Garbage not collected — Karol Bagh (MCD sanitation)
    i3 = IssueRecord(
        original_report_id="seed-r3", created_by="seed-citizen-3",
        title="Garbage not collected for a week — Karol Bagh",
        public_summary="Community bin overflowing, garbage spilling onto the road.",
        ai_summary="Garbage not collected; overflowing community bin.",
        ai_confidence=0.9, status="submitted",
        latitude=28.6519, longitude=77.1909,
        local_body_type="MCD", ward_no=76, ward_name="Karol Bagh", locality_name="Karol Bagh",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="medium", urgency_score=2.5,
        corroboration_count=2, total_report_count=3, total_evidence_count=3,
        last_corroborated_at=now - timedelta(hours=20),
        primary_authority_slug="mcd_sanitation", routing_confidence=0.9,
        created_at=now - timedelta(days=2),
    )
    make(i3, desc="Bin overflowing for days, stray dogs everywhere.", media_seeds=["garbage1"])

    # 4) Streetlight — Rohini — resolved then REOPENED (false closure story)
    i4 = IssueRecord(
        original_report_id="seed-r4", created_by="seed-citizen-4",
        title="Streetlight not working — Rohini Sector 7",
        public_summary="Dark stretch at night; streetlight marked fixed but still off.",
        ai_summary="Streetlight outage on a residential stretch.",
        ai_confidence=0.78, status="reopened",
        latitude=28.7050, longitude=77.1180,
        local_body_type="MCD", ward_no=24, ward_name="Rohini", locality_name="Rohini Sector 7",
        issue_category_slug="lights_electrical", issue_type_slug="streetlight_not_working",
        severity="low", urgency_score=2.0,
        corroboration_count=3, total_report_count=4, total_evidence_count=2,
        last_corroborated_at=now - timedelta(hours=6),
        primary_authority_slug="mcd_engineering", routing_confidence=0.8,
        created_at=now - timedelta(days=9),
    )
    make(i4, desc="Whole street pitch dark, unsafe for women at night.",
         media_seeds=["light1"],
         extra_events=[("resolved", "authority", {"note": "Marked fixed"}),
                       ("reopened", "citizen", {"note": "Still not working"}),
                       ("still_unresolved_confirmed", "citizen", {"count": 3})])

    # 5) Waterlogging — Dwarka (PWD + IFCD)
    i5 = IssueRecord(
        original_report_id="seed-r5", created_by="seed-citizen-5",
        title="Waterlogging on main road — Dwarka Sector 10",
        public_summary="Knee-deep waterlogging after rain, traffic blocked.",
        ai_summary="Corridor waterlogging, likely drain overflow.",
        ai_confidence=0.8, status="submitted",
        latitude=28.5823, longitude=77.0500,
        local_body_type="MCD", ward_no=127, ward_name="Dwarka", locality_name="Dwarka Sector 10",
        issue_category_slug="water_sewer_drainage", issue_type_slug="waterlogging",
        asset_type_slug="roadside_storm_drain", severity="high", urgency_score=5.0,
        corroboration_count=4, total_report_count=5, total_evidence_count=4,
        last_corroborated_at=now - timedelta(hours=2),
        road_class="arterial", obstruction_flag=True,
        primary_authority_slug="pwd", secondary_authority_slug="ifcd", routing_confidence=0.85,
        created_at=now - timedelta(hours=10),
    )
    make(i5, desc="Road completely flooded, cars stuck.", media_seeds=["water1", "water2"])

    return out
