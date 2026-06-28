"""Demo issues — comprehensive Delhi dataset for the feed / map / dashboards.

60 issues across 30+ wards covering all major Delhi districts.
Realistic statuses, corroboration counts, severity mix, and real civic edge cases.
"""

from __future__ import annotations

from datetime import timedelta

from app.models.issue import IssueEventRecord, IssueRecord, _now
from app.models.issue_report import IssueMediaRecord, IssueReportRecord

# ── Category image banks — verified Wikimedia Commons images ──────────────

_I = {
    "pothole": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Potholes_on_road.jpg/960px-Potholes_on_road.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Potholed_road_outside_Kolkata_Airport.jpg/960px-Potholed_road_outside_Kolkata_Airport.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Driving_through_potholes.jpg/960px-Driving_through_potholes.jpg",
    ],
    "sewer": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Open_sewer_%282731597018%29.jpg/960px-Open_sewer_%282731597018%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Measuring_PM2.5_air_pollution_from_a_burning_roadside_garbage_dump_at_Bhiwandi_near_Mumbai.jpg/960px-Measuring_PM2.5_air_pollution_from_a_burning_roadside_garbage_dump_at_Bhiwandi_near_Mumbai.jpg",
    ],
    "waterlog": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Morogoro_road_B129_flooded_%281%29_01.jpg/960px-Morogoro_road_B129_flooded_%281%29_01.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Morogoro_road_B129_flooded_%282%29.jpg/960px-Morogoro_road_B129_flooded_%282%29.jpg",
    ],
    "garbage": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/A_burning_roadside_garbage_dump_at_Panvel_Naka_near_Mumbai.jpg/960px-A_burning_roadside_garbage_dump_at_Panvel_Naka_near_Mumbai.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/India_-_Sights_%26_Culture_-_Common_garbage_dump_outside_a_temple_%282566331277%29.jpg/960px-India_-_Sights_%26_Culture_-_Common_garbage_dump_outside_a_temple_%282566331277%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Measuring_PM2.5_air_pollution_from_a_burning_roadside_garbage_dump_at_Bhiwandi_near_Mumbai.jpg/960px-Measuring_PM2.5_air_pollution_from_a_burning_roadside_garbage_dump_at_Bhiwandi_near_Mumbai.jpg",
    ],
    "streetlight": [
        "https://upload.wikimedia.org/wikipedia/commons/e/e2/India-5144_-_Flickr_-_archer10_%28Dennis%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Potholes_on_road.jpg/960px-Potholes_on_road.jpg",
    ],
    "footpath": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Potholed_road_outside_Kolkata_Airport.jpg/960px-Potholed_road_outside_Kolkata_Airport.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Driving_through_potholes.jpg/960px-Driving_through_potholes.jpg",
    ],
    "tree": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Fallen_Tree_in_Dormer_Place%2C_Leamington_Spa_%281%29.jpg/960px-Fallen_Tree_in_Dormer_Place%2C_Leamington_Spa_%281%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7f/Storm_Tree_Fallen_-_geograph.org.uk_-_318190.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Fallen_tree_%2823732226750%29.jpg/960px-Fallen_tree_%2823732226750%29.jpg",
    ],
    "water_supply": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Overhead_water_tank_rural_Raichur_Karnataka_India_water_tower.jpg/960px-Overhead_water_tank_rural_Raichur_Karnataka_India_water_tower.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Water_supply_by_Firemen_after_Cyclone_Fani.jpg/960px-Water_supply_by_Firemen_after_Cyclone_Fani.jpg",
    ],
    "stray_dog": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Stray_dog_in_the_streets_of_Pune.jpg/960px-Stray_dog_in_the_streets_of_Pune.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Stray_Dog_-_Kolkata_05907.JPG/960px-Stray_Dog_-_Kolkata_05907.JPG",
    ],
    "encroach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/India_-_Sights_%26_Culture_-_Common_garbage_dump_outside_a_temple_%282566331277%29.jpg/960px-India_-_Sights_%26_Culture_-_Common_garbage_dump_outside_a_temple_%282566331277%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/e/e2/India-5144_-_Flickr_-_archer10_%28Dennis%29.jpg",
    ],
    "dead_animal": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Dead_animal_on_Rozoda_road.jpg/960px-Dead_animal_on_Rozoda_road.jpg",
    ],
    "contaminated": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/India_-_Rural_-_03_-_drinking_water_and_waste_water_meet_on_the_street_%282564575360%29.jpg/960px-India_-_Rural_-_03_-_drinking_water_and_waste_water_meet_on_the_street_%282564575360%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/India_-_Rural_-_02_-_water_source_%282563743107%29.jpg/960px-India_-_Rural_-_02_-_water_source_%282563743107%29.jpg",
    ],
}


def _imgs(*keys: str) -> list[str]:
    out = []
    for k in keys:
        out.extend(_I.get(k, [])[:2])
    return out[:3]


def build_demo_issues():
    now = _now()
    out = []

    def make(issue: IssueRecord, *, desc: str, imgs: list[str],
             extra_events: list[tuple[str, str, dict]] | None = None):
        if imgs:
            issue.cover_media_url = imgs[0]
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
            merged_into_issue_id=issue.id,
            merge_decision="forced_new",
            created_at=issue.created_at,
        )
        media = [
            IssueMediaRecord(report_id=report.id, storage_url=url, created_at=issue.created_at)
            for url in imgs
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
            events.append(IssueEventRecord(issue_id=issue.id, actor_type=actor,
                                           event_type=et, payload=payload,
                                           created_at=now))
        out.append((issue, report, media, events))

    # ════════════════════════════════════════════════════
    # TEST ISSUE — exercises every UI component
    # ward_name="__TEST__" so the frontend can filter to only this
    # ════════════════════════════════════════════════════
    make(IssueRecord(
        original_report_id="seed-test-r1", created_by="seed-u-test",
        title="Collapsed sewer line flooding entire lane — health emergency for 200+ residents",
        public_summary=(
            "A major underground sewer pipe has burst on the main service lane near Block E, "
            "Lajpat Nagar II. Raw sewage is overflowing, waterlogging the lane and entering "
            "ground-floor homes. 200+ residents cannot leave their homes safely. Children and "
            "elderly are at immediate risk of cholera and dengue. Road is completely obstructed. "
            "Three repair attempts in the past 4 days have failed to seal the burst."
        ),
        ai_summary=(
            "Critical sewer collapse causing simultaneous waterlogging, road obstruction, and "
            "health hazard. DJB is the primary authority; MCD Sanitation coordinates debris "
            "removal. Urgency elevated after citizen re-corroboration confirmed active overflow."
        ),
        ai_confidence=0.97,
        status="in_progress",
        severity="critical",
        latitude=28.5677, longitude=77.2433,
        local_body_type="MCD",
        ward_no=42, ward_name="__TEST__",
        locality_name="Lajpat Nagar II",
        issue_category_slug="water_sewer_drainage",
        issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line",
        drain_type="underground_sewer",
        health_hazard_flag=True,
        obstruction_flag=True,
        public_safety_flag=True,
        primary_authority_slug="djb",
        secondary_authority_slug="mcd_sanitation",
        routing_confidence=0.95,
        routing_reason={"primary": "DJB owns underground sewer infrastructure", "secondary": "MCD clears road debris"},
        urgency_score=9.4,
        corroboration_count=47,
        total_report_count=9,
        total_evidence_count=14,
        last_corroborated_at=now - timedelta(hours=1, minutes=23),
        created_at=now - timedelta(days=4),
    ),
    desc=(
        "Raw sewage overflowing from a burst underground pipe on the service lane beside Block E. "
        "The lane is knee-deep in contaminated water. Three DJB attempts to plug the pipe have "
        "failed — each time the temporary seal blew within 24 hrs. Residents are using plastic "
        "boards to wade through. Stench is unbearable. Kids are falling sick."
    ),
    imgs=_imgs("sewer", "waterlog", "contaminated"),
    extra_events=[
        ("issue_corroborated",         "citizen",   {"count": 8}),
        ("urgency_score_updated",       "system",    {"old": 4.1, "new": 7.6}),
        ("authority_acknowledged",      "authority", {"note": "Field team dispatched within 2 hrs"}),
        ("field_visit_scheduled",       "authority", {"scheduled_for": "Day 1 afternoon"}),
        ("field_visit_completed",       "authority", {"findings": "40m pipe burst confirmed, temporary seal placed"}),
        ("issue_corroborated",          "citizen",   {"count": 22}),
        ("repair_scheduled",            "authority", {"eta": "Day 2 morning", "crew": "6 workers"}),
        ("still_unresolved_confirmed",  "citizen",   {"note": "Seal blew again, lane re-flooded"}),
        ("urgency_score_updated",       "system",    {"old": 7.6, "new": 9.4}),
        ("rerouted",                    "system",    {"reason": "MCD added as secondary for debris coordination"}),
        ("issue_corroborated",          "citizen",   {"count": 47}),
        ("joint_inspection_done",       "authority", {"participants": "DJB + MCD Sanitation"}),
    ])

    # ════════════════════════════════════════════════════
    # SOUTH DELHI
    # ════════════════════════════════════════════════════

    # 1 · Lajpat Nagar II — sewer overflow, heavily corroborated (in_progress)
    make(IssueRecord(
        original_report_id="seed-r1", created_by="seed-u1",
        title="Sewer overflow flooding residential lane — Lajpat Nagar II",
        public_summary="Sewage overflowing from a choked sewer line for 3 days. Lane flooded, intolerable smell.",
        ai_summary="Sewer line blockage causing road-level overflow. DJB jurisdiction.",
        ai_confidence=0.93, status="in_progress",
        latitude=28.5677, longitude=77.2433,
        local_body_type="MCD", ward_no=42, ward_name="Lajpat Nagar",
        locality_name="Lajpat Nagar II",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="high", urgency_score=9.2,
        corroboration_count=11, total_report_count=12, total_evidence_count=14,
        last_corroborated_at=now - timedelta(hours=2),
        health_hazard_flag=True, drain_type="sewer",
        primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
        routing_confidence=0.96, routing_reason={"rule": "sewer_overflow->djb"},
        created_at=now - timedelta(days=3),
    ), desc="Sewage all over the lane since 3 days. My children can't go to school this way. DJB not responding.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 11}),
                     ("urgency_score_updated", "system", {"score": 9.2}),
                     ("authority_acknowledged", "authority", {"note": "Team dispatched"})])

    # 2 · Moolchand — arterial pothole, scooter accident reported (assigned)
    make(IssueRecord(
        original_report_id="seed-r2", created_by="seed-u2",
        title="Deep pothole on Ring Road near Moolchand flyover",
        public_summary="30cm-deep pothole on Ring Road. A two-wheeler fell last evening. Accident risk.",
        ai_summary="Arterial road pothole. PWD jurisdiction. Safety hazard.",
        ai_confidence=0.88, status="assigned",
        latitude=28.5700, longitude=77.2350,
        local_body_type="MCD", ward_no=42, ward_name="Lajpat Nagar",
        locality_name="Moolchand",
        issue_category_slug="roads_streets", issue_type_slug="pothole_major_road",
        asset_type_slug="arterial_road", severity="high", urgency_score=6.8,
        corroboration_count=5, total_report_count=6, total_evidence_count=6,
        road_class="arterial", public_safety_flag=True,
        primary_authority_slug="pwd", routing_confidence=0.91,
        created_at=now - timedelta(days=2),
    ), desc="Huge pothole on Ring Road. Scooter fell yesterday. PWD does nothing.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 5}),
                     ("field_visit_scheduled", "authority", {"date": "Tomorrow 10am"})])

    # 3 · Defence Colony — no water supply 48 hours (in_progress)
    make(IssueRecord(
        original_report_id="seed-r3", created_by="seed-u3",
        title="No water supply for 48 hours — Defence Colony Block C",
        public_summary="Water supply completely cut. Block C residents relying on tankers. Pipeline burst suspected.",
        ai_summary="No water supply; likely pipeline break. DJB jurisdiction.",
        ai_confidence=0.91, status="in_progress",
        latitude=28.5717, longitude=77.2294,
        local_body_type="MCD", ward_no=43, ward_name="Defence Colony",
        locality_name="Defence Colony Block C",
        issue_category_slug="water_sewer_drainage", issue_type_slug="no_water_supply",
        asset_type_slug="water_pipeline", severity="high", urgency_score=7.5,
        corroboration_count=8, total_report_count=9, total_evidence_count=8,
        last_corroborated_at=now - timedelta(hours=5),
        health_hazard_flag=True,
        primary_authority_slug="djb", routing_confidence=0.94,
        created_at=now - timedelta(days=2, hours=3),
    ), desc="48 hours no water. 200 flats affected. DJB helpline not picking up. Tanker demanded Rs 500.",
       imgs=_imgs("water_supply"),
       extra_events=[("issue_corroborated", "citizen", {"count": 8}),
                     ("tanker_deployed", "authority", {"tankers": 2, "area": "Block C"})])

    # 4 · Greater Kailash I — footpath encroachment by vendor (pending_verification)
    make(IssueRecord(
        original_report_id="seed-r4", created_by="seed-u4",
        title="Footpath fully blocked by vendor stalls — GK-I M Block Market",
        public_summary="Permanent vendor stalls occupying entire footpath. Pedestrians forced onto road.",
        ai_summary="Encroachment on public footpath near commercial area. MCD enforcement.",
        ai_confidence=0.81, status="pending_verification",
        latitude=28.5406, longitude=77.2357,
        local_body_type="MCD", ward_no=54, ward_name="Greater Kailash",
        locality_name="Greater Kailash I - M Block",
        issue_category_slug="roads_streets", issue_type_slug="footpath_encroachment",
        asset_type_slug="footpath", severity="medium", urgency_score=3.2,
        corroboration_count=3, total_report_count=3, total_evidence_count=4,
        primary_authority_slug="mcd_engineering", routing_confidence=0.78,
        created_at=now - timedelta(days=5),
    ), desc="Vendors have taken over the footpath permanently. Old people and children have to walk on the road.",
       imgs=_imgs("encroach", "footpath"))

    # 5 · Saket — tree fallen blocking access road (submitted, critical)
    make(IssueRecord(
        original_report_id="seed-r5", created_by="seed-u5",
        title="Large tree fallen across access road — Saket Block H",
        public_summary="Old neem tree uprooted in last night's storm. Blocking the only access road to Block H.",
        ai_summary="Tree hazard blocking road. MCD horticulture + engineering.",
        ai_confidence=0.89, status="submitted",
        latitude=28.5223, longitude=77.2100,
        local_body_type="MCD", ward_no=51, ward_name="Saket",
        locality_name="Saket Block H",
        issue_category_slug="parks_public_space", issue_type_slug="tree_hazard",
        asset_type_slug="tree", severity="critical", urgency_score=8.9,
        corroboration_count=6, total_report_count=6, total_evidence_count=7,
        last_corroborated_at=now - timedelta(hours=1),
        obstruction_flag=True, public_safety_flag=True,
        primary_authority_slug="mcd_horticulture", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.92, routing_reason={"rule": "tree_hazard->mcd_horticulture"},
        created_at=now - timedelta(hours=7),
    ), desc="Huge tree fell last night during storm. Completely blocking Block H access. Ambulance can't enter.",
       imgs=_imgs("tree"),
       extra_events=[("issue_corroborated", "citizen", {"count": 6})])

    # 6 · Okhla — dead animal carcass on main road (submitted)
    make(IssueRecord(
        original_report_id="seed-r6", created_by="seed-u6",
        title="Dead cow carcass on Okhla Industrial Road — day 2",
        public_summary="Dead animal lying on a busy industrial road for 2 days. Health hazard and traffic issue.",
        ai_summary="Dead animal removal required. MCD public health.",
        ai_confidence=0.87, status="submitted",
        latitude=28.5380, longitude=77.2647,
        local_body_type="MCD", ward_no=60, ward_name="Okhla",
        locality_name="Okhla Phase II Industrial Area",
        issue_category_slug="garbage_sanitation", issue_type_slug="dead_animal",
        severity="high", urgency_score=7.1,
        corroboration_count=4, total_report_count=4, total_evidence_count=4,
        last_corroborated_at=now - timedelta(hours=4),
        health_hazard_flag=True,
        primary_authority_slug="mcd_public_health", routing_confidence=0.88,
        created_at=now - timedelta(days=2),
    ), desc="Dead cow lying on the road for 2 days. Strong smell. Dogs surrounding it. MCD not responding.",
       imgs=_imgs("dead_animal"),
       extra_events=[("issue_corroborated", "citizen", {"count": 4})])

    # ════════════════════════════════════════════════════
    # CENTRAL DELHI
    # ════════════════════════════════════════════════════

    # 7 · Karol Bagh — garbage overflow, stray dogs (submitted)
    make(IssueRecord(
        original_report_id="seed-r7", created_by="seed-u7",
        title="Garbage not collected for 6 days — Karol Bagh Gaffar Market lane",
        public_summary="Community bin overflowing since 6 days. Garbage spilling onto road, stray dogs menace.",
        ai_summary="Garbage collection failure. MCD sanitation jurisdiction.",
        ai_confidence=0.92, status="submitted",
        latitude=28.6519, longitude=77.1909,
        local_body_type="MCD", ward_no=76, ward_name="Karol Bagh",
        locality_name="Karol Bagh - Gaffar Market",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="high", urgency_score=6.3,
        corroboration_count=9, total_report_count=10, total_evidence_count=11,
        last_corroborated_at=now - timedelta(hours=3),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.93,
        created_at=now - timedelta(days=4),
    ), desc="Garbage not picked up in 6 days. Bin overflowing. Stray dogs fighting at night near the lane.",
       imgs=_imgs("garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 9})])

    # 8 · Paharganj — open manhole on busy pedestrian lane (critical, in_progress)
    make(IssueRecord(
        original_report_id="seed-r8", created_by="seed-u8",
        title="Open sewer manhole on Paharganj main lane — child fell in last week",
        public_summary="Sewer manhole open without cover. A child fell in last week. Very dangerous on busy tourist lane.",
        ai_summary="Open uncovered manhole. Immediate safety risk. DJB + MCD.",
        ai_confidence=0.95, status="in_progress",
        latitude=28.6440, longitude=77.2092,
        local_body_type="MCD", ward_no=68, ward_name="Paharganj",
        locality_name="Paharganj Main Bazar",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="critical", urgency_score=9.8,
        corroboration_count=14, total_report_count=14, total_evidence_count=16,
        last_corroborated_at=now - timedelta(hours=1),
        obstruction_flag=True, public_safety_flag=True, health_hazard_flag=True,
        primary_authority_slug="djb", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.97,
        created_at=now - timedelta(days=7),
    ), desc="Open manhole with no cover since 1 week. A 7 year old child fell in and got injured. Busy tourist area.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 14}),
                     ("urgency_score_updated", "system", {"score": 9.8}),
                     ("authority_acknowledged", "authority", {"note": "Temporary barricade placed"})])

    # 9 · Patel Nagar — pothole near school, kids at risk (assigned)
    make(IssueRecord(
        original_report_id="seed-r9", created_by="seed-u9",
        title="Dangerous pothole outside Patel Nagar school gate",
        public_summary="Multiple potholes right outside a school gate. Children stumbling daily. Bus wheel damaged.",
        ai_summary="Pothole cluster outside school. PWD jurisdiction.",
        ai_confidence=0.85, status="assigned",
        latitude=28.6529, longitude=77.1710,
        local_body_type="MCD", ward_no=73, ward_name="Patel Nagar",
        locality_name="Patel Nagar West",
        issue_category_slug="roads_streets", issue_type_slug="pothole_local_road",
        asset_type_slug="local_lane", severity="medium", urgency_score=5.2,
        corroboration_count=7, total_report_count=8, total_evidence_count=9,
        last_corroborated_at=now - timedelta(hours=8),
        public_safety_flag=True,
        primary_authority_slug="pwd", routing_confidence=0.83,
        created_at=now - timedelta(days=6),
    ), desc="Three big potholes right at school gate. Kids fall almost every day. School bus wheel got punctured.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 7}),
                     ("field_visit_scheduled", "authority", {"engineer": "Sharma"})])

    # ════════════════════════════════════════════════════
    # NORTH WEST DELHI
    # ════════════════════════════════════════════════════

    # 10 · Rohini Sector 7 — streetlight false closure (reopened)
    make(IssueRecord(
        original_report_id="seed-r10", created_by="seed-u10",
        title="Streetlight not working — Rohini Sector 7 (marked fixed but still off)",
        public_summary="Entire stretch dark. Marked as resolved but still not working. 3 women reported unsafe.",
        ai_summary="Streetlight outage. Falsely closed. MCD engineering.",
        ai_confidence=0.79, status="reopened",
        latitude=28.7050, longitude=77.1180,
        local_body_type="MCD", ward_no=24, ward_name="Rohini",
        locality_name="Rohini Sector 7",
        issue_category_slug="lights_electrical", issue_type_slug="streetlight_not_working",
        severity="medium", urgency_score=4.5,
        corroboration_count=6, total_report_count=8, total_evidence_count=5,
        last_corroborated_at=now - timedelta(hours=6),
        public_safety_flag=True,
        primary_authority_slug="mcd_engineering", routing_confidence=0.81,
        created_at=now - timedelta(days=12),
    ), desc="Street was pitch dark for 2 weeks. Authority marked it resolved but light is still not working!",
       imgs=_imgs("streetlight"),
       extra_events=[("resolved", "authority", {"note": "Bulb replaced per inspection"}),
                     ("reopened", "citizen", {"note": "Light STILL not working, I took a video proof"}),
                     ("still_unresolved_confirmed", "citizen", {"count": 6})])

    # 11 · Pitampura — deep pothole on collector road (in_progress)
    make(IssueRecord(
        original_report_id="seed-r11", created_by="seed-u11",
        title="Pothole cluster on Pitampura collector road near Metro",
        public_summary="Multiple potholes near Pitampura metro station approach road. Evening traffic badly affected.",
        ai_summary="Pothole cluster on collector road. PWD jurisdiction.",
        ai_confidence=0.86, status="in_progress",
        latitude=28.7057, longitude=77.1349,
        local_body_type="MCD", ward_no=21, ward_name="Pitampura",
        locality_name="Pitampura - Metro Station Road",
        issue_category_slug="roads_streets", issue_type_slug="pothole_major_road",
        asset_type_slug="arterial_road", severity="medium", urgency_score=4.8,
        corroboration_count=5, total_report_count=5, total_evidence_count=6,
        road_class="collector_road", public_safety_flag=True,
        primary_authority_slug="pwd", routing_confidence=0.87,
        created_at=now - timedelta(days=4),
    ), desc="5-6 big potholes on road to Pitampura metro. Vehicles slow down suddenly, causes accidents.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 5}),
                     ("repair_scheduled", "authority", {"date": "Next week"})])

    # 12 · Rohini Sector 14 — illegal garbage dump in park (submitted)
    make(IssueRecord(
        original_report_id="seed-r12", created_by="seed-u12",
        title="Construction debris illegally dumped in Rohini Sector 14 park",
        public_summary="A builder has dumped construction malba in the public park. Children can't play. RWA protesting.",
        ai_summary="Illegal dumping of construction waste in public park. DDA + MCD.",
        ai_confidence=0.83, status="submitted",
        latitude=28.7219, longitude=77.1043,
        local_body_type="MCD", ward_no=22, ward_name="Rohini",
        locality_name="Rohini Sector 14",
        issue_category_slug="garbage_sanitation", issue_type_slug="illegal_dumping",
        asset_type_slug="garbage_blackspot", severity="medium", urgency_score=3.9,
        corroboration_count=3, total_report_count=3, total_evidence_count=5,
        primary_authority_slug="mcd_sanitation", secondary_authority_slug="dda",
        routing_confidence=0.79,
        created_at=now - timedelta(days=3),
    ), desc="Builder next door dumped all construction waste in our colony park. 2 trucks worth of malba.",
       imgs=_imgs("garbage"))

    # ════════════════════════════════════════════════════
    # SOUTH WEST DELHI
    # ════════════════════════════════════════════════════

    # 13 · Dwarka Sector 10 — waterlogging blocking arterial (submitted)
    make(IssueRecord(
        original_report_id="seed-r13", created_by="seed-u13",
        title="Knee-deep waterlogging on Dwarka Sector 10 main road",
        public_summary="Knee-deep water after yesterday's rain. Storm drain choked. Traffic grid-locked for 4 hours.",
        ai_summary="Corridor waterlogging, storm drain overflow. PWD + IFCD.",
        ai_confidence=0.84, status="submitted",
        latitude=28.5823, longitude=77.0500,
        local_body_type="MCD", ward_no=127, ward_name="Dwarka",
        locality_name="Dwarka Sector 10",
        issue_category_slug="water_sewer_drainage", issue_type_slug="waterlogging",
        asset_type_slug="roadside_storm_drain", severity="high", urgency_score=7.3,
        corroboration_count=9, total_report_count=10, total_evidence_count=10,
        last_corroborated_at=now - timedelta(hours=2),
        road_class="arterial", obstruction_flag=True, drain_type="roadside_storm_drain",
        primary_authority_slug="pwd", secondary_authority_slug="ifcd", routing_confidence=0.88,
        created_at=now - timedelta(hours=14),
    ), desc="Road completely flooded. Knee deep water. Cars stuck. Drain completely choked with debris.",
       imgs=_imgs("waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 9})])

    # 14 · Janakpuri — contaminated yellow water supply (assigned)
    make(IssueRecord(
        original_report_id="seed-r14", created_by="seed-u14",
        title="Contaminated yellowish water from taps — Janakpuri Block A",
        public_summary="Yellowish-brown water since 3 days. Residents bought bottled water. Pipeline cross-connection suspected.",
        ai_summary="Contaminated water supply. DJB urgent inspection required.",
        ai_confidence=0.90, status="assigned",
        latitude=28.6270, longitude=77.0857,
        local_body_type="MCD", ward_no=110, ward_name="Janakpuri",
        locality_name="Janakpuri Block A",
        issue_category_slug="water_sewer_drainage", issue_type_slug="contaminated_water",
        asset_type_slug="water_pipeline", severity="high", urgency_score=8.1,
        corroboration_count=12, total_report_count=13, total_evidence_count=13,
        last_corroborated_at=now - timedelta(hours=3),
        health_hazard_flag=True,
        primary_authority_slug="djb", routing_confidence=0.93,
        created_at=now - timedelta(days=3),
    ), desc="Yellow dirty water from taps. 3 children sick with stomach issues. Doctor suspects contamination.",
       imgs=_imgs("contaminated", "water_supply"),
       extra_events=[("issue_corroborated", "citizen", {"count": 12}),
                     ("urgency_score_updated", "system", {"score": 8.1}),
                     ("sample_collected", "authority", {"lab": "DJB Lab, Pusa Rd"})])

    # 15 · Janakpuri — garbage not collected near flyover (resolved)
    make(IssueRecord(
        original_report_id="seed-r15", created_by="seed-u15",
        title="Garbage pile under Janakpuri flyover — cleared after 5 days",
        public_summary="Resolved. 2-tonne garbage mound under flyover collected after 5 days and repeated reports.",
        ai_summary="Garbage collection success story after community pressure.",
        ai_confidence=0.88, status="resolved",
        latitude=28.6210, longitude=77.0910,
        local_body_type="MCD", ward_no=111, ward_name="Janakpuri",
        locality_name="Janakpuri Flyover",
        issue_category_slug="garbage_sanitation", issue_type_slug="illegal_dumping",
        asset_type_slug="garbage_blackspot", severity="medium", urgency_score=1.0,
        corroboration_count=5, total_report_count=6, total_evidence_count=6,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.87,
        created_at=now - timedelta(days=8),
    ), desc="Huge pile under flyover. Stray dogs, rats. Finally cleaned after multiple reports!",
       imgs=_imgs("garbage"),
       extra_events=[("resolved", "authority", {"note": "2-tonne garbage cleared, area disinfected"}),
                     ("resolution_confirmed", "citizen", {"note": "Confirmed clean, thank you"})])

    # ════════════════════════════════════════════════════
    # WEST DELHI
    # ════════════════════════════════════════════════════

    # 16 · Rajouri Garden — broken footpath blocking wheelchair (submitted)
    make(IssueRecord(
        original_report_id="seed-r16", created_by="seed-u16",
        title="Footpath broken and uneven — Rajouri Garden West market",
        public_summary="Severely broken footpath. Elderly residents and wheelchair users cannot use it. Tiles missing.",
        ai_summary="Broken footpath, accessibility concern. MCD engineering.",
        ai_confidence=0.78, status="submitted",
        latitude=28.6495, longitude=77.1227,
        local_body_type="MCD", ward_no=93, ward_name="Rajouri Garden",
        locality_name="Rajouri Garden - Tagore Garden Road",
        issue_category_slug="roads_streets", issue_type_slug="broken_footpath",
        asset_type_slug="footpath", severity="low", urgency_score=2.3,
        corroboration_count=2, total_report_count=2, total_evidence_count=3,
        primary_authority_slug="mcd_engineering", routing_confidence=0.74,
        created_at=now - timedelta(days=10),
    ), desc="Footpath completely broken in front of park. My 80-year-old mother fell last month.",
       imgs=_imgs("footpath"))

    # 17 · Tilak Nagar — garbage not collected 5 days (in_progress)
    make(IssueRecord(
        original_report_id="seed-r17", created_by="seed-u17",
        title="Garbage van hasn't come in 5 days — Tilak Nagar Block 14",
        public_summary="Residential garbage not collected for 5 days. Bin overflowing. Rats and mosquitoes.",
        ai_summary="Sanitation lapse. MCD garbage collection failure.",
        ai_confidence=0.91, status="in_progress",
        latitude=28.6410, longitude=77.0969,
        local_body_type="MCD", ward_no=89, ward_name="Tilak Nagar",
        locality_name="Tilak Nagar Block 14",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="medium", urgency_score=5.0,
        corroboration_count=6, total_report_count=7, total_evidence_count=7,
        last_corroborated_at=now - timedelta(hours=9),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.90,
        created_at=now - timedelta(days=5),
    ), desc="Garbage van driver says vehicle is broken but no replacement. Dengue season and no garbage pickup.",
       imgs=_imgs("garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 6}),
                     ("authority_acknowledged", "authority", {"note": "Replacement vehicle arranged"})])

    # 18 · Punjabi Bagh — contaminated water, skin rashes reported (assigned)
    make(IssueRecord(
        original_report_id="seed-r18", created_by="seed-u18",
        title="Smelly brown water causing skin rashes — Punjabi Bagh West",
        public_summary="Brown-coloured, foul-smelling water. At least 8 families report skin rashes and diarrhea.",
        ai_summary="Contaminated water supply. Public health emergency. DJB + MCD health.",
        ai_confidence=0.93, status="assigned",
        latitude=28.6684, longitude=77.1324,
        local_body_type="MCD", ward_no=86, ward_name="Punjabi Bagh",
        locality_name="Punjabi Bagh West",
        issue_category_slug="water_sewer_drainage", issue_type_slug="contaminated_water",
        asset_type_slug="water_pipeline", severity="critical", urgency_score=9.5,
        corroboration_count=15, total_report_count=16, total_evidence_count=17,
        last_corroborated_at=now - timedelta(hours=1),
        health_hazard_flag=True,
        primary_authority_slug="djb", secondary_authority_slug="mcd_public_health",
        routing_confidence=0.96,
        created_at=now - timedelta(days=4),
    ), desc="Brown smelly water since 4 days. 3 children hospitalised with stomach infection. Help urgently needed.",
       imgs=_imgs("contaminated"),
       extra_events=[("issue_corroborated", "citizen", {"count": 15}),
                     ("urgency_score_updated", "system", {"score": 9.5}),
                     ("authority_acknowledged", "authority", {"note": "Emergency tankers deployed, lab test ordered"})])

    # ════════════════════════════════════════════════════
    # NORTH DELHI
    # ════════════════════════════════════════════════════

    # 19 · Civil Lines — dangerous tree hanging over road (assigned)
    make(IssueRecord(
        original_report_id="seed-r19", created_by="seed-u19",
        title="Large dead tree branch hanging over Civil Lines road — ready to fall",
        public_summary="Half-dead tree branch hanging over busy road near Civil Lines metro. Will fall any time.",
        ai_summary="Imminent tree hazard on road. MCD horticulture urgent.",
        ai_confidence=0.87, status="assigned",
        latitude=28.6858, longitude=77.2259,
        local_body_type="MCD", ward_no=4, ward_name="Civil Lines",
        locality_name="Civil Lines - Alipur Road",
        issue_category_slug="parks_public_space", issue_type_slug="tree_hazard",
        asset_type_slug="tree", severity="high", urgency_score=7.9,
        corroboration_count=4, total_report_count=4, total_evidence_count=5,
        last_corroborated_at=now - timedelta(hours=4),
        public_safety_flag=True, obstruction_flag=True,
        primary_authority_slug="mcd_horticulture", routing_confidence=0.90,
        created_at=now - timedelta(days=2),
    ), desc="Dead tree branch hanging dangerously over the road. Very heavy. Wind will bring it down. School bus passes here.",
       imgs=_imgs("tree"),
       extra_events=[("issue_corroborated", "citizen", {"count": 4}),
                     ("field_visit_scheduled", "authority", {"team": "Horticulture wing"})])

    # 20 · Model Town — no water supply 3 days (in_progress)
    make(IssueRecord(
        original_report_id="seed-r20", created_by="seed-u20",
        title="No water supply for 72 hours — Model Town Phase II",
        public_summary="72 hours without municipal water. 300+ households affected. DJB booster pump failed.",
        ai_summary="No water supply due to pump failure. DJB emergency repair.",
        ai_confidence=0.92, status="in_progress",
        latitude=28.7186, longitude=77.1899,
        local_body_type="MCD", ward_no=9, ward_name="Model Town",
        locality_name="Model Town Phase II",
        issue_category_slug="water_sewer_drainage", issue_type_slug="no_water_supply",
        asset_type_slug="water_pipeline", severity="high", urgency_score=8.4,
        corroboration_count=18, total_report_count=19, total_evidence_count=18,
        last_corroborated_at=now - timedelta(hours=2),
        health_hazard_flag=True,
        primary_authority_slug="djb", routing_confidence=0.95,
        created_at=now - timedelta(days=3),
    ), desc="3 days no water. We are buying 20L cans at Rs 30 each. DJB says booster pump is under repair.",
       imgs=_imgs("water_supply"),
       extra_events=[("issue_corroborated", "citizen", {"count": 18}),
                     ("urgency_score_updated", "system", {"score": 8.4}),
                     ("tanker_deployed", "authority", {"tankers": 4, "schedule": "8am and 6pm"})])

    # 21 · Burari — open drain overflow near homes (submitted)
    make(IssueRecord(
        original_report_id="seed-r21", created_by="seed-u21",
        title="Open nullah overflowing into homes — Burari Jagjit Nagar",
        public_summary="Seasonal nullah overflow entering ground-floor homes. 6 families displaced. Mosquito menace.",
        ai_summary="Local drain overflow into habitation. IFCD + MCD drainage.",
        ai_confidence=0.86, status="submitted",
        latitude=28.7452, longitude=77.2061,
        local_body_type="MCD", ward_no=6, ward_name="Burari",
        locality_name="Burari Jagjit Nagar",
        issue_category_slug="water_sewer_drainage", issue_type_slug="clogged_local_drain",
        asset_type_slug="local_open_drain", severity="high", urgency_score=6.7,
        corroboration_count=7, total_report_count=7, total_evidence_count=8,
        last_corroborated_at=now - timedelta(hours=5),
        health_hazard_flag=True, drain_type="local_open_drain",
        primary_authority_slug="ifcd", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.84,
        created_at=now - timedelta(days=1),
    ), desc="Nullah overflowing into our houses. Ground floor flooded. 6 families sleeping in the streets.",
       imgs=_imgs("waterlog", "sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 7})])

    # ════════════════════════════════════════════════════
    # EAST DELHI
    # ════════════════════════════════════════════════════

    # 22 · Mayur Vihar Phase I — sewer burst (critical, in_progress)
    make(IssueRecord(
        original_report_id="seed-r22", created_by="seed-u22",
        title="Sewer pipe burst — Mayur Vihar Phase 1 Pocket 3",
        public_summary="Main sewer line burst at pocket 3 crossing. Raw sewage flowing on road. 500m stretch affected.",
        ai_summary="Sewer main burst. DJB emergency. Critical public health issue.",
        ai_confidence=0.95, status="in_progress",
        latitude=28.6086, longitude=77.2992,
        local_body_type="MCD", ward_no=172, ward_name="Mayur Vihar",
        locality_name="Mayur Vihar Phase 1 Pocket 3",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="critical", urgency_score=9.6,
        corroboration_count=16, total_report_count=17, total_evidence_count=19,
        last_corroborated_at=now - timedelta(minutes=45),
        health_hazard_flag=True, obstruction_flag=True, drain_type="sewer",
        primary_authority_slug="djb", routing_confidence=0.97,
        created_at=now - timedelta(hours=18),
    ), desc="Sewer burst. Raw sewage 2 inches deep on entire street. Cannot walk. Shops closed.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 16}),
                     ("urgency_score_updated", "system", {"score": 9.6}),
                     ("authority_acknowledged", "authority", {"note": "Emergency team deployed, ETA 2 hrs"})])

    # 23 · Preet Vihar — pothole local road (submitted)
    make(IssueRecord(
        original_report_id="seed-r23", created_by="seed-u23",
        title="Pothole-riddled road in Preet Vihar Block A",
        public_summary="Entire block A internal road in terrible condition. 12+ potholes in 200m stretch.",
        ai_summary="Multiple potholes on local lane. MCD engineering.",
        ai_confidence=0.83, status="submitted",
        latitude=28.6390, longitude=77.2943,
        local_body_type="MCD", ward_no=167, ward_name="Preet Vihar",
        locality_name="Preet Vihar Block A",
        issue_category_slug="roads_streets", issue_type_slug="pothole_local_road",
        asset_type_slug="local_lane", severity="medium", urgency_score=3.5,
        corroboration_count=4, total_report_count=4, total_evidence_count=4,
        road_class="local_lane",
        primary_authority_slug="pwd", routing_confidence=0.80,
        created_at=now - timedelta(days=7),
    ), desc="Entire road is nothing but potholes. Residents have been complaining for 2 years. No one listens.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 4})])

    # 24 · Laxmi Nagar — stray dog pack attack (submitted)
    make(IssueRecord(
        original_report_id="seed-r24", created_by="seed-u24",
        title="Pack of aggressive stray dogs attacking people — Laxmi Nagar Vikas Marg",
        public_summary="Pack of 10+ stray dogs attacking pedestrians and cyclists near Laxmi Nagar metro. 2 bite incidents.",
        ai_summary="Stray dog menace. MCD animal control required urgently.",
        ai_confidence=0.88, status="submitted",
        latitude=28.6302, longitude=77.2793,
        local_body_type="MCD", ward_no=178, ward_name="Laxmi Nagar",
        locality_name="Laxmi Nagar - Vikas Marg",
        issue_category_slug="public_safety_hazard", issue_type_slug="stray_dog_issue",
        severity="high", urgency_score=7.2,
        corroboration_count=8, total_report_count=8, total_evidence_count=8,
        last_corroborated_at=now - timedelta(hours=3),
        public_safety_flag=True, health_hazard_flag=True,
        primary_authority_slug="mcd_public_health", routing_confidence=0.86,
        created_at=now - timedelta(days=2),
    ), desc="2 people bitten in 3 days near Laxmi Nagar metro exit gate 1. School children are scared.",
       imgs=_imgs("stray_dog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 8})])

    # ════════════════════════════════════════════════════
    # NORTH EAST DELHI
    # ════════════════════════════════════════════════════

    # 25 · Seelampur — open sewer on main road (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r25", created_by="seed-u25",
        title="Open raw sewage channel on Seelampur main road — months unaddressed",
        public_summary="Open sewer with raw sewage flowing alongside main road for months. Area has high child population.",
        ai_summary="Open sewage channel. Major public health risk. DJB + MCD sanitation.",
        ai_confidence=0.90, status="submitted",
        latitude=28.6714, longitude=77.2807,
        local_body_type="MCD", ward_no=63, ward_name="Seelampur",
        locality_name="Seelampur Main Road",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="critical", urgency_score=8.8,
        corroboration_count=11, total_report_count=12, total_evidence_count=12,
        last_corroborated_at=now - timedelta(hours=6),
        health_hazard_flag=True, drain_type="sewer",
        primary_authority_slug="djb", secondary_authority_slug="mcd_sanitation",
        routing_confidence=0.91,
        created_at=now - timedelta(days=14),
    ), desc="Open nullah with black sewage water on main road. Months old problem. Children play near it.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 11}),
                     ("urgency_score_updated", "system", {"score": 8.8})])

    # 26 · Mustafabad — illegal dumping, garbage blackspot (assigned)
    make(IssueRecord(
        original_report_id="seed-r26", created_by="seed-u26",
        title="Recurring illegal garbage dump — Mustafabad Chowk",
        public_summary="Notorious garbage blackspot at Mustafabad Chowk. Trucks dump construction and domestic waste nightly.",
        ai_summary="Illegal garbage blackspot. MCD sanitation enforcement needed.",
        ai_confidence=0.87, status="assigned",
        latitude=28.7122, longitude=77.3053,
        local_body_type="MCD", ward_no=67, ward_name="Mustafabad",
        locality_name="Mustafabad Chowk",
        issue_category_slug="garbage_sanitation", issue_type_slug="illegal_dumping",
        asset_type_slug="garbage_blackspot", severity="medium", urgency_score=5.4,
        corroboration_count=6, total_report_count=7, total_evidence_count=9,
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.85,
        created_at=now - timedelta(days=9),
    ), desc="Same spot gets filled with garbage and construction waste every week. Camera needed here.",
       imgs=_imgs("garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 6}),
                     ("field_visit_scheduled", "authority", {"officer": "Sanitation Inspector"})])

    # ════════════════════════════════════════════════════
    # SHAHDARA DISTRICT
    # ════════════════════════════════════════════════════

    # 27 · Shahdara — waterlogging near busy market (in_progress)
    make(IssueRecord(
        original_report_id="seed-r27", created_by="seed-u27",
        title="Waterlogging flooding Shahdara main market — business losses daily",
        public_summary="Low-lying market area floods even in light rain. Shopkeepers losing business. IFCD drain needs desilting.",
        ai_summary="Recurring waterlogging due to silted drain. IFCD + MCD. Commercial area.",
        ai_confidence=0.85, status="in_progress",
        latitude=28.6726, longitude=77.2872,
        local_body_type="MCD", ward_no=183, ward_name="Shahdara",
        locality_name="Shahdara Market - Gandhi Nagar",
        issue_category_slug="water_sewer_drainage", issue_type_slug="waterlogging",
        asset_type_slug="roadside_storm_drain", severity="high", urgency_score=6.9,
        corroboration_count=9, total_report_count=10, total_evidence_count=11,
        last_corroborated_at=now - timedelta(hours=4),
        obstruction_flag=True, drain_type="roadside_storm_drain",
        primary_authority_slug="ifcd", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.87,
        created_at=now - timedelta(days=6),
    ), desc="Market floods every time it rains. Shops losing lakhs. Drain is completely silted and choked.",
       imgs=_imgs("waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 9}),
                     ("authority_acknowledged", "authority", {"note": "Desilting scheduled this week"})])

    # 28 · Vishwasnagar — 3 streetlights broken, dark lane (submitted)
    make(IssueRecord(
        original_report_id="seed-r28", created_by="seed-u28",
        title="Three consecutive streetlights not working — Vishwasnagar back lane",
        public_summary="300m stretch of residential back lane completely dark. Women's safety concern.",
        ai_summary="Multiple streetlight failures. MCD engineering.",
        ai_confidence=0.81, status="submitted",
        latitude=28.6613, longitude=77.2977,
        local_body_type="MCD", ward_no=184, ward_name="Vishwasnagar",
        locality_name="Vishwasnagar Block B",
        issue_category_slug="lights_electrical", issue_type_slug="streetlight_not_working",
        severity="medium", urgency_score=3.8,
        corroboration_count=3, total_report_count=3, total_evidence_count=3,
        public_safety_flag=True,
        primary_authority_slug="mcd_engineering", routing_confidence=0.79,
        created_at=now - timedelta(days=8),
    ), desc="3 lights broken in a row. 300 metre stretch. Harassment incidents happened twice this month.",
       imgs=_imgs("streetlight"))

    # ════════════════════════════════════════════════════
    # NEW DELHI / NDMC
    # ════════════════════════════════════════════════════

    # 29 · Connaught Place — damaged park tiles, tourist area (resolved)
    make(IssueRecord(
        original_report_id="seed-r29", created_by="seed-u29",
        title="Broken tiles and damaged benches — CP Central Park [RESOLVED]",
        public_summary="Resolved successfully. 14 broken tiles and 3 benches repaired in CP Central Park within 48 hours.",
        ai_summary="Park infrastructure damage. NDMC maintenance.",
        ai_confidence=0.77, status="resolved",
        latitude=28.6319, longitude=77.2195,
        local_body_type="NDMC", ward_no=1, ward_name="Connaught Place",
        locality_name="Connaught Place Inner Circle",
        issue_category_slug="parks_public_space", issue_type_slug="park_maintenance_issue",
        asset_type_slug="park", severity="low", urgency_score=1.0,
        corroboration_count=2, total_report_count=2, total_evidence_count=2,
        primary_authority_slug="ndmc_civil", routing_confidence=0.82,
        created_at=now - timedelta(days=5),
    ), desc="Broken tiles in CP central park. Elderly people are tripping. Tourist area should be better maintained.",
       imgs=_imgs("footpath"),
       extra_events=[("resolved", "authority", {"note": "14 tiles replaced, 3 benches repaired in 48 hrs"}),
                     ("resolution_confirmed", "citizen", {"rating": 5})])

    # 30 · Lodhi Road — road crater after water pipe burst (in_progress)
    make(IssueRecord(
        original_report_id="seed-r30", created_by="seed-u30",
        title="Road cave-in after water pipe burst — Lodhi Road junction",
        public_summary="Water pipe burst caused road to cave in. 4-foot crater near important junction. Traffic diverted.",
        ai_summary="Road subsidence from pipe burst. PWD + DJB. Major arterial impact.",
        ai_confidence=0.94, status="in_progress",
        latitude=28.5918, longitude=77.2222,
        local_body_type="NDMC", ward_no=2, ward_name="New Delhi",
        locality_name="Lodhi Road Junction",
        issue_category_slug="roads_streets", issue_type_slug="road_obstruction",
        asset_type_slug="arterial_road", severity="critical", urgency_score=9.1,
        corroboration_count=7, total_report_count=8, total_evidence_count=8,
        last_corroborated_at=now - timedelta(hours=2),
        obstruction_flag=True, public_safety_flag=True, road_class="arterial",
        primary_authority_slug="pwd", secondary_authority_slug="djb",
        routing_confidence=0.96,
        created_at=now - timedelta(hours=20),
    ), desc="Water pipe burst and road caved in overnight. 4 foot deep crater. Police deployed for traffic control.",
       imgs=_imgs("pothole", "waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 7}),
                     ("urgency_score_updated", "system", {"score": 9.1}),
                     ("authority_acknowledged", "authority", {"note": "Joint PWD-DJB team on site"})])

    # ════════════════════════════════════════════════════
    # BATCH 2 — 30 more issues covering new wards & new issue types
    # Unused authority slugs introduced: ndmc_sanitation, ndmc_horticulture,
    #   dcb_civic, delhi_police, nhai, dda (expanded use)
    # New edge cases: manual_review, jurisdiction disputes, 45-day chronic,
    #   fastest-ever resolution, NHAI highway pothole, industrial pollution,
    #   dengue outbreak, diplomatic area flood, cantonment board
    # ════════════════════════════════════════════════════

    # ── SOUTH DELHI (new localities) ─────────────────────────────────────────

    # 31 · Malviya Nagar — road sinking, AI misrouted twice, manual_review
    make(IssueRecord(
        original_report_id="seed-r31", created_by="seed-u31",
        title="Road sinking above corroded water main — Malviya Nagar C Block (45 days)",
        public_summary="Road surface collapsing in 3 spots over 40m. 45 days reported, wrongly routed to MCD twice. DJB finally identified corroded main but disputes road repair.",
        ai_summary="Road subsidence from corroded underground water main. DJB root-cause, PWD road repair.",
        ai_confidence=0.61, status="manual_review",
        latitude=28.5297, longitude=77.2018,
        local_body_type="MCD", ward_no=49, ward_name="Malviya Nagar",
        locality_name="Malviya Nagar C Block",
        issue_category_slug="roads_streets", issue_type_slug="road_obstruction",
        asset_type_slug="arterial_road", severity="high", urgency_score=7.4,
        corroboration_count=10, total_report_count=13, total_evidence_count=15,
        last_corroborated_at=now - timedelta(days=1),
        obstruction_flag=True, public_safety_flag=True, road_class="collector_road",
        primary_authority_slug="djb", secondary_authority_slug="pwd",
        routing_confidence=0.61, routing_reason={"rule": "low_confidence_manual_review"},
        created_at=now - timedelta(days=45),
    ), desc="Road sinking for 45 days. MCD sent twice, says its DJB pipe. DJB says road repair is MCD. Nobody fixes it.",
       imgs=_imgs("pothole", "waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 10}),
                     ("routed", "system", {"to": "mcd_engineering", "confidence": 0.55}),
                     ("authority_rejected", "authority", {"note": "Not MCD scope, pipe is DJB"}),
                     ("rerouted", "system", {"to": "djb", "confidence": 0.61}),
                     ("manual_review_triggered", "system", {"reason": "Two authority rejections"})])

    # 32 · Hauz Khas Village — illegal rooftop construction blocking fire escape (submitted)
    make(IssueRecord(
        original_report_id="seed-r32", created_by="seed-u32",
        title="Illegal third-floor extension blocking fire escape — Hauz Khas Village",
        public_summary="Unauthorized rooftop extension on DDA-regulated land blocking the only fire-escape route for 3 adjacent properties.",
        ai_summary="Unauthorized construction on DDA land. DDA enforcement required.",
        ai_confidence=0.79, status="submitted",
        latitude=28.5541, longitude=77.2030,
        local_body_type="MCD", ward_no=53, ward_name="Hauz Khas",
        locality_name="Hauz Khas Village",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="high", urgency_score=5.8,
        corroboration_count=4, total_report_count=4, total_evidence_count=6,
        public_safety_flag=True, obstruction_flag=True,
        primary_authority_slug="dda", routing_confidence=0.82,
        created_at=now - timedelta(days=9),
    ), desc="Neighbour built an illegal third floor. Blocked the only fire exit for 3 buildings. DDA please act.",
       imgs=_imgs("encroach"))

    # 33 · Vasant Kunj Sector B — DDA park grabbed by 15 vendor stalls (pending_verification)
    make(IssueRecord(
        original_report_id="seed-r33", created_by="seed-u33",
        title="DDA park taken over by 15 permanent vendor stalls — Vasant Kunj Sector B",
        public_summary="15 permanent shops erected in DDA park over 18 months. 200+ families petitioned. Children have no play area.",
        ai_summary="Encroachment of DDA park by vendors. DDA enforcement required.",
        ai_confidence=0.74, status="pending_verification",
        latitude=28.5205, longitude=77.1560,
        local_body_type="MCD", ward_no=130, ward_name="Vasant Kunj",
        locality_name="Vasant Kunj Sector B",
        issue_category_slug="parks_public_space", issue_type_slug="park_maintenance_issue",
        asset_type_slug="park", severity="medium", urgency_score=3.1,
        corroboration_count=22, total_report_count=23, total_evidence_count=20,
        last_corroborated_at=now - timedelta(hours=10),
        primary_authority_slug="dda", secondary_authority_slug="mcd_sanitation",
        routing_confidence=0.76,
        created_at=now - timedelta(days=20),
    ), desc="DDA park fully occupied by dhabas and shops for 18 months. We've complained many times. RWA signed petition.",
       imgs=_imgs("encroach", "garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 22}),
                     ("verification_requested", "system", {"reason": "High corroboration, pending field check"})])

    # 34 · Mehrauli — stolen manhole cover on tourist road near Qutb Minar (critical, in_progress)
    make(IssueRecord(
        original_report_id="seed-r34", created_by="seed-u34",
        title="Stolen manhole cover — open pit on tourist road near Qutb Minar",
        public_summary="Manhole cover stolen. Open pit on busy tourist road near Qutb Minar. Tourists and cyclists at risk. Night visibility zero.",
        ai_summary="Missing manhole cover on tourist road. Safety hazard. DJB + MCD engineering.",
        ai_confidence=0.93, status="in_progress",
        latitude=28.5244, longitude=77.1853,
        local_body_type="MCD", ward_no=48, ward_name="Mehrauli",
        locality_name="Mehrauli - Qutb Road",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="critical", urgency_score=9.0,
        corroboration_count=8, total_report_count=9, total_evidence_count=10,
        last_corroborated_at=now - timedelta(hours=3),
        obstruction_flag=True, public_safety_flag=True,
        primary_authority_slug="djb", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.91,
        created_at=now - timedelta(days=3),
    ), desc="Manhole cover stolen. Open pit on tourist road. Foreign tourists walking nearby. Very dangerous at night.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 8}),
                     ("urgency_score_updated", "system", {"score": 9.0}),
                     ("authority_acknowledged", "authority", {"note": "Temporary barricade placed, cover on order"})])

    # 35 · Sangam Vihar J-Block — choked nullah, 12 dengue cases (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r35", created_by="seed-u35",
        title="Choked nullah breeding dengue — 12 confirmed cases — Sangam Vihar J-Block",
        public_summary="Open nullah completely blocked. Stagnant water 3+ weeks. Health centre reports 12 dengue cases from this block alone. No fogging done.",
        ai_summary="Stagnant nullah with dengue breeding. Public health emergency. MCD public health + IFCD.",
        ai_confidence=0.89, status="submitted",
        latitude=28.4962, longitude=77.2315,
        local_body_type="MCD", ward_no=56, ward_name="Sangam Vihar",
        locality_name="Sangam Vihar J-Block",
        issue_category_slug="public_safety_hazard", issue_type_slug="stray_dog_issue",
        severity="critical", urgency_score=9.3,
        corroboration_count=17, total_report_count=18, total_evidence_count=16,
        last_corroborated_at=now - timedelta(hours=2),
        health_hazard_flag=True, drain_type="local_open_drain",
        primary_authority_slug="mcd_public_health", secondary_authority_slug="ifcd",
        routing_confidence=0.88,
        created_at=now - timedelta(days=5),
    ), desc="12 dengue cases in our block. Nullah completely choked, standing water 3 weeks. No fogging. Please help.",
       imgs=_imgs("waterlog", "garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 17}),
                     ("urgency_score_updated", "system", {"score": 9.3})])

    # ── CENTRAL DELHI (new) ────────────────────────────────────────────────

    # 36 · Chandni Chowk Nai Sarak — live wire at head height, sparking (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r36", created_by="seed-u36",
        title="Snapped live power line hanging 1m above Nai Sarak — sparking at night",
        public_summary="Electric wire snapped by overloaded rickshaw. Hanging at head height over busy market lane for 2 days. Sparking visibly at night.",
        ai_summary="Live electrical wire at head height. Immediate electrocution risk. Delhi Police + MCD engineering.",
        ai_confidence=0.96, status="submitted",
        latitude=28.6505, longitude=77.2303,
        local_body_type="MCD", ward_no=68, ward_name="Chandni Chowk",
        locality_name="Chandni Chowk - Nai Sarak",
        issue_category_slug="lights_electrical", issue_type_slug="streetlight_not_working",
        severity="critical", urgency_score=9.7,
        corroboration_count=13, total_report_count=14, total_evidence_count=15,
        last_corroborated_at=now - timedelta(hours=1),
        public_safety_flag=True,
        primary_authority_slug="mcd_engineering", secondary_authority_slug="delhi_police",
        routing_confidence=0.95,
        created_at=now - timedelta(days=2),
    ), desc="Live wire hanging low over crowded market lane. Sparking at night. Thousands of people walk here daily.",
       imgs=_imgs("streetlight"),
       extra_events=[("issue_corroborated", "citizen", {"count": 13}),
                     ("urgency_score_updated", "system", {"score": 9.7}),
                     ("delhi_police_informed", "system", {"note": "Auto-notified due to electrocution risk"})])

    # 37 · Sadar Bazar Anaj Mandi — garbage next to wholesale food market (high, submitted)
    make(IssueRecord(
        original_report_id="seed-r37", created_by="seed-u37",
        title="Overflowing garbage bins outside grain wholesale market — Sadar Bazar",
        public_summary="4 bins overflowing for 5 days next to grain market. Rats visible in open. Food contamination risk for wholesale goods.",
        ai_summary="Garbage overflow adjacent to food storage area. Serious contamination risk. MCD sanitation.",
        ai_confidence=0.91, status="submitted",
        latitude=28.6582, longitude=77.2117,
        local_body_type="MCD", ward_no=69, ward_name="Sadar Bazar",
        locality_name="Sadar Bazar Anaj Mandi",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="high", urgency_score=7.0,
        corroboration_count=8, total_report_count=9, total_evidence_count=9,
        last_corroborated_at=now - timedelta(hours=6),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.92,
        created_at=now - timedelta(days=5),
    ), desc="Garbage rotting next to the grain market. Rats everywhere. People buying food here. Health disaster waiting.",
       imgs=_imgs("garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 8})])

    # 38 · Kamla Market NH-48 — bus shelter roof caved in (medium, assigned)
    make(IssueRecord(
        original_report_id="seed-r38", created_by="seed-u38",
        title="Bus shelter roof collapsed — Kamla Market stop, NH-48",
        public_summary="Bus shelter roof caved in after last week's storm. 60+ daily commuters standing on national highway with no cover.",
        ai_summary="Collapsed bus shelter on highway stop. MCD engineering.",
        ai_confidence=0.78, status="assigned",
        latitude=28.6443, longitude=77.2105,
        local_body_type="MCD", ward_no=70, ward_name="Minto Road",
        locality_name="Kamla Market Bus Stop",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="medium", urgency_score=4.1,
        corroboration_count=5, total_report_count=5, total_evidence_count=5,
        primary_authority_slug="mcd_engineering", routing_confidence=0.80,
        created_at=now - timedelta(days=7),
    ), desc="Bus shelter roof fell in rain. Senior citizens standing on highway edge every morning. Please fix urgently.",
       imgs=_imgs("footpath"),
       extra_events=[("issue_corroborated", "citizen", {"count": 5}),
                     ("field_visit_completed", "authority", {"note": "Assessed, materials ordered"})])

    # ── NORTH WEST DELHI (new) ────────────────────────────────────────────

    # 39 · Shalimar Bagh Block AF — DDA park wall collapsed by construction vibration (medium, assigned)
    make(IssueRecord(
        original_report_id="seed-r39", created_by="seed-u39",
        title="DDA park boundary wall collapsed from construction vibration — Shalimar Bagh Block AF",
        public_summary="20-metre wall section fell due to nearby building construction. Children's play equipment now exposed to road traffic.",
        ai_summary="DDA park wall collapse. DDA enforcement + construction supervision needed.",
        ai_confidence=0.82, status="assigned",
        latitude=28.7138, longitude=77.1640,
        local_body_type="MCD", ward_no=16, ward_name="Shalimar Bagh",
        locality_name="Shalimar Bagh Block AF",
        issue_category_slug="parks_public_space", issue_type_slug="park_maintenance_issue",
        asset_type_slug="park", severity="medium", urgency_score=5.3,
        corroboration_count=4, total_report_count=4, total_evidence_count=5,
        public_safety_flag=True,
        primary_authority_slug="dda", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.79,
        created_at=now - timedelta(days=6),
    ), desc="Park wall fell due to nearby building construction. Kids' swings visible from main road now. Trespassing risk.",
       imgs=_imgs("footpath"),
       extra_events=[("issue_corroborated", "citizen", {"count": 4}),
                     ("notice_issued", "authority", {"to": "Builder", "note": "Stop work pending inspection"})])

    # 40 · Nangloi Railway Underpass — floods 4 feet, ambulance blocked (critical, in_progress)
    make(IssueRecord(
        original_report_id="seed-r40", created_by="seed-u40",
        title="Nangloi Railway underpass floods 4 feet — ambulance route blocked, pump broken",
        public_summary="Railway underpass floods to 4 feet after moderate rain. Only ambulance route to Nangloi hospital. Drainage pump station non-functional.",
        ai_summary="Underpass flood due to pump failure. IFCD + PWD. Emergency access blocked.",
        ai_confidence=0.90, status="in_progress",
        latitude=28.6818, longitude=77.0526,
        local_body_type="MCD", ward_no=99, ward_name="Nangloi Jat",
        locality_name="Nangloi Railway Underpass",
        issue_category_slug="water_sewer_drainage", issue_type_slug="waterlogging",
        asset_type_slug="roadside_storm_drain", severity="critical", urgency_score=9.4,
        corroboration_count=21, total_report_count=22, total_evidence_count=24,
        last_corroborated_at=now - timedelta(hours=1),
        obstruction_flag=True, public_safety_flag=True, road_class="arterial",
        primary_authority_slug="ifcd", secondary_authority_slug="pwd",
        routing_confidence=0.92, drain_type="roadside_storm_drain",
        created_at=now - timedelta(days=3),
    ), desc="Underpass 4 feet in water. Ambulance couldn't reach hospital. Baby delivered in auto-rickshaw nearby last week.",
       imgs=_imgs("waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 21}),
                     ("urgency_score_updated", "system", {"score": 9.4}),
                     ("pump_engineer_dispatched", "authority",
                      {"note": "Mobile pump deployed; permanent pump under repair"})])

    # 41 · Mangolpuri Block H — pack of 15 dogs, 3 children bitten (high, assigned)
    make(IssueRecord(
        original_report_id="seed-r41", created_by="seed-u41",
        title="Pack of 15 stray dogs — 3 children bitten in one week — Mangolpuri Block H",
        public_summary="Aggressive dog pack near school bus stop. 3 children bitten this week. Anti-rabies shots administered. Police also informed.",
        ai_summary="High-aggression stray dog pack near school. MCD public health + Delhi Police.",
        ai_confidence=0.88, status="assigned",
        latitude=28.6970, longitude=77.0752,
        local_body_type="MCD", ward_no=97, ward_name="Mangolpuri",
        locality_name="Mangolpuri Block H",
        issue_category_slug="public_safety_hazard", issue_type_slug="stray_dog_issue",
        severity="high", urgency_score=8.6,
        corroboration_count=11, total_report_count=12, total_evidence_count=11,
        last_corroborated_at=now - timedelta(hours=4),
        public_safety_flag=True, health_hazard_flag=True,
        primary_authority_slug="mcd_public_health", secondary_authority_slug="delhi_police",
        routing_confidence=0.89,
        created_at=now - timedelta(days=4),
    ), desc="3 kids bitten near school bus stop this week. Anti-rabies Rs 2000 each. Delhi Police informed. Please trap them.",
       imgs=_imgs("stray_dog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 11}),
                     ("urgency_score_updated", "system", {"score": 8.6}),
                     ("field_visit_scheduled", "authority",
                      {"team": "Animal Control Unit", "date": "Tomorrow 7am"})])

    # 42 · Sultanpuri E-Block — 8 days no garbage collection (medium, submitted)
    make(IssueRecord(
        original_report_id="seed-r42", created_by="seed-u42",
        title="No garbage truck for 8 days — Sultanpuri E-Block",
        public_summary="Residential waste piling for 8 days. 5 bins overflowing. Rats in broad daylight. Driver sick, no substitute sent.",
        ai_summary="Extended garbage collection failure. MCD sanitation.",
        ai_confidence=0.90, status="submitted",
        latitude=28.6990, longitude=77.0671,
        local_body_type="MCD", ward_no=96, ward_name="Sultanpuri",
        locality_name="Sultanpuri E-Block",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="medium", urgency_score=5.6,
        corroboration_count=9, total_report_count=10, total_evidence_count=10,
        last_corroborated_at=now - timedelta(hours=5),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.91,
        created_at=now - timedelta(days=8),
    ), desc="8 days no garbage pickup. Driver on leave, nobody substituted. Rats visible even in afternoon.",
       imgs=_imgs("garbage"))

    # ── SOUTH WEST DELHI (new) ────────────────────────────────────────────

    # 43 · Uttam Nagar East — truck overturned in NH-10 pothole (critical, in_progress)
    make(IssueRecord(
        original_report_id="seed-r43", created_by="seed-u43",
        title="Loaded truck overturned in NH-10 pothole — 2 workers injured, Uttam Nagar",
        public_summary="Loaded truck overturned in a 50cm pothole on NH-10 service road. 2 workers injured. Traffic blocked 6+ hours.",
        ai_summary="Major pothole on national highway service road caused truck rollover. PWD + NHAI.",
        ai_confidence=0.92, status="in_progress",
        latitude=28.6198, longitude=77.0484,
        local_body_type="MCD", ward_no=115, ward_name="Uttam Nagar",
        locality_name="Uttam Nagar East - NH-10 Service Road",
        issue_category_slug="roads_streets", issue_type_slug="pothole_major_road",
        asset_type_slug="arterial_road", severity="critical", urgency_score=9.2,
        corroboration_count=14, total_report_count=15, total_evidence_count=17,
        last_corroborated_at=now - timedelta(hours=2),
        obstruction_flag=True, public_safety_flag=True, road_class="arterial",
        primary_authority_slug="pwd", secondary_authority_slug="nhai",
        routing_confidence=0.88,
        created_at=now - timedelta(hours=10),
    ), desc="Truck overturned in pothole. 2 workers injured. Road blocked 6 hours. NHAI and PWD must fix this now.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 14}),
                     ("urgency_score_updated", "system", {"score": 9.2}),
                     ("authority_acknowledged", "authority",
                      {"note": "PWD road crew en route, NHAI informed"})])

    # 44 · Vikaspuri Main Market — public toilet locked 3 weeks (medium, submitted)
    make(IssueRecord(
        original_report_id="seed-r44", created_by="seed-u44",
        title="Community toilet block locked and abandoned for 3 weeks — Vikaspuri Market",
        public_summary="MCD toilet block near market locked for 3 weeks. Workers and shoppers using open ground behind it. Sanitation crisis.",
        ai_summary="Public toilet closure causing open defecation. MCD sanitation.",
        ai_confidence=0.83, status="submitted",
        latitude=28.6320, longitude=77.0751,
        local_body_type="MCD", ward_no=112, ward_name="Vikaspuri",
        locality_name="Vikaspuri Main Market",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        severity="medium", urgency_score=4.7,
        corroboration_count=7, total_report_count=8, total_evidence_count=7,
        last_corroborated_at=now - timedelta(hours=7),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.86,
        created_at=now - timedelta(days=21),
    ), desc="Public toilet locked 3 weeks. Nobody knows who has the key. Workers openly defecating behind it.",
       imgs=_imgs("garbage"))

    # 45 · Palam Village DDA Park — community toilet sewage flowing into park (high, submitted)
    make(IssueRecord(
        original_report_id="seed-r45", created_by="seed-u45",
        title="Community toilet sewage pipe discharging raw effluent into DDA park — Palam Village",
        public_summary="Overflow pipe from community toilet discharging raw sewage into DDA park. Children's play area fully contaminated.",
        ai_summary="Sewage discharge into public park. DJB toilet maintenance + DDA park authority.",
        ai_confidence=0.87, status="submitted",
        latitude=28.5919, longitude=77.0738,
        local_body_type="MCD", ward_no=126, ward_name="Palam",
        locality_name="Palam Village - DDA Park",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="high", urgency_score=7.8,
        corroboration_count=8, total_report_count=8, total_evidence_count=9,
        last_corroborated_at=now - timedelta(hours=5),
        health_hazard_flag=True, drain_type="sewer",
        primary_authority_slug="djb", secondary_authority_slug="dda",
        routing_confidence=0.85,
        created_at=now - timedelta(days=4),
    ), desc="Toilet sewage running directly into the park where children play. Entire park smells like open sewer.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 8}),
                     ("urgency_score_updated", "system", {"score": 7.8})])

    # ── WEST DELHI (new) ───────────────────────────────────────────────────

    # 46 · Naraina Phase I — industrial effluent, fish kill (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r46", created_by="seed-u46",
        title="Black industrial effluent poisoning storm drain — fish kill — Naraina Phase I",
        public_summary="Black foamy industrial discharge from factory outlet into storm drain. Fish dead in nearby pond. Residents reporting nausea.",
        ai_summary="Industrial pollution in municipal drain. MCD public health + PWD. Environmental hazard.",
        ai_confidence=0.85, status="submitted",
        latitude=28.6293, longitude=77.1421,
        local_body_type="MCD", ward_no=91, ward_name="Naraina",
        locality_name="Naraina Phase I Industrial Area",
        issue_category_slug="public_safety_hazard", issue_type_slug="clogged_local_drain",
        asset_type_slug="local_open_drain", severity="critical", urgency_score=8.7,
        corroboration_count=10, total_report_count=11, total_evidence_count=13,
        last_corroborated_at=now - timedelta(hours=3),
        health_hazard_flag=True, drain_type="local_open_drain",
        primary_authority_slug="mcd_public_health", secondary_authority_slug="pwd",
        routing_confidence=0.84,
        created_at=now - timedelta(days=3),
    ), desc="Black foamy liquid pouring from factory into drain. Fish in pond are dead. Kids playing near it.",
       imgs=_imgs("contaminated", "waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 10}),
                     ("urgency_score_updated", "system", {"score": 8.7})])

    # 47 · Paschim Vihar B Block — 30yr water main burst, road collapsed (high, in_progress)
    make(IssueRecord(
        original_report_id="seed-r47", created_by="seed-u47",
        title="30-year water main burst — 3m road collapse — Paschim Vihar B Block",
        public_summary="Old water main burst, washing out road subgrade. 3m road collapse on main colony road. 180 families without water.",
        ai_summary="Water main failure causing road collapse. DJB pipe + PWD road. Joint repair needed.",
        ai_confidence=0.93, status="in_progress",
        latitude=28.6693, longitude=77.1108,
        local_body_type="MCD", ward_no=88, ward_name="Paschim Vihar",
        locality_name="Paschim Vihar B Block",
        issue_category_slug="water_sewer_drainage", issue_type_slug="no_water_supply",
        asset_type_slug="water_pipeline", severity="high", urgency_score=8.0,
        corroboration_count=12, total_report_count=13, total_evidence_count=14,
        last_corroborated_at=now - timedelta(hours=4),
        health_hazard_flag=True, obstruction_flag=True,
        primary_authority_slug="djb", secondary_authority_slug="pwd",
        routing_confidence=0.91,
        created_at=now - timedelta(days=2),
    ), desc="Old pipeline burst. Road sank 1.5 feet. 180 families no water. Tanker water not sufficient.",
       imgs=_imgs("waterlog", "pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 12}),
                     ("joint_inspection_done", "authority",
                      {"teams": ["DJB", "PWD"], "note": "Pipe isolated, road repair starting tomorrow"})])

    # ── EAST DELHI (new) ───────────────────────────────────────────────────

    # 48 · Geeta Colony — open manhole at school gate, 500 kids daily (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r48", created_by="seed-u48",
        title="Open sewer manhole with stolen cover — at Geeta Colony school gate",
        public_summary="Manhole cover missing right at the school gate for 4 days. 500+ children pass daily.",
        ai_summary="Uncovered sewer manhole at school entrance. Immediate child safety risk. DJB.",
        ai_confidence=0.95, status="submitted",
        latitude=28.6510, longitude=77.2730,
        local_body_type="MCD", ward_no=161, ward_name="Geeta Colony",
        locality_name="Geeta Colony - Bhola Nath Nagar Road",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="critical", urgency_score=9.5,
        corroboration_count=9, total_report_count=9, total_evidence_count=11,
        last_corroborated_at=now - timedelta(hours=2),
        obstruction_flag=True, public_safety_flag=True,
        primary_authority_slug="djb", routing_confidence=0.94,
        created_at=now - timedelta(days=4),
    ), desc="Open manhole right at school gate. 500 students pass every morning. A child almost fell in today.",
       imgs=_imgs("sewer"),
       extra_events=[("issue_corroborated", "citizen", {"count": 9}),
                     ("urgency_score_updated", "system", {"score": 9.5})])

    # 49 · Patparganj I.P. Extension — sewer backs into homes every rain (high, in_progress)
    make(IssueRecord(
        original_report_id="seed-r49", created_by="seed-u49",
        title="Sewer backs into ground-floor homes every rain — Patparganj I.P. Extension",
        public_summary="Every time it rains, sewage backs up into ground-floor flats in I.P. Extension Pocket 1. Documented for 2 years.",
        ai_summary="Sewer back-pressure into residential units. DJB + IFCD.",
        ai_confidence=0.88, status="in_progress",
        latitude=28.6210, longitude=77.3050,
        local_body_type="MCD", ward_no=164, ward_name="Patparganj",
        locality_name="Patparganj I.P. Extension Pocket 1",
        issue_category_slug="water_sewer_drainage", issue_type_slug="sewer_overflow",
        asset_type_slug="sewer_line", severity="high", urgency_score=7.6,
        corroboration_count=11, total_report_count=13, total_evidence_count=14,
        last_corroborated_at=now - timedelta(hours=6),
        health_hazard_flag=True, drain_type="sewer",
        primary_authority_slug="djb", secondary_authority_slug="ifcd",
        routing_confidence=0.87,
        created_at=now - timedelta(days=11),
    ), desc="Sewage enters our house every time it rains. Ground floor flooded with sewer water. 5 families, 2 years.",
       imgs=_imgs("sewer", "waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 11}),
                     ("cctv_inspection_done", "authority",
                      {"note": "Camera shows sag in main sewer, dewatering needed"})])

    # 50 · Kondli T-junction — 2-year garbage blackspot, chronic reopened (medium, assigned)
    make(IssueRecord(
        original_report_id="seed-r50", created_by="seed-u50",
        title="Chronic 2-year garbage blackspot at Kondli T-junction — self-cleaned 3x, always returns",
        public_summary="Permanent illegal dumping point opposite Shiv Mandir. 2 years of complaints. Community self-cleaned 3 times. Back within days each time.",
        ai_summary="Chronic garbage blackspot. Enforcement failure. CCTV recommended. MCD sanitation.",
        ai_confidence=0.86, status="assigned",
        latitude=28.6081, longitude=77.3190,
        local_body_type="MCD", ward_no=175, ward_name="Kondli",
        locality_name="Kondli - T-Junction near Shiv Mandir",
        issue_category_slug="garbage_sanitation", issue_type_slug="illegal_dumping",
        asset_type_slug="garbage_blackspot", severity="medium", urgency_score=4.3,
        corroboration_count=7, total_report_count=10, total_evidence_count=9,
        last_corroborated_at=now - timedelta(hours=8),
        health_hazard_flag=True,
        primary_authority_slug="mcd_sanitation", routing_confidence=0.88,
        created_at=now - timedelta(days=730),
    ), desc="This blackspot exists 2+ years. Cleaned 3 times ourselves. It refills within a week every time.",
       imgs=_imgs("garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 7}),
                     ("resolved", "authority", {"note": "Area cleared"}),
                     ("reopened", "citizen", {"note": "Back to the same within 1 week"}),
                     ("field_visit_scheduled", "authority", {"note": "CCTV camera deployment proposed"})])

    # 51 · Trilokpuri Block 22 — DDA compound wall collapsed (medium, submitted)
    make(IssueRecord(
        original_report_id="seed-r51", created_by="seed-u51",
        title="DDA compound wall debris blocking service lane — Trilokpuri Block 22-23",
        public_summary="Old DDA boundary wall fell, blocking service lane between blocks 22 and 23. Emergency exit to main road inaccessible.",
        ai_summary="Collapsed boundary wall blocking access lane. DDA structural + MCD debris removal.",
        ai_confidence=0.80, status="submitted",
        latitude=28.6190, longitude=77.3050,
        local_body_type="MCD", ward_no=177, ward_name="Trilokpuri",
        locality_name="Trilokpuri Block 22",
        issue_category_slug="public_safety_hazard", issue_type_slug="road_obstruction",
        severity="medium", urgency_score=5.1,
        corroboration_count=4, total_report_count=4, total_evidence_count=4,
        obstruction_flag=True,
        primary_authority_slug="dda", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.77,
        created_at=now - timedelta(days=4),
    ), desc="Old boundary wall fell in rain. Debris blocking only back lane. Fire truck cannot pass.",
       imgs=_imgs("footpath"))

    # ── NORTH EAST DELHI (new) ────────────────────────────────────────────

    # 52 · Gokulpuri — 7 potholes in 100m, car axle snapped (high, in_progress)
    make(IssueRecord(
        original_report_id="seed-r52", created_by="seed-u52",
        title="7 potholes in 100m — car axle snapped — Gokulpuri Ring Road connector",
        public_summary="Pothole cluster on Ring Road connector near Gokulpuri metro. Car axle snapped yesterday. Two-wheelers swerving dangerously.",
        ai_summary="Pothole cluster on Ring Road connector. PWD jurisdiction.",
        ai_confidence=0.87, status="in_progress",
        latitude=28.6920, longitude=77.2986,
        local_body_type="MCD", ward_no=64, ward_name="Gokulpuri",
        locality_name="Gokulpuri - Ring Road Connector",
        issue_category_slug="roads_streets", issue_type_slug="pothole_major_road",
        asset_type_slug="arterial_road", severity="high", urgency_score=7.3,
        corroboration_count=9, total_report_count=10, total_evidence_count=10,
        last_corroborated_at=now - timedelta(hours=5),
        public_safety_flag=True, road_class="arterial",
        primary_authority_slug="pwd", routing_confidence=0.89,
        created_at=now - timedelta(days=5),
    ), desc="Car axle broke in a pothole near Gokulpuri metro. Bikes swerving to avoid them and hitting each other.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 9}),
                     ("repair_scheduled", "authority", {"date": "Next 3 days"})])

    # 53 · Nand Nagri Block E — 4-day water cut, disputed jurisdiction (high, manual_review)
    make(IssueRecord(
        original_report_id="seed-r53", created_by="seed-u53",
        title="4-day water cut — DJB denies responsibility — tanker mafia Rs 800/1000L",
        public_summary="No municipal water 4 days. DJB says area is served by private cooperative. Cooperative denies maintenance. Tankers price-gouging at Rs 800/1000L.",
        ai_summary="Water supply gap with disputed jurisdiction. DJB + DDA. Manual review needed.",
        ai_confidence=0.52, status="manual_review",
        latitude=28.7076, longitude=77.2893,
        local_body_type="MCD", ward_no=62, ward_name="Nand Nagri",
        locality_name="Nand Nagri Block E",
        issue_category_slug="water_sewer_drainage", issue_type_slug="no_water_supply",
        asset_type_slug="water_pipeline", severity="high", urgency_score=8.2,
        corroboration_count=19, total_report_count=20, total_evidence_count=18,
        last_corroborated_at=now - timedelta(hours=3),
        health_hazard_flag=True,
        primary_authority_slug="djb", secondary_authority_slug="dda",
        routing_confidence=0.52, routing_reason={"rule": "disputed_jurisdiction_manual"},
        created_at=now - timedelta(days=4),
    ), desc="DJB says cooperative must supply. Cooperative says DJB pipe is broken. No water 4 days. Tankers gouging us.",
       imgs=_imgs("water_supply"),
       extra_events=[("issue_corroborated", "citizen", {"count": 19}),
                     ("urgency_score_updated", "system", {"score": 8.2}),
                     ("djb_rejection", "authority", {"note": "Area not under DJB direct supply zone"}),
                     ("manual_review_triggered", "system", {"reason": "Disputed jurisdiction, high corroboration"})])

    # 54 · Seemapuri Industrial Pocket — dengue outbreak, open drain (critical, submitted)
    make(IssueRecord(
        original_report_id="seed-r54", created_by="seed-u54",
        title="Blocked industrial drain — stagnant 2 weeks — 12 dengue cases — Seemapuri",
        public_summary="Open drain behind industrial units completely blocked. Stagnant water 2+ weeks. Health centre reports 12 dengue cases from this micro-area.",
        ai_summary="Industrial drain with dengue breeding. MCD public health + IFCD. Disease outbreak.",
        ai_confidence=0.91, status="submitted",
        latitude=28.6832, longitude=77.3125,
        local_body_type="MCD", ward_no=66, ward_name="Seemapuri",
        locality_name="Seemapuri Industrial Pocket",
        issue_category_slug="public_safety_hazard", issue_type_slug="clogged_local_drain",
        asset_type_slug="local_open_drain", severity="critical", urgency_score=9.3,
        corroboration_count=15, total_report_count=16, total_evidence_count=16,
        last_corroborated_at=now - timedelta(hours=2),
        health_hazard_flag=True, drain_type="local_open_drain",
        primary_authority_slug="mcd_public_health", secondary_authority_slug="ifcd",
        routing_confidence=0.90,
        created_at=now - timedelta(days=6),
    ), desc="12 dengue cases from our area. Open drain behind factory has standing water for 2 weeks. No fogging.",
       imgs=_imgs("waterlog", "garbage"),
       extra_events=[("issue_corroborated", "citizen", {"count": 15}),
                     ("urgency_score_updated", "system", {"score": 9.3})])

    # ── SHAHDARA (new localities) ─────────────────────────────────────────

    # 55 · Dilshad Garden Block D — tree fell on 2 cars, gate blocked (high, in_progress)
    make(IssueRecord(
        original_report_id="seed-r55", created_by="seed-u55",
        title="Eucalyptus fell on 2 cars — only entry gate blocked — Dilshad Garden Block D",
        public_summary="Eucalyptus uprooted in storm, crushing 2 parked cars and blocking the only entry gate to Block D. Residents trapped.",
        ai_summary="Tree hazard blocking road and colony access gate. MCD horticulture + engineering.",
        ai_confidence=0.90, status="in_progress",
        latitude=28.6823, longitude=77.3123,
        local_body_type="MCD", ward_no=185, ward_name="Dilshad Garden",
        locality_name="Dilshad Garden Block D",
        issue_category_slug="parks_public_space", issue_type_slug="tree_hazard",
        asset_type_slug="tree", severity="high", urgency_score=8.1,
        corroboration_count=7, total_report_count=8, total_evidence_count=8,
        last_corroborated_at=now - timedelta(hours=3),
        obstruction_flag=True, public_safety_flag=True,
        primary_authority_slug="mcd_horticulture", secondary_authority_slug="mcd_engineering",
        routing_confidence=0.91,
        created_at=now - timedelta(hours=12),
    ), desc="Tree fell on 2 cars last night. Entire colony blocked. Ambulance cannot enter. MCD please come with chainsaw.",
       imgs=_imgs("tree"),
       extra_events=[("issue_corroborated", "citizen", {"count": 7}),
                     ("authority_acknowledged", "authority",
                      {"note": "Horticulture team dispatched, ETA 1 hour"})])

    # 56 · Ghonda Extension — cracked footbridge over nullah (medium, submitted)
    make(IssueRecord(
        original_report_id="seed-r56", created_by="seed-u56",
        title="Cracked footbridge over nullah — railing missing — Ghonda Extension",
        public_summary="Only footbridge over main nullah has cracked railing and buckled deck. 300+ residents use it daily. Alternate route adds 2km.",
        ai_summary="Damaged footbridge over drain. MCD engineering + IFCD.",
        ai_confidence=0.80, status="submitted",
        latitude=28.6910, longitude=77.3110,
        local_body_type="MCD", ward_no=186, ward_name="Ghonda",
        locality_name="Ghonda Extension - Nullah Bridge",
        issue_category_slug="roads_streets", issue_type_slug="broken_footpath",
        asset_type_slug="footpath", severity="medium", urgency_score=5.5,
        corroboration_count=5, total_report_count=5, total_evidence_count=5,
        last_corroborated_at=now - timedelta(hours=9),
        public_safety_flag=True,
        primary_authority_slug="mcd_engineering", secondary_authority_slug="ifcd",
        routing_confidence=0.78,
        created_at=now - timedelta(days=14),
    ), desc="Bridge is cracking. Railing gone. Elderly and schoolkids cross it daily. Will collapse soon.",
       imgs=_imgs("footpath"),
       extra_events=[("issue_corroborated", "citizen", {"count": 5})])

    # ── NDMC / CANTONMENT / NEW DELHI (new) ─────────────────────────────

    # 57 · Sarojini Nagar — Sunday market garbage, fastest-ever NDMC clearance (resolved)
    make(IssueRecord(
        original_report_id="seed-r57", created_by="seed-u57",
        title="Post-Sunday market garbage — Sarojini Nagar [RESOLVED IN 6 HOURS]",
        public_summary="Resolved in 6 hours. After Sunday flea market, NDMC deployed 4 trucks and cleared 8 tonnes of waste by 6pm — exemplary.",
        ai_summary="Post-market garbage cleared by NDMC within 6 hours.",
        ai_confidence=0.84, status="resolved",
        latitude=28.5758, longitude=77.1990,
        local_body_type="NDMC", ward_no=3, ward_name="Sarojini Nagar",
        locality_name="Sarojini Nagar Market",
        issue_category_slug="garbage_sanitation", issue_type_slug="garbage_not_collected",
        asset_type_slug="community_bin", severity="medium", urgency_score=1.0,
        corroboration_count=4, total_report_count=4, total_evidence_count=4,
        primary_authority_slug="ndmc_sanitation", routing_confidence=0.90,
        created_at=now - timedelta(days=3),
    ), desc="Post Sunday market chaos. 8 tonnes garbage. NDMC cleared all of it in 6 hours — very impressed.",
       imgs=_imgs("garbage"),
       extra_events=[("authority_acknowledged", "authority", {"note": "4 trucks deployed immediately"}),
                     ("resolved", "authority", {"note": "8T cleared, lanes washed, disinfected by 6pm"}),
                     ("resolution_confirmed", "citizen",
                      {"rating": 5, "note": "Best NDMC response I have seen!"})])

    # 58 · Chanakyapuri Shantipatha — embassy road drain blocked (medium, in_progress)
    make(IssueRecord(
        original_report_id="seed-r58", created_by="seed-u58",
        title="Storm drain blocked by construction debris — embassy zone flooding, Chanakyapuri",
        public_summary="Storm drain on Shantipatha blocked by construction debris. Embassy compounds flooded in last rain. Diplomatic protocol concern raised.",
        ai_summary="Storm drain blockage in embassy zone. PWD + NDMC civil.",
        ai_confidence=0.83, status="in_progress",
        latitude=28.5982, longitude=77.1907,
        local_body_type="NDMC", ward_no=4, ward_name="Chanakyapuri",
        locality_name="Chanakyapuri - Shantipatha",
        issue_category_slug="water_sewer_drainage", issue_type_slug="clogged_local_drain",
        asset_type_slug="roadside_storm_drain", severity="medium", urgency_score=5.0,
        corroboration_count=3, total_report_count=3, total_evidence_count=3,
        drain_type="roadside_storm_drain",
        primary_authority_slug="pwd", secondary_authority_slug="ndmc_civil",
        routing_confidence=0.81,
        created_at=now - timedelta(days=5),
    ), desc="Construction debris blocking storm drain on embassy road. Multiple compounds flooded last rain.",
       imgs=_imgs("waterlog"),
       extra_events=[("issue_corroborated", "citizen", {"count": 3}),
                     ("diplomatic_note_raised", "authority",
                      {"note": "MEA protocol team informed; PWD team on site"})])

    # 59 · Khan Market back lane — 60cm sinkhole overnight (high, assigned)
    make(IssueRecord(
        original_report_id="seed-r59", created_by="seed-u59",
        title="60cm sinkhole opened overnight — Khan Market back service lane",
        public_summary="Sinkhole in busy Khan Market back service lane. Suspected underground utility failure. High foot traffic. Deliveries blocked.",
        ai_summary="Road sinkhole in commercial area. NDMC civil + DJB utility check.",
        ai_confidence=0.89, status="assigned",
        latitude=28.6002, longitude=77.2290,
        local_body_type="NDMC", ward_no=5, ward_name="New Delhi",
        locality_name="Khan Market Back Service Lane",
        issue_category_slug="roads_streets", issue_type_slug="road_obstruction",
        asset_type_slug="local_lane", severity="high", urgency_score=7.2,
        corroboration_count=6, total_report_count=6, total_evidence_count=7,
        last_corroborated_at=now - timedelta(hours=5),
        obstruction_flag=True, public_safety_flag=True,
        primary_authority_slug="ndmc_civil", secondary_authority_slug="djb",
        routing_confidence=0.87,
        created_at=now - timedelta(days=1),
    ), desc="Huge sinkhole appeared overnight. Delivery vehicles blocked. Dangerous for pedestrians.",
       imgs=_imgs("pothole"),
       extra_events=[("issue_corroborated", "citizen", {"count": 6}),
                     ("field_visit_completed", "authority",
                      {"note": "Barricades placed, utility scan ordered"})])

    # 60 · Delhi Cantonment boundary road — broken streetlight (low, submitted)
    make(IssueRecord(
        original_report_id="seed-r60", created_by="seed-u60",
        title="Streetlight dark for 2 weeks — Delhi Cantonment boundary road",
        public_summary="Single streetlight on cantonment boundary road near Ring Road non-functional for 2 weeks. Late commuters reporting safety concern.",
        ai_summary="Streetlight failure on DCB-jurisdiction road. Delhi Cantonment Board.",
        ai_confidence=0.76, status="submitted",
        latitude=28.5933, longitude=77.1356,
        local_body_type="MCD", ward_no=200, ward_name="Delhi Cantonment",
        locality_name="Delhi Cantonment Boundary Road",
        issue_category_slug="lights_electrical", issue_type_slug="streetlight_not_working",
        severity="low", urgency_score=2.5,
        corroboration_count=2, total_report_count=2, total_evidence_count=2,
        public_safety_flag=True,
        primary_authority_slug="dcb_civic", routing_confidence=0.77,
        created_at=now - timedelta(days=14),
    ), desc="Streetlight gone for 2 weeks on cantonment boundary road. Very dark at night. Purse snatching happened once.",
       imgs=_imgs("streetlight"))

    return out
