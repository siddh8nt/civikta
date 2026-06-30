"""CIVIKTA Analytics Agent — Gemini function-calling loop for oversight intelligence.

Gemini is given 16 tools covering every analytical angle of Delhi civic governance.
It autonomously decides which tools to call, in what order, to answer any
natural-language governance question from oversight officials.

Tool inventory:
  get_issue_stats          — aggregate stats with flexible filters
  get_issue_detail         — full expanded view of one specific issue
  search_issues            — advanced filtered/sorted issue list
  get_authority_scorecard  — deep audit of one authority
  get_authority_comparison — side-by-side multi-authority comparison
  get_category_breakdown   — issue distribution by category/type
  get_ward_health_scores   — health scores per ward with false closure data
  get_zone_comparison      — all zones ranked on all governance metrics
  get_sla_analysis         — SLA breach analysis (who is late, by how much)
  get_escalation_analysis  — false closure & reopen pattern analysis
  get_stalled_issues       — issues stuck in intermediate status (no movement)
  get_chronic_hotspots     — locations/wards where same problems keep recurring
  get_rejection_analysis   — rejected issues with corroboration context
  get_safety_hazard_report — all open safety/health critical issues
  get_unrouted_issues      — issues with no authority assigned (routing gaps)
  get_citizen_engagement          — corroboration, participation, and trust metrics
  get_trend_analysis              — time-bucketed filing and resolution trend data
  get_commissioner_accountability — issues grouped by MCD zonal commissioner (accountability layer)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Any

from app.llm.base import LLMClient
from app.repositories.base import Repository
from app.models.issue import IssueRecord

log = logging.getLogger(__name__)

# ── SLA targets by severity (hours) ───────────────────────────────────────────
_SLA_HOURS: dict[str, int] = {
    "critical": 24,
    "high": 72,
    "medium": 168,   # 7 days
    "low": 336,      # 14 days
}

_OPEN_STATUSES = {"submitted", "pending_verification", "assigned", "in_progress", "reopened"}
_CLOSED_STATUSES = {"resolved", "closed"}
_STALL_STATUSES = {"assigned", "in_progress", "pending_verification"}

_AUTHORITY_NAMES: dict[str, str] = {
    "mcd_sanitation":    "MCD Sanitation",
    "mcd_engineering":   "MCD Engineering",
    "mcd_horticulture":  "MCD Horticulture",
    "mcd_public_health": "MCD Public Health",
    "ndmc_sanitation":   "NDMC Sanitation",
    "ndmc_civil":        "NDMC Civil Works",
    "ndmc_horticulture": "NDMC Horticulture",
    "dcb_civic":         "Delhi Cantonment Board",
    "djb":               "Delhi Jal Board",
    "pwd":               "Public Works Department",
    "ifcd":              "Irrigation & Flood Control",
    "dda":               "Delhi Development Authority",
    "delhi_police":      "Delhi Police",
    "nhai":              "NHAI",
}

_SEV_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# MCD zonal commissioner assignments (Sep 2024)
_ZONE_COMMISSIONER: dict[str, dict] = {
    # Sachin Shinde — Additional Commissioner (West/Narela/Najafgarh)
    "Narela":     {"name": "Sachin Shinde", "email": "sachin.shinde@mcd.delhi.gov.in", "zones": ["Narela", "West", "Najafgarh"]},
    "West":       {"name": "Sachin Shinde", "email": "sachin.shinde@mcd.delhi.gov.in", "zones": ["Narela", "West", "Najafgarh"]},
    "Najafgarh":  {"name": "Sachin Shinde", "email": "sachin.shinde@mcd.delhi.gov.in", "zones": ["Narela", "West", "Najafgarh"]},
    # Jitender Yadav — Additional Commissioner (South/City-SP/Central)
    "South":      {"name": "Jitender Yadav", "email": "jitender.yadav@mcd.delhi.gov.in", "zones": ["South", "City SP", "Central"]},
    "City SP":    {"name": "Jitender Yadav", "email": "jitender.yadav@mcd.delhi.gov.in", "zones": ["South", "City SP", "Central"]},
    "Central":    {"name": "Jitender Yadav", "email": "jitender.yadav@mcd.delhi.gov.in", "zones": ["South", "City SP", "Central"]},
    # Nidhi Malik — Additional Commissioner (Rohini/North/South West)
    "Rohini":     {"name": "Nidhi Malik", "email": "nidhi.malik@mcd.delhi.gov.in", "zones": ["Rohini", "North", "South West"]},
    "North":      {"name": "Nidhi Malik", "email": "nidhi.malik@mcd.delhi.gov.in", "zones": ["Rohini", "North", "South West"]},
    "South West": {"name": "Nidhi Malik", "email": "nidhi.malik@mcd.delhi.gov.in", "zones": ["Rohini", "North", "South West"]},
    # Dr. Tariq Thomas — Additional Commissioner (Civil Lines/Karol Bagh)
    "Civil Lines": {"name": "Dr. Tariq Thomas", "email": "tariq.thomas@mcd.delhi.gov.in", "zones": ["Civil Lines", "Karol Bagh"]},
    "Karol Bagh":  {"name": "Dr. Tariq Thomas", "email": "tariq.thomas@mcd.delhi.gov.in", "zones": ["Civil Lines", "Karol Bagh"]},
    # Pankaj Naresh Agrawal — Additional Commissioner (Shahdara/East)
    "Shahdara":   {"name": "Pankaj Naresh Agrawal", "email": "pankaj.agrawal@mcd.delhi.gov.in", "zones": ["Shahdara", "East"]},
    "East":       {"name": "Pankaj Naresh Agrawal", "email": "pankaj.agrawal@mcd.delhi.gov.in", "zones": ["Shahdara", "East"]},
}

# ── System prompt ─────────────────────────────────────────────────────────────
_SYSTEM = """\
You are CIVIKTA's Oversight Intelligence Agent — an AI analyst embedded in Delhi's \
civic issue transparency platform.

Your role: answer ANY governance question from oversight officials using real-time \
data. You serve three purposes:
  1. AUDIT — evaluate authority performance: SLA, resolution quality, false closures
  2. ANALYSIS — hotspots, systemic failures, routing gaps, citizen trust
  3. POLICY — specific interventions, resource reallocation, structural changes

═══════════════════════════════════════════════
PLATFORM ARCHITECTURE
═══════════════════════════════════════════════
CIVIKTA has 3 stakeholder layers:
  • Citizen layer — files issues, corroborates, disputes resolutions
  • Authority layer — 14 departments across Delhi, receive and resolve issues
  • Oversight layer — you are here

ADMINISTRATIVE GEOGRAPHY:
  State (NCT Delhi) → Zone (12 MCD zones + NDMC/DCB) → Ward (250+ wards) → Locality

14 AUTHORITIES:
  MCD: mcd_sanitation, mcd_engineering, mcd_horticulture, mcd_public_health
  NDMC: ndmc_civil, ndmc_sanitation, ndmc_horticulture
  Others: dcb_civic, djb, pwd, ifcd, dda, delhi_police, nhai

KEY DATA FIELDS:
  urgency_score          — 1.0–10.0, computed from severity + corroborations + duration + safety
  corroboration_count    — citizens who independently confirmed the issue
  total_report_count     — total filings merged into this issue
  SLA targets            — critical:24h, high:72h, medium:7d, low:14d
  false_closure_suspected — resolved by authority, then disputed by citizens
  persistence_type       — new | recurring | chronic (same location repeatedly)
  status flow            — submitted → pending_verification → assigned → in_progress → resolved/rejected/closed
  reopened               — was resolved, citizen challenged, re-opened

ISSUE TYPE SLUGS for issue_type_slug filter:
  Roads: pothole, road_damage, road_cave_in, encroachment_road, footpath_damage
  Water: waterlogging, drain_overflow, sewer_overflow, water_supply_issue, pipe_burst, drain_blockage
  Garbage: garbage_dump, overflowing_bin, garbage_not_collected, dead_animal
  Lights: streetlight_outage, traffic_light_fault
  Safety: open_manhole, fallen_wire, construction_hazard
  Parks: park_damage, tree_fall, illegal_dumping_park

═══════════════════════════════════════════════
TOOL USAGE STRATEGY — match query to tool
═══════════════════════════════════════════════
• "Show me issue #XYZ" / expand a specific issue
  → get_issue_detail(issue_id)

• "Which issues are corroborated by 100+ people but unresolved?"
  → search_issues(min_corroborations=100, status="open")

• "What are the most urgent safety hazards right now?"
  → get_safety_hazard_report()  OR  search_issues(public_safety_only=True, sort_by="urgency")

• "Show issues stuck with no movement for weeks"
  → get_stalled_issues(min_days_stalled=14)

• "Which issues have no authority assigned?"
  → get_unrouted_issues()

• "Compare MCD Sanitation vs NDMC Sanitation"
  → get_authority_comparison(authority_slugs=["mcd_sanitation","ndmc_sanitation"])

• "Which ward/zone has worst false closure rate?"
  → get_ward_health_scores() [use worst_false_closure_wards field]
  OR get_escalation_analysis() [use false_closure_by_zone field]

• "Waterlogging / type-specific analysis"
  → search_issues(issue_type_slug="waterlogging") + get_sla_analysis(issue_type_slug="waterlogging")

• "Chronic problem locations / recurring issues"
  → get_chronic_hotspots()

• "Which rejected issues had high citizen support?"
  → get_rejection_analysis(min_corroborations=5)

• "Is the situation getting better or worse over time?"
  → get_trend_analysis(group_by="month")

• "How much do citizens trust the system? Engagement stats?"
  → get_citizen_engagement()

• "Zone-level comparison across all metrics"
  → get_zone_comparison()

• "Worst authority overall" or "SLA compliance ranking"
  → get_authority_comparison() or get_sla_analysis()

• "State-wide audit / executive summary"
  → get_issue_stats() + get_zone_comparison() + get_escalation_analysis() + get_sla_analysis()

• "Who is the commissioner responsible" / "Hold commissioner accountable" / "MCD official performance"
  → get_commissioner_accountability() — groups all zones by their Additional Commissioner

ALWAYS call tools before answering. Use 2–4 tools for complex questions.
For individual issue requests, always call get_issue_detail first.

═══════════════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════════════
Structure every response:
  ## FINDINGS — cite specific numbers and named entities
  ## ANALYSIS — root cause, why this matters
  ## RECOMMENDATIONS — specific, actionable, measurable

Be concrete:
  ✓ "MCD Engineering's Sangam Vihar ward has 23 open potholes, 15 SLA-breached, \
average 11 days overdue — deploy a dedicated repair crew for 2 weeks"
  ✗ "The authority should improve response times"

For individual issues: include full context — location, timeline, authority assigned, \
citizen engagement, SLA status, event history.
Use markdown: headers, bold, tables.
"""


class AnalyticsService:
    def __init__(self, repo: Repository, llm: LLMClient) -> None:
        self.repo = repo
        self.llm = llm

    # ── Public entry point ────────────────────────────────────────────────────
    async def query(
        self,
        question: str,
        context: dict | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        if not hasattr(self.llm, "_client"):
            return {
                "answer": (
                    "Analytics requires Gemini (CIVIKTA_LLM=gemini). "
                    "Set CIVIKTA_LLM=gemini and GCP_PROJECT in .env."
                ),
                "tool_calls": [],
                "suggested_questions": [],
            }
        return await self._gemini_loop(question, context or {}, history or [])

    # ── Gemini function-calling loop ──────────────────────────────────────────
    async def _gemini_loop(self, question: str, context: dict, history: list[dict]) -> dict:
        from google.genai import types as gt

        tools = [gt.Tool(function_declarations=self._declarations())]
        config = gt.GenerateContentConfig(
            system_instruction=_SYSTEM,
            tools=tools,
            temperature=0.3,
            max_output_tokens=3000,
        )

        ctx_prefix = ""
        if context:
            parts = []
            if context.get("authority_slug"):
                parts.append(f"authority: {_AUTHORITY_NAMES.get(context['authority_slug'], context['authority_slug'])}")
            if context.get("zone"):
                parts.append(f"zone: {context['zone']}")
            if context.get("ward_name"):
                parts.append(f"ward: {context['ward_name']}")
            if parts:
                ctx_prefix = f"[Context: {', '.join(parts)}]\n\n"

        contents: list = []
        for turn in history:
            role = "user" if turn["role"] == "user" else "model"
            contents.append(gt.Content(role=role, parts=[gt.Part.from_text(text=turn["text"])]))

        contents.append(
            gt.Content(role="user", parts=[gt.Part.from_text(text=ctx_prefix + question)])
        )

        tool_calls: list[dict] = []
        max_rounds = 8

        for _ in range(max_rounds):
            try:
                response = await self.llm._client.aio.models.generate_content(
                    model=self.llm._model,
                    contents=contents,
                    config=config,
                )
            except Exception as exc:
                err_str = str(exc)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    import re
                    retry_match = re.search(r"retry in ([\d.]+)s", err_str)
                    wait_str = f" Retry in {retry_match.group(1)}s." if retry_match else " Please wait a few seconds and try again."
                    return {
                        "answer": f"**Rate limit reached.** Gemini is receiving too many requests right now.{wait_str}",
                        "tool_calls": tool_calls,
                        "suggested_questions": [],
                    }
                log.error("Gemini loop error: %s", exc)
                return {
                    "answer": f"**Analysis failed.** Gemini returned an unexpected error. Please try a simpler question or retry in a moment.",
                    "tool_calls": tool_calls,
                    "suggested_questions": [],
                }

            candidate = response.candidates[0].content
            fc_parts = [p for p in candidate.parts if getattr(p, "function_call", None)]

            if not fc_parts:
                text_parts = [getattr(p, "text", "") for p in candidate.parts if getattr(p, "text", "")]
                answer = "\n".join(text_parts).strip()
                suggestions = await self._suggest_followups(question, answer)
                return {
                    "answer": answer,
                    "tool_calls": tool_calls,
                    "suggested_questions": suggestions,
                }

            contents.append(candidate)
            response_parts = []

            for part in fc_parts:
                fc = part.function_call
                name = fc.name
                args = dict(fc.args) if fc.args else {}
                result = self._dispatch(name, args)
                tool_calls.append({"name": name, "args": args, "result": result})
                response_parts.append(
                    gt.Part.from_function_response(name=name, response={"result": result})
                )

            contents.append(gt.Content(role="user", parts=response_parts))

        return {"answer": "Analysis exceeded tool call limit.", "tool_calls": tool_calls, "suggested_questions": []}

    # ── Follow-up suggestion generator ────────────────────────────────────────
    async def _suggest_followups(self, question: str, answer: str) -> list[str]:
        import json, re
        from google.genai import types as gt

        prompt = (
            "You are advising a Delhi civic oversight officer. "
            "Based on the question and analysis below, suggest exactly 4 short, specific follow-up questions "
            "the officer should ask next to dig deeper or drive action. "
            "Each question must be under 12 words.\n"
            "Return ONLY a valid JSON array of 4 strings, nothing else. Example:\n"
            '["Question one?", "Question two?", "Question three?", "Question four?"]\n\n'
            f"Question asked: {question}\n\n"
            f"Analysis (first 600 chars): {answer[:600]}"
        )
        try:
            response = await self.llm._client.aio.models.generate_content(
                model=self.llm._model,
                contents=prompt,
                config=gt.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=512,
                    thinking_config=gt.ThinkingConfig(thinking_budget=0),
                ),
            )
            raw = (response.text or "").strip()
            match = re.search(r'\[.*?\]', raw, re.DOTALL)
            if match:
                suggestions = json.loads(match.group())
                if isinstance(suggestions, list):
                    return [str(s) for s in suggestions[:4]]
        except Exception as exc:
            log.warning("Suggestion generation failed: %s", exc)
        return []

    # ── Tool dispatcher ───────────────────────────────────────────────────────
    def _dispatch(self, name: str, args: dict) -> Any:
        try:
            dispatch = {
                "get_issue_stats":          self._tool_issue_stats,
                "get_issue_detail":         self._tool_issue_detail,
                "search_issues":            self._tool_search_issues,
                "get_authority_scorecard":  self._tool_authority_scorecard,
                "get_authority_comparison": self._tool_authority_comparison,
                "get_category_breakdown":   self._tool_category_breakdown,
                "get_ward_health_scores":   self._tool_ward_health_scores,
                "get_zone_comparison":      self._tool_zone_comparison,
                "get_sla_analysis":         self._tool_sla_analysis,
                "get_escalation_analysis":  self._tool_escalation_analysis,
                "get_stalled_issues":       self._tool_stalled_issues,
                "get_chronic_hotspots":     self._tool_chronic_hotspots,
                "get_rejection_analysis":   self._tool_rejection_analysis,
                "get_safety_hazard_report": self._tool_safety_hazard_report,
                "get_unrouted_issues":      self._tool_unrouted_issues,
                "get_citizen_engagement":          self._tool_citizen_engagement,
                "get_trend_analysis":              self._tool_trend_analysis,
                "get_commissioner_accountability": self._tool_commissioner_accountability,
            }
            fn = dispatch.get(name)
            if fn is None:
                return {"error": f"Unknown tool: {name}"}
            return fn(**args)
        except Exception as exc:
            log.error("Tool %s failed: %s", name, exc)
            return {"error": str(exc)}

    # ═══════════════════════════════════════════════
    # TOOLS
    # ═══════════════════════════════════════════════

    # ── Tool: aggregate stats ─────────────────────────────────────────────────
    def _tool_issue_stats(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        ward_name: str | None = None,
        status: str | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
        severity: str | None = None,
        days_ago: int | None = None,
    ) -> dict:
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone, ward_name=ward_name,
            status=status, category=category, issue_type_slug=issue_type_slug,
            severity=severity, days_ago=days_ago,
        )
        now = datetime.now(timezone.utc)
        status_counts: dict[str, int] = defaultdict(int)
        sev_counts: dict[str, int] = defaultdict(int)
        for i in issues:
            status_counts[i.status] += 1
            sev_counts[i.severity] += 1

        open_issues = [i for i in issues if i.status in _OPEN_STATUSES]
        top_urgent = sorted(open_issues, key=lambda x: x.urgency_score, reverse=True)[:10]

        return {
            "total": len(issues),
            "open": len(open_issues),
            "resolved": status_counts.get("resolved", 0),
            "reopened": status_counts.get("reopened", 0),
            "rejected": status_counts.get("rejected", 0),
            "by_status": dict(status_counts),
            "by_severity": dict(sev_counts),
            "total_corroborations": sum(i.corroboration_count for i in issues),
            "avg_urgency_score": round(
                sum(i.urgency_score for i in open_issues) / len(open_issues), 2
            ) if open_issues else 0,
            "oldest_open_days": max(
                ((now - i.created_at).days for i in open_issues), default=0
            ),
            "chronic_count": sum(1 for i in issues if i.persistence_type == "chronic"),
            "safety_flag_count": sum(1 for i in issues if i.public_safety_flag or i.health_hazard_flag),
            "false_closure_count": sum(1 for i in issues if i.false_closure_suspected),
            "unrouted_count": sum(1 for i in issues if not i.primary_authority_slug),
            "top_urgent_issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "locality": i.locality_name,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", i.primary_authority_slug or "UNROUTED"),
                    "severity": i.severity,
                    "days_open": (now - i.created_at).days,
                    "urgency_score": i.urgency_score,
                    "corroborations": i.corroboration_count,
                    "category": i.issue_category_slug,
                    "type": i.issue_type_slug,
                    "public_safety": i.public_safety_flag,
                    "health_hazard": i.health_hazard_flag,
                    "status": i.status,
                    "false_closure": i.false_closure_suspected,
                }
                for i in top_urgent
            ],
        }

    # ── Tool: single issue deep dive ──────────────────────────────────────────
    def _tool_issue_detail(self, issue_id: str) -> dict:
        """Full expanded view of one issue — equivalent to the citizen issue detail screen."""
        issue = self.repo.get_issue(issue_id)
        if not issue:
            return {"error": f"Issue not found: {issue_id}"}

        now = datetime.now(timezone.utc)
        events = self.repo.list_events(issue_id)
        hrs_open = (now - issue.created_at).total_seconds() / 3600
        sla_target = _SLA_HOURS.get(issue.severity, 168)
        sla_breached = hrs_open > sla_target and issue.status in _OPEN_STATUSES

        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.canonical_description,
            "public_summary": issue.public_summary,
            "ai_summary": issue.ai_summary,
            "status": issue.status,
            "status_reason": issue.status_reason,
            "severity": issue.severity,
            "urgency_score": issue.urgency_score,
            "corroboration_count": issue.corroboration_count,
            "total_reports_merged": issue.total_report_count,
            "total_evidence_count": issue.total_evidence_count,
            "days_open": (now - issue.created_at).days,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "last_corroborated_at": issue.last_corroborated_at.isoformat() if issue.last_corroborated_at else None,
            "location": {
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "ward_name": issue.ward_name,
                "ward_no": issue.ward_no,
                "zone": issue.mcd_zone,
                "locality": issue.locality_name,
                "landmark": issue.landmark,
                "local_body_type": issue.local_body_type,
                "revenue_district": issue.revenue_district,
            },
            "classification": {
                "category": issue.issue_category_slug,
                "subcategory": issue.issue_subcategory_slug,
                "type": issue.issue_type_slug,
                "asset_type": issue.asset_type_slug,
                "persistence": issue.persistence_type,
            },
            "flags": {
                "obstruction": issue.obstruction_flag,
                "health_hazard": issue.health_hazard_flag,
                "public_safety": issue.public_safety_flag,
                "false_closure_suspected": issue.false_closure_suspected,
                "impact_tags": issue.impact_tags,
            },
            "authority": {
                "primary": _AUTHORITY_NAMES.get(issue.primary_authority_slug or "", issue.primary_authority_slug or "UNROUTED"),
                "primary_slug": issue.primary_authority_slug,
                "secondary": _AUTHORITY_NAMES.get(issue.secondary_authority_slug or "", issue.secondary_authority_slug) if issue.secondary_authority_slug else None,
                "routing_confidence": issue.routing_confidence,
                "routing_reason": issue.routing_reason,
            },
            "sla": {
                "target_hours": sla_target,
                "target_days": round(sla_target / 24, 1),
                "hours_open": round(hrs_open, 1),
                "sla_breached": sla_breached,
                "breach_by_hours": round(hrs_open - sla_target, 1) if sla_breached else 0,
            },
            "event_timeline": [
                {
                    "event_type": e.event_type,
                    "actor_type": e.actor_type,
                    "payload": e.payload,
                    "timestamp": e.created_at.isoformat(),
                }
                for e in events
            ],
        }

    # ── Tool: advanced issue search ───────────────────────────────────────────
    def _tool_search_issues(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        ward_name: str | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        days_ago: int | None = None,
        min_corroborations: int | None = None,
        max_corroborations: int | None = None,
        min_urgency_score: float | None = None,
        min_days_open: int | None = None,
        max_days_open: int | None = None,
        public_safety_only: bool = False,
        health_hazard_only: bool = False,
        obstruction_only: bool = False,
        false_closure_only: bool = False,
        chronic_only: bool = False,
        recurring_only: bool = False,
        unrouted_only: bool = False,
        sort_by: str = "urgency",
        limit: int = 20,
    ) -> dict:
        """Flexible issue search. sort_by: urgency|corroborations|days_open|severity|created_at"""
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone, ward_name=ward_name,
            category=category, issue_type_slug=issue_type_slug,
            severity=severity, status=status, days_ago=days_ago,
        )
        now = datetime.now(timezone.utc)

        result = []
        for i in issues:
            days_open = (now - i.created_at).days
            if min_corroborations is not None and i.corroboration_count < min_corroborations:
                continue
            if max_corroborations is not None and i.corroboration_count > max_corroborations:
                continue
            if min_urgency_score is not None and i.urgency_score < min_urgency_score:
                continue
            if min_days_open is not None and days_open < min_days_open:
                continue
            if max_days_open is not None and days_open > max_days_open:
                continue
            if public_safety_only and not i.public_safety_flag:
                continue
            if health_hazard_only and not i.health_hazard_flag:
                continue
            if obstruction_only and not i.obstruction_flag:
                continue
            if false_closure_only and not i.false_closure_suspected:
                continue
            if chronic_only and i.persistence_type != "chronic":
                continue
            if recurring_only and i.persistence_type not in ("recurring", "chronic"):
                continue
            if unrouted_only and i.primary_authority_slug:
                continue
            result.append(i)

        sort_key = {
            "urgency":        lambda x: x.urgency_score,
            "corroborations": lambda x: x.corroboration_count,
            "days_open":      lambda x: (now - x.created_at).days,
            "severity":       lambda x: _SEV_RANK.get(x.severity, 0),
            "created_at":     lambda x: x.created_at,
        }.get(sort_by, lambda x: x.urgency_score)

        result.sort(key=sort_key, reverse=True)
        total = len(result)
        result = result[:limit]

        return {
            "total_matching": total,
            "returned": len(result),
            "sort_by": sort_by,
            "filters_applied": {k: v for k, v in {
                "authority": authority_slug, "zone": zone, "ward": ward_name,
                "category": category, "issue_type": issue_type_slug, "severity": severity,
                "status": status, "min_corroborations": min_corroborations,
                "public_safety_only": public_safety_only or None,
                "false_closure_only": false_closure_only or None,
                "chronic_only": chronic_only or None,
            }.items() if v is not None},
            "issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "status": i.status,
                    "severity": i.severity,
                    "urgency_score": i.urgency_score,
                    "corroborations": i.corroboration_count,
                    "total_reports": i.total_report_count,
                    "days_open": (now - i.created_at).days,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "locality": i.locality_name,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", i.primary_authority_slug or "UNROUTED"),
                    "category": i.issue_category_slug,
                    "type": i.issue_type_slug,
                    "persistence": i.persistence_type,
                    "false_closure": i.false_closure_suspected,
                    "public_safety": i.public_safety_flag,
                    "health_hazard": i.health_hazard_flag,
                    "obstruction": i.obstruction_flag,
                    "last_corroborated": i.last_corroborated_at.isoformat() if i.last_corroborated_at else None,
                }
                for i in result
            ],
        }

    # ── Tool: authority scorecard ─────────────────────────────────────────────
    def _tool_authority_scorecard(self, authority_slug: str) -> dict:
        issues = self._filtered(authority_slug=authority_slug)
        if not issues:
            return {"error": f"No issues found for authority: {authority_slug}"}

        now = datetime.now(timezone.utc)
        open_i = [i for i in issues if i.status in _OPEN_STATUSES]
        resolved_i = [i for i in issues if i.status in _CLOSED_STATUSES]
        reopened_i = [i for i in issues if i.status == "reopened"]
        rejected_i = [i for i in issues if i.status == "rejected"]
        stalled_i = [
            i for i in issues
            if i.status in _STALL_STATUSES and (now - i.updated_at).days >= 7
        ]

        sla_breached = [
            i for i in open_i
            if (now - i.created_at).total_seconds() / 3600 > _SLA_HOURS.get(i.severity, 168)
        ]

        avg_res_days = 0.0
        if resolved_i:
            avg_res_days = round(
                sum((i.updated_at - i.created_at).days for i in resolved_i) / len(resolved_i), 1
            )

        false_closure = sum(1 for i in issues if i.false_closure_suspected)

        cat_counts: dict[str, int] = defaultdict(int)
        for i in issues:
            cat_counts[i.issue_category_slug or "unknown"] += 1
        top_categories = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        worst = sorted(open_i, key=lambda x: x.urgency_score, reverse=True)[:5]

        # Zone distribution
        zone_counts: dict[str, int] = defaultdict(int)
        for i in open_i:
            zone_counts[i.mcd_zone or "Unknown"] += 1

        return {
            "authority": _AUTHORITY_NAMES.get(authority_slug, authority_slug),
            "authority_slug": authority_slug,
            "total_assigned": len(issues),
            "open": len(open_i),
            "resolved": len(resolved_i),
            "reopened": len(reopened_i),
            "rejected": len(rejected_i),
            "stalled_7d": len(stalled_i),
            "resolution_rate_pct": round(len(resolved_i) / len(issues) * 100, 1) if issues else 0,
            "rejection_rate_pct": round(len(rejected_i) / len(issues) * 100, 1) if issues else 0,
            "sla_breach_count": len(sla_breached),
            "sla_breach_rate_pct": round(len(sla_breached) / len(open_i) * 100, 1) if open_i else 0,
            "avg_resolution_days": avg_res_days,
            "false_closure_count": false_closure,
            "false_closure_rate_pct": round(false_closure / len(resolved_i) * 100, 1) if resolved_i else 0,
            "chronic_issues": sum(1 for i in issues if i.persistence_type == "chronic"),
            "recurring_issues": sum(1 for i in issues if i.persistence_type in ("recurring", "chronic")),
            "total_corroborations": sum(i.corroboration_count for i in issues),
            "safety_flagged_open": sum(1 for i in open_i if i.public_safety_flag or i.health_hazard_flag),
            "top_categories": [{"category": k, "count": v} for k, v in top_categories],
            "open_by_zone": dict(sorted(zone_counts.items(), key=lambda x: x[1], reverse=True)),
            "worst_open_issues": [
                {"id": i.id, "title": i.title, "urgency": i.urgency_score,
                 "days_open": (now - i.created_at).days, "severity": i.severity,
                 "ward": i.ward_name, "corroborations": i.corroboration_count}
                for i in worst
            ],
        }

    # ── Tool: multi-authority comparison ──────────────────────────────────────
    def _tool_authority_comparison(
        self,
        authority_slugs: list[str] | None = None,
    ) -> dict:
        """Side-by-side comparison of multiple authorities. Defaults to all 14."""
        slugs = authority_slugs or list(_AUTHORITY_NAMES.keys())
        now = datetime.now(timezone.utc)
        rows = []

        for slug in slugs:
            issues = self._filtered(authority_slug=slug)
            if not issues:
                continue
            open_i = [i for i in issues if i.status in _OPEN_STATUSES]
            resolved_i = [i for i in issues if i.status in _CLOSED_STATUSES]
            sla_breached = [
                i for i in open_i
                if (now - i.created_at).total_seconds() / 3600 > _SLA_HOURS.get(i.severity, 168)
            ]
            false_closure = sum(1 for i in issues if i.false_closure_suspected)
            stalled = sum(
                1 for i in issues
                if i.status in _STALL_STATUSES and (now - i.updated_at).days >= 7
            )
            rows.append({
                "authority": _AUTHORITY_NAMES.get(slug, slug),
                "slug": slug,
                "total": len(issues),
                "open": len(open_i),
                "resolved": len(resolved_i),
                "resolution_rate_pct": round(len(resolved_i) / len(issues) * 100, 1) if issues else 0,
                "sla_breach_rate_pct": round(len(sla_breached) / len(open_i) * 100, 1) if open_i else 0,
                "false_closure_rate_pct": round(false_closure / len(resolved_i) * 100, 1) if resolved_i else 0,
                "stalled_7d": stalled,
                "chronic": sum(1 for i in issues if i.persistence_type == "chronic"),
                "avg_urgency": round(sum(i.urgency_score for i in open_i) / len(open_i), 2) if open_i else 0,
                "total_corroborations": sum(i.corroboration_count for i in issues),
            })

        # Rank each authority on key metrics
        rows.sort(key=lambda x: x["resolution_rate_pct"], reverse=True)
        best_resolution = rows[0]["authority"] if rows else "N/A"
        rows_by_sla = sorted(rows, key=lambda x: x["sla_breach_rate_pct"])
        best_sla = rows_by_sla[0]["authority"] if rows_by_sla else "N/A"

        return {
            "authorities_compared": len(rows),
            "best_resolution_rate": best_resolution,
            "best_sla_compliance": best_sla,
            "worst_resolution_rate": rows[-1]["authority"] if rows else "N/A",
            "worst_sla_compliance": rows_by_sla[-1]["authority"] if rows_by_sla else "N/A",
            "comparison_table": rows,
        }

    # ── Tool: category breakdown ──────────────────────────────────────────────
    def _tool_category_breakdown(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        ward_name: str | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
    ) -> dict:
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone, ward_name=ward_name,
            category=category, issue_type_slug=issue_type_slug,
        )
        cat: dict[str, dict] = defaultdict(lambda: {"total": 0, "open": 0, "critical": 0, "corroborations": 0, "chronic": 0})
        type_counts: dict[str, int] = defaultdict(int)

        for i in issues:
            c = i.issue_category_slug or "unknown"
            cat[c]["total"] += 1
            if i.status in _OPEN_STATUSES:
                cat[c]["open"] += 1
            if i.severity == "critical":
                cat[c]["critical"] += 1
            cat[c]["corroborations"] += i.corroboration_count
            if i.persistence_type == "chronic":
                cat[c]["chronic"] += 1
            type_counts[i.issue_type_slug or "unknown"] += 1

        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_issues": len(issues),
            "by_category": dict(sorted(cat.items(), key=lambda x: x[1]["total"], reverse=True)),
            "top_issue_types": [{"type": k, "count": v} for k, v in top_types],
            "safety_flags": {
                "obstruction": sum(1 for i in issues if i.obstruction_flag),
                "health_hazard": sum(1 for i in issues if i.health_hazard_flag),
                "public_safety": sum(1 for i in issues if i.public_safety_flag),
            },
        }

    # ── Tool: ward health scores ──────────────────────────────────────────────
    def _tool_ward_health_scores(
        self,
        zone: str | None = None,
        local_body_type: str | None = None,
    ) -> dict:
        issues = self._filtered(zone=zone, local_body_type=local_body_type)
        now = datetime.now(timezone.utc)

        ward_data: dict[str, dict] = defaultdict(lambda: {
            "ward_no": None, "zone": None, "open": 0, "resolved": 0,
            "reopened": 0, "chronic": 0, "total_urgency": 0.0,
            "sla_breached": 0, "corroborations": 0, "false_closure": 0,
        })

        for i in issues:
            key = i.ward_name or f"Ward {i.ward_no}" or "Unknown"
            d = ward_data[key]
            d["ward_no"] = i.ward_no
            d["zone"] = i.mcd_zone
            d["corroborations"] += i.corroboration_count
            if i.status in _OPEN_STATUSES:
                d["open"] += 1
                d["total_urgency"] += i.urgency_score
                hrs_open = (now - i.created_at).total_seconds() / 3600
                if hrs_open > _SLA_HOURS.get(i.severity, 168):
                    d["sla_breached"] += 1
            elif i.status in _CLOSED_STATUSES:
                d["resolved"] += 1
            if i.status == "reopened":
                d["reopened"] += 1
            if i.persistence_type == "chronic":
                d["chronic"] += 1
            if i.false_closure_suspected:
                d["false_closure"] += 1

        scored = []
        for ward, d in ward_data.items():
            total = d["open"] + d["resolved"]
            if total == 0:
                continue
            resolution_rate = d["resolved"] / total if total else 0
            sla_compliance = 1 - (d["sla_breached"] / d["open"]) if d["open"] else 1
            reopen_penalty = min(d["reopened"] / max(d["resolved"], 1), 0.5)
            chronic_penalty = min(d["chronic"] * 0.05, 0.3)
            score = max(0, min(100, (
                resolution_rate * 40 + sla_compliance * 40
                - reopen_penalty * 10 - chronic_penalty * 10
            ) * 100))
            fc_rate = round(d["false_closure"] / d["resolved"] * 100, 1) if d["resolved"] else 0
            scored.append({
                "ward_name": ward,
                "ward_no": d["ward_no"],
                "zone": d["zone"],
                "health_score": round(score, 1),
                "open": d["open"],
                "resolved": d["resolved"],
                "reopened": d["reopened"],
                "chronic": d["chronic"],
                "sla_breached": d["sla_breached"],
                "avg_urgency": round(d["total_urgency"] / d["open"], 2) if d["open"] else 0,
                "false_closure_count": d["false_closure"],
                "false_closure_rate_pct": fc_rate,
                "corroborations": d["corroborations"],
            })

        scored.sort(key=lambda x: x["health_score"])
        by_false_closure = sorted(scored, key=lambda x: x["false_closure_rate_pct"], reverse=True)

        return {
            "total_wards": len(scored),
            "wards": scored,
            "worst_5": scored[:5],
            "best_5": scored[-5:] if len(scored) >= 5 else scored,
            "worst_false_closure_wards": by_false_closure[:10],
            "avg_health_score": round(
                sum(w["health_score"] for w in scored) / len(scored), 1
            ) if scored else 0,
        }

    # ── Tool: zone comparison ─────────────────────────────────────────────────
    def _tool_zone_comparison(self) -> dict:
        """Rank all MCD zones across every governance metric."""
        all_issues = self._filtered()
        now = datetime.now(timezone.utc)

        zone_data: dict[str, dict] = defaultdict(lambda: {
            "total": 0, "open": 0, "resolved": 0, "reopened": 0,
            "sla_breached": 0, "false_closure": 0, "chronic": 0,
            "corroborations": 0, "total_urgency": 0.0, "safety_flags": 0,
            "unrouted": 0,
        })

        for i in all_issues:
            z = i.mcd_zone or "Unknown"
            d = zone_data[z]
            d["total"] += 1
            d["corroborations"] += i.corroboration_count
            if i.status in _OPEN_STATUSES:
                d["open"] += 1
                d["total_urgency"] += i.urgency_score
                hrs = (now - i.created_at).total_seconds() / 3600
                if hrs > _SLA_HOURS.get(i.severity, 168):
                    d["sla_breached"] += 1
                if i.public_safety_flag or i.health_hazard_flag:
                    d["safety_flags"] += 1
            elif i.status in _CLOSED_STATUSES:
                d["resolved"] += 1
            if i.status == "reopened":
                d["reopened"] += 1
            if i.persistence_type == "chronic":
                d["chronic"] += 1
            if i.false_closure_suspected:
                d["false_closure"] += 1
            if not i.primary_authority_slug:
                d["unrouted"] += 1

        zones = []
        for zone, d in zone_data.items():
            res_rate = round(d["resolved"] / d["total"] * 100, 1) if d["total"] else 0
            sla_rate = round(d["sla_breached"] / d["open"] * 100, 1) if d["open"] else 0
            fc_rate = round(d["false_closure"] / d["resolved"] * 100, 1) if d["resolved"] else 0
            avg_urg = round(d["total_urgency"] / d["open"], 2) if d["open"] else 0
            zones.append({
                "zone": zone,
                "total_issues": d["total"],
                "open": d["open"],
                "resolved": d["resolved"],
                "resolution_rate_pct": res_rate,
                "sla_breach_rate_pct": sla_rate,
                "false_closure_rate_pct": fc_rate,
                "chronic_issues": d["chronic"],
                "safety_flagged_open": d["safety_flags"],
                "avg_urgency": avg_urg,
                "total_corroborations": d["corroborations"],
                "unrouted_issues": d["unrouted"],
            })

        zones.sort(key=lambda x: x["resolution_rate_pct"], reverse=True)

        return {
            "total_zones": len(zones),
            "zones_ranked_by_resolution": zones,
            "worst_sla_zone": min(zones, key=lambda x: -x["sla_breach_rate_pct"])["zone"] if zones else "N/A",
            "best_resolution_zone": zones[0]["zone"] if zones else "N/A",
            "worst_resolution_zone": zones[-1]["zone"] if zones else "N/A",
            "most_urgent_zone": max(zones, key=lambda x: x["avg_urgency"])["zone"] if zones else "N/A",
        }

    # ── Tool: SLA analysis ────────────────────────────────────────────────────
    def _tool_sla_analysis(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
    ) -> dict:
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone, severity=severity,
            category=category, issue_type_slug=issue_type_slug,
            status_list=list(_OPEN_STATUSES),
        )
        now = datetime.now(timezone.utc)

        compliant, breached = [], []
        breach_by_sev: dict[str, int] = defaultdict(int)
        breach_by_auth: dict[str, int] = defaultdict(int)
        breach_details = []

        for i in issues:
            target_hrs = _SLA_HOURS.get(i.severity, 168)
            hrs_open = (now - i.created_at).total_seconds() / 3600
            breach_days = round((hrs_open - target_hrs) / 24, 1)
            if hrs_open > target_hrs:
                breached.append(i)
                breach_by_sev[i.severity] += 1
                auth_name = _AUTHORITY_NAMES.get(i.primary_authority_slug or "", i.primary_authority_slug or "UNROUTED")
                breach_by_auth[auth_name] += 1
                breach_details.append({
                    "id": i.id,
                    "title": i.title,
                    "authority": auth_name,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "severity": i.severity,
                    "days_open": round(hrs_open / 24, 1),
                    "sla_target_days": round(target_hrs / 24, 1),
                    "breach_by_days": breach_days,
                    "urgency_score": i.urgency_score,
                    "corroborations": i.corroboration_count,
                    "public_safety": i.public_safety_flag,
                })
            else:
                compliant.append(i)

        breach_details.sort(key=lambda x: x["breach_by_days"], reverse=True)

        return {
            "total_open": len(issues),
            "sla_compliant": len(compliant),
            "sla_breached": len(breached),
            "breach_rate_pct": round(len(breached) / len(issues) * 100, 1) if issues else 0,
            "breached_by_severity": dict(breach_by_sev),
            "breached_by_authority": dict(sorted(breach_by_auth.items(), key=lambda x: x[1], reverse=True)),
            "avg_breach_days": round(
                sum(d["breach_by_days"] for d in breach_details) / len(breach_details), 1
            ) if breach_details else 0,
            "worst_breaches": breach_details[:10],
            "sla_targets": {k: f"{v}h ({round(v/24,1)}d)" for k, v in _SLA_HOURS.items()},
        }

    # ── Tool: escalation analysis ─────────────────────────────────────────────
    def _tool_escalation_analysis(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        ward_name: str | None = None,
    ) -> dict:
        issues = self._filtered(authority_slug=authority_slug, zone=zone, ward_name=ward_name)
        now = datetime.now(timezone.utc)

        reopened = [i for i in issues if i.status == "reopened"]
        false_closure = [i for i in issues if i.false_closure_suspected]
        resolved = [i for i in issues if i.status in _CLOSED_STATUSES]

        auth_reopen: dict[str, int] = defaultdict(int)
        auth_false: dict[str, int] = defaultdict(int)
        zone_false: dict[str, int] = defaultdict(int)
        for i in reopened:
            auth_reopen[_AUTHORITY_NAMES.get(i.primary_authority_slug or "", i.primary_authority_slug or "unrouted")] += 1
        for i in false_closure:
            auth_false[_AUTHORITY_NAMES.get(i.primary_authority_slug or "", i.primary_authority_slug or "unrouted")] += 1
            zone_false[i.mcd_zone or "Unknown"] += 1

        return {
            "total_issues": len(issues),
            "total_resolved": len(resolved),
            "total_reopened": len(reopened),
            "reopen_rate_pct": round(len(reopened) / len(resolved) * 100, 1) if resolved else 0,
            "false_closure_count": len(false_closure),
            "false_closure_rate_pct": round(len(false_closure) / len(resolved) * 100, 1) if resolved else 0,
            "reopened_by_authority": dict(sorted(auth_reopen.items(), key=lambda x: x[1], reverse=True)),
            "false_closure_by_authority": dict(sorted(auth_false.items(), key=lambda x: x[1], reverse=True)),
            "false_closure_by_zone": dict(sorted(zone_false.items(), key=lambda x: x[1], reverse=True)),
            "reopened_issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", ""),
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "severity": i.severity,
                    "days_open": (now - i.created_at).days,
                    "corroborations": i.corroboration_count,
                    "urgency_score": i.urgency_score,
                    "false_closure_suspected": i.false_closure_suspected,
                }
                for i in sorted(reopened, key=lambda x: x.urgency_score, reverse=True)[:10]
            ],
        }

    # ── Tool: stalled issues ──────────────────────────────────────────────────
    def _tool_stalled_issues(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        min_days_stalled: int = 7,
    ) -> dict:
        """Issues in assigned/in_progress/pending_verification with no update for N days."""
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone,
            status_list=list(_STALL_STATUSES),
        )
        now = datetime.now(timezone.utc)

        stalled = []
        for i in issues:
            days_since_update = (now - i.updated_at).days
            if days_since_update >= min_days_stalled:
                stalled.append((i, days_since_update))

        stalled.sort(key=lambda x: x[1], reverse=True)

        by_authority: dict[str, int] = defaultdict(int)
        by_status: dict[str, int] = defaultdict(int)
        for i, _ in stalled:
            by_authority[_AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED")] += 1
            by_status[i.status] += 1

        return {
            "total_stalled": len(stalled),
            "threshold_days": min_days_stalled,
            "by_authority": dict(sorted(by_authority.items(), key=lambda x: x[1], reverse=True)),
            "by_status": dict(by_status),
            "worst_stalled": [
                {
                    "id": i.id,
                    "title": i.title,
                    "status": i.status,
                    "days_since_update": days,
                    "days_open": (now - i.created_at).days,
                    "severity": i.severity,
                    "urgency_score": i.urgency_score,
                    "corroborations": i.corroboration_count,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED"),
                }
                for i, days in stalled[:15]
            ],
        }

    # ── Tool: chronic hotspots ────────────────────────────────────────────────
    def _tool_chronic_hotspots(
        self,
        zone: str | None = None,
        authority_slug: str | None = None,
        category: str | None = None,
        limit: int = 15,
    ) -> dict:
        """Wards/localities where the same class of problems keeps recurring."""
        issues = self._filtered(
            zone=zone, authority_slug=authority_slug, category=category,
        )

        # Ward-level chronic accumulation
        ward_chronic: dict[str, dict] = defaultdict(lambda: {
            "chronic": 0, "recurring": 0, "new": 0,
            "categories": defaultdict(int), "zone": None,
            "corroborations": 0, "open": 0,
        })
        locality_chronic: dict[str, dict] = defaultdict(lambda: {
            "chronic": 0, "recurring": 0, "types": defaultdict(int),
            "ward": None, "zone": None,
        })

        for i in issues:
            ward_key = i.ward_name or f"Ward {i.ward_no}" or "Unknown"
            d = ward_chronic[ward_key]
            d["zone"] = i.mcd_zone
            d[i.persistence_type] = d.get(i.persistence_type, 0) + 1
            d["categories"][i.issue_category_slug or "unknown"] += 1
            d["corroborations"] += i.corroboration_count
            if i.status in _OPEN_STATUSES:
                d["open"] += 1

            if i.locality_name:
                loc = locality_chronic[i.locality_name]
                loc["ward"] = i.ward_name
                loc["zone"] = i.mcd_zone
                loc[i.persistence_type] = loc.get(i.persistence_type, 0) + 1
                loc["types"][i.issue_type_slug or "unknown"] += 1

        ward_rows = [
            {
                "ward_name": ward,
                "zone": d["zone"],
                "chronic_count": d["chronic"],
                "recurring_count": d["recurring"],
                "persistence_score": d["chronic"] * 3 + d["recurring"],
                "open_issues": d["open"],
                "corroborations": d["corroborations"],
                "dominant_categories": sorted(
                    d["categories"].items(), key=lambda x: x[1], reverse=True
                )[:3],
            }
            for ward, d in ward_chronic.items()
            if d["chronic"] + d["recurring"] > 0
        ]
        ward_rows.sort(key=lambda x: x["persistence_score"], reverse=True)

        locality_rows = [
            {
                "locality": loc,
                "ward": d["ward"],
                "zone": d["zone"],
                "chronic_count": d["chronic"],
                "recurring_count": d["recurring"],
                "dominant_types": sorted(
                    d["types"].items(), key=lambda x: x[1], reverse=True
                )[:3],
            }
            for loc, d in locality_chronic.items()
            if d["chronic"] + d["recurring"] > 0
        ]
        locality_rows.sort(key=lambda x: x["chronic_count"], reverse=True)

        return {
            "total_chronic_issues": sum(1 for i in issues if i.persistence_type == "chronic"),
            "total_recurring_issues": sum(1 for i in issues if i.persistence_type in ("recurring", "chronic")),
            "worst_wards": ward_rows[:limit],
            "worst_localities": locality_rows[:limit],
        }

    # ── Tool: rejection analysis ──────────────────────────────────────────────
    def _tool_rejection_analysis(
        self,
        authority_slug: str | None = None,
        zone: str | None = None,
        min_corroborations: int | None = None,
    ) -> dict:
        """Analyse rejected issues — especially high-corroboration rejections (accountability red flags)."""
        all_issues = self._filtered(authority_slug=authority_slug, zone=zone)
        rejected = [i for i in all_issues if i.status == "rejected"]

        if min_corroborations is not None:
            rejected = [i for i in rejected if i.corroboration_count >= min_corroborations]

        by_authority: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)
        for i in rejected:
            by_authority[_AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED")] += 1
            by_category[i.issue_category_slug or "unknown"] += 1

        total = len(all_issues)
        total_resolved = sum(1 for i in all_issues if i.status in _CLOSED_STATUSES)

        # High-corroboration rejections are the most concerning
        suspicious = sorted(rejected, key=lambda x: x.corroboration_count, reverse=True)

        return {
            "total_issues_in_scope": total,
            "total_rejected": len(rejected),
            "rejection_rate_pct": round(len(rejected) / total * 100, 1) if total else 0,
            "high_corroboration_rejections": [
                i for i in suspicious if i.corroboration_count >= 3
            ].__len__(),
            "by_authority": dict(sorted(by_authority.items(), key=lambda x: x[1], reverse=True)),
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "most_suspicious_rejections": [
                {
                    "id": i.id,
                    "title": i.title,
                    "corroborations": i.corroboration_count,
                    "severity": i.severity,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED"),
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "status_reason": i.status_reason,
                    "category": i.issue_category_slug,
                }
                for i in suspicious[:15]
            ],
        }

    # ── Tool: safety hazard report ────────────────────────────────────────────
    def _tool_safety_hazard_report(
        self,
        zone: str | None = None,
        authority_slug: str | None = None,
    ) -> dict:
        """All open issues with public safety or health hazard flags — triage board."""
        all_open = self._filtered(
            zone=zone, authority_slug=authority_slug,
            status_list=list(_OPEN_STATUSES),
        )
        now = datetime.now(timezone.utc)

        safety = [i for i in all_open if i.public_safety_flag]
        health = [i for i in all_open if i.health_hazard_flag]
        obstruction = [i for i in all_open if i.obstruction_flag]
        any_flag = [i for i in all_open if i.public_safety_flag or i.health_hazard_flag or i.obstruction_flag]

        by_type: dict[str, int] = defaultdict(int)
        by_authority: dict[str, int] = defaultdict(int)
        for i in any_flag:
            by_type[i.issue_type_slug or i.issue_category_slug or "unknown"] += 1
            by_authority[_AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED")] += 1

        critical_safety = sorted(any_flag, key=lambda x: x.urgency_score, reverse=True)

        return {
            "total_safety_flagged_open": len(any_flag),
            "public_safety_count": len(safety),
            "health_hazard_count": len(health),
            "obstruction_count": len(obstruction),
            "by_issue_type": dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
            "by_authority": dict(sorted(by_authority.items(), key=lambda x: x[1], reverse=True)),
            "critical_safety_issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "urgency_score": i.urgency_score,
                    "days_open": (now - i.created_at).days,
                    "corroborations": i.corroboration_count,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "locality": i.locality_name,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED"),
                    "type": i.issue_type_slug,
                    "flags": {
                        "public_safety": i.public_safety_flag,
                        "health_hazard": i.health_hazard_flag,
                        "obstruction": i.obstruction_flag,
                    },
                    "sla_breached": (now - i.created_at).total_seconds() / 3600 > _SLA_HOURS.get(i.severity, 168),
                }
                for i in critical_safety[:20]
            ],
        }

    # ── Tool: unrouted issues (routing gap) ───────────────────────────────────
    def _tool_unrouted_issues(
        self,
        zone: str | None = None,
        category: str | None = None,
    ) -> dict:
        """Issues with no primary authority assigned — falling through the cracks."""
        issues = self._filtered(zone=zone, category=category)
        now = datetime.now(timezone.utc)

        unrouted = [i for i in issues if not i.primary_authority_slug]

        by_category: dict[str, int] = defaultdict(int)
        by_zone: dict[str, int] = defaultdict(int)
        by_type: dict[str, int] = defaultdict(int)
        for i in unrouted:
            by_category[i.issue_category_slug or "unknown"] += 1
            by_zone[i.mcd_zone or "Unknown"] += 1
            by_type[i.issue_type_slug or "unknown"] += 1

        urgent_unrouted = sorted(unrouted, key=lambda x: x.urgency_score, reverse=True)

        return {
            "total_unrouted": len(unrouted),
            "unrouted_rate_pct": round(len(unrouted) / len(issues) * 100, 1) if issues else 0,
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "by_zone": dict(sorted(by_zone.items(), key=lambda x: x[1], reverse=True)),
            "by_type": dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
            "safety_flagged_unrouted": sum(1 for i in unrouted if i.public_safety_flag or i.health_hazard_flag),
            "top_unrouted": [
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "urgency_score": i.urgency_score,
                    "corroborations": i.corroboration_count,
                    "days_open": (now - i.created_at).days,
                    "ward": i.ward_name,
                    "zone": i.mcd_zone,
                    "category": i.issue_category_slug,
                    "type": i.issue_type_slug,
                    "public_safety": i.public_safety_flag,
                }
                for i in urgent_unrouted[:15]
            ],
        }

    # ── Tool: citizen engagement stats ───────────────────────────────────────
    def _tool_citizen_engagement(
        self,
        zone: str | None = None,
        authority_slug: str | None = None,
        category: str | None = None,
        days_ago: int | None = None,
    ) -> dict:
        """Corroboration patterns, citizen trust, and participation metrics."""
        issues = self._filtered(
            zone=zone, authority_slug=authority_slug,
            category=category, days_ago=days_ago,
        )
        now = datetime.now(timezone.utc)

        total_corroborations = sum(i.corroboration_count for i in issues)
        total_reports = sum(i.total_report_count for i in issues)

        # Issues with highest citizen backing
        highly_corroborated = sorted(issues, key=lambda x: x.corroboration_count, reverse=True)
        high_corr_unresolved = [i for i in highly_corroborated if i.status in _OPEN_STATUSES]

        # Corroboration buckets
        buckets = {"100+": 0, "50-99": 0, "20-49": 0, "10-19": 0, "5-9": 0, "1-4": 0, "0": 0}
        for i in issues:
            c = i.corroboration_count
            if c >= 100:
                buckets["100+"] += 1
            elif c >= 50:
                buckets["50-99"] += 1
            elif c >= 20:
                buckets["20-49"] += 1
            elif c >= 10:
                buckets["10-19"] += 1
            elif c >= 5:
                buckets["5-9"] += 1
            elif c >= 1:
                buckets["1-4"] += 1
            else:
                buckets["0"] += 1

        # Trust signals: how often do citizens dispute resolutions?
        resolved = [i for i in issues if i.status in _CLOSED_STATUSES]
        false_closures = sum(1 for i in resolved if i.false_closure_suspected)
        trust_rate = round((1 - false_closures / len(resolved)) * 100, 1) if resolved else 100.0

        return {
            "total_issues": len(issues),
            "total_corroborations": total_corroborations,
            "total_citizen_reports": total_reports,
            "avg_corroborations_per_issue": round(total_corroborations / len(issues), 2) if issues else 0,
            "corroboration_distribution": buckets,
            "citizen_trust_rate_pct": trust_rate,
            "false_closures_disputed": false_closures,
            "most_corroborated_open": [
                {
                    "id": i.id,
                    "title": i.title,
                    "corroborations": i.corroboration_count,
                    "total_reports": i.total_report_count,
                    "days_open": (now - i.created_at).days,
                    "status": i.status,
                    "severity": i.severity,
                    "ward": i.ward_name,
                    "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED"),
                    "urgency_score": i.urgency_score,
                }
                for i in high_corr_unresolved[:10]
            ],
            "most_corroborated_overall": [
                {
                    "id": i.id,
                    "title": i.title,
                    "corroborations": i.corroboration_count,
                    "status": i.status,
                    "ward": i.ward_name,
                }
                for i in highly_corroborated[:5]
            ],
        }

    # ── Tool: trend analysis ──────────────────────────────────────────────────
    def _tool_trend_analysis(
        self,
        group_by: str = "week",
        authority_slug: str | None = None,
        zone: str | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
        days: int = 90,
    ) -> dict:
        """Time-bucketed filing and resolution trends. group_by: day|week|month"""
        issues = self._filtered(
            authority_slug=authority_slug, zone=zone,
            category=category, issue_type_slug=issue_type_slug,
            days_ago=days,
        )
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)

        def bucket_key(dt: datetime) -> str:
            if group_by == "day":
                return dt.strftime("%Y-%m-%d")
            elif group_by == "month":
                return dt.strftime("%Y-%m")
            else:  # week
                iso = dt.isocalendar()
                return f"{iso[0]}-W{iso[1]:02d}"

        filed: dict[str, int] = defaultdict(int)
        resolved_trend: dict[str, int] = defaultdict(int)
        sla_breached_trend: dict[str, int] = defaultdict(int)
        critical_trend: dict[str, int] = defaultdict(int)

        for i in issues:
            if i.created_at >= cutoff:
                k = bucket_key(i.created_at)
                filed[k] += 1
                if i.severity == "critical":
                    critical_trend[k] += 1

            if i.status in _CLOSED_STATUSES and i.updated_at >= cutoff:
                resolved_trend[bucket_key(i.updated_at)] += 1

            if i.status in _OPEN_STATUSES:
                hrs = (now - i.created_at).total_seconds() / 3600
                if hrs > _SLA_HOURS.get(i.severity, 168):
                    sla_breached_trend[bucket_key(i.created_at)] += 1

        all_keys = sorted(set(list(filed.keys()) + list(resolved_trend.keys())))

        trend_rows = [
            {
                "period": k,
                "filed": filed.get(k, 0),
                "resolved": resolved_trend.get(k, 0),
                "sla_breached_filed": sla_breached_trend.get(k, 0),
                "critical_filed": critical_trend.get(k, 0),
                "net_backlog_change": filed.get(k, 0) - resolved_trend.get(k, 0),
            }
            for k in all_keys
        ]

        recent = trend_rows[-4:] if len(trend_rows) >= 4 else trend_rows
        early = trend_rows[:4] if len(trend_rows) >= 4 else trend_rows

        avg_recent_filed = round(sum(r["filed"] for r in recent) / len(recent), 1) if recent else 0
        avg_early_filed = round(sum(r["filed"] for r in early) / len(early), 1) if early else 0

        return {
            "period": f"last {days} days",
            "group_by": group_by,
            "total_filed_in_period": len(issues),
            "trend": trend_rows,
            "avg_recent_period_filings": avg_recent_filed,
            "avg_early_period_filings": avg_early_filed,
            "trajectory": "increasing" if avg_recent_filed > avg_early_filed * 1.1
            else "decreasing" if avg_recent_filed < avg_early_filed * 0.9
            else "stable",
        }

    # ── Tool: commissioner accountability ─────────────────────────────────────
    def _tool_commissioner_accountability(
        self,
        commissioner_name: str | None = None,
    ) -> dict:
        """Aggregate civic issue performance broken down by MCD zonal commissioner."""
        all_issues = self._filtered()
        now = datetime.now(timezone.utc)

        # Group by commissioner
        comm_data: dict[str, dict] = {}
        for zone, info in _ZONE_COMMISSIONER.items():
            cname = info["name"]
            if cname not in comm_data:
                comm_data[cname] = {
                    "commissioner": cname,
                    "email": info["email"],
                    "zones": info["zones"],
                    "total": 0,
                    "open": 0,
                    "resolved": 0,
                    "reopened": 0,
                    "sla_breached": 0,
                    "false_closure": 0,
                    "chronic": 0,
                    "corroborations": 0,
                    "safety_flagged": 0,
                    "total_urgency": 0.0,
                    "worst_issues": [],
                }

        for i in all_issues:
            zone = i.mcd_zone or ""
            info = _ZONE_COMMISSIONER.get(zone)
            if not info:
                continue
            d = comm_data[info["name"]]
            d["total"] += 1
            d["corroborations"] += i.corroboration_count
            if i.status in _OPEN_STATUSES:
                d["open"] += 1
                d["total_urgency"] += i.urgency_score
                hrs = (now - i.created_at).total_seconds() / 3600
                if hrs > _SLA_HOURS.get(i.severity, 168):
                    d["sla_breached"] += 1
                if i.public_safety_flag or i.health_hazard_flag:
                    d["safety_flagged"] += 1
            elif i.status in _CLOSED_STATUSES:
                d["resolved"] += 1
            if i.status == "reopened":
                d["reopened"] += 1
            if i.persistence_type == "chronic":
                d["chronic"] += 1
            if i.false_closure_suspected:
                d["false_closure"] += 1

        rows = []
        for cname, d in comm_data.items():
            if commissioner_name and commissioner_name.lower() not in cname.lower():
                continue
            open_count = d["open"]
            resolved = d["resolved"]
            total = d["total"]
            worst = sorted(
                [i for i in all_issues if _ZONE_COMMISSIONER.get(i.mcd_zone or "", {}).get("name") == cname and i.status in _OPEN_STATUSES],
                key=lambda x: x.urgency_score,
                reverse=True,
            )[:5]
            rows.append({
                "commissioner": d["commissioner"],
                "email": d["email"],
                "zones_under_jurisdiction": d["zones"],
                "total_issues": total,
                "open_issues": open_count,
                "resolved_issues": resolved,
                "resolution_rate_pct": round(resolved / total * 100, 1) if total else 0,
                "sla_breach_count": d["sla_breached"],
                "sla_breach_rate_pct": round(d["sla_breached"] / open_count * 100, 1) if open_count else 0,
                "false_closure_count": d["false_closure"],
                "false_closure_rate_pct": round(d["false_closure"] / resolved * 100, 1) if resolved else 0,
                "chronic_issues": d["chronic"],
                "safety_flagged_open": d["safety_flagged"],
                "total_corroborations": d["corroborations"],
                "avg_urgency": round(d["total_urgency"] / open_count, 2) if open_count else 0,
                "worst_open_issues": [
                    {
                        "id": i.id, "title": i.title, "severity": i.severity,
                        "urgency_score": i.urgency_score,
                        "days_open": (now - i.created_at).days,
                        "ward": i.ward_name, "zone": i.mcd_zone,
                        "corroborations": i.corroboration_count,
                        "authority": _AUTHORITY_NAMES.get(i.primary_authority_slug or "", "UNROUTED"),
                    }
                    for i in worst
                ],
            })

        rows.sort(key=lambda x: x["sla_breach_rate_pct"], reverse=True)
        return {
            "commissioners_total": len(rows),
            "note": "Covers MCD Additional Commissioners only. NDMC/DCB/other bodies not included.",
            "accountability_table": rows,
            "worst_sla_commissioner": rows[0]["commissioner"] if rows else "N/A",
            "best_resolution_commissioner": max(rows, key=lambda x: x["resolution_rate_pct"])["commissioner"] if rows else "N/A",
        }

    # ── Shared filter helper ──────────────────────────────────────────────────
    def _filtered(
        self,
        *,
        authority_slug: str | None = None,
        zone: str | None = None,
        ward_name: str | None = None,
        status: str | None = None,
        status_list: list[str] | None = None,
        category: str | None = None,
        issue_type_slug: str | None = None,
        severity: str | None = None,
        days_ago: int | None = None,
        local_body_type: str | None = None,
    ) -> list[IssueRecord]:
        issues = self.repo.list_issues(
            statuses=status_list or ([status] if status else None),
            primary_authority_slug=authority_slug,
        )
        now = datetime.now(timezone.utc)
        result = []
        for i in issues:
            if zone and (i.mcd_zone or "").lower() != zone.lower():
                continue
            if ward_name and (i.ward_name or "").lower() != ward_name.lower():
                continue
            if category and i.issue_category_slug != category:
                continue
            if issue_type_slug and (i.issue_type_slug or "").lower() != issue_type_slug.lower():
                continue
            if severity and i.severity != severity:
                continue
            if local_body_type and (i.local_body_type or "").upper() != local_body_type.upper():
                continue
            if days_ago and (now - i.created_at).days > days_ago:
                continue
            result.append(i)
        return result

    # ═══════════════════════════════════════════════
    # GEMINI FUNCTION DECLARATIONS
    # ═══════════════════════════════════════════════
    def _declarations(self) -> list:
        from google.genai import types as gt

        def obj(props: dict, required: list[str] | None = None):
            p = {k: gt.Schema(**v) for k, v in props.items()}
            return gt.Schema(type=gt.Type.OBJECT, properties=p, required=required or [])

        def str_prop(desc: str):
            return {"type": gt.Type.STRING, "description": desc}

        def int_prop(desc: str):
            return {"type": gt.Type.INTEGER, "description": desc}

        def num_prop(desc: str):
            return {"type": gt.Type.NUMBER, "description": desc}

        def bool_prop(desc: str):
            return {"type": gt.Type.BOOLEAN, "description": desc}

        def arr_str_prop(desc: str):
            return {"type": gt.Type.ARRAY, "description": desc, "items": gt.Schema(type=gt.Type.STRING)}

        AUTHORITY_DESC = (
            "Authority slug. One of: mcd_sanitation, mcd_engineering, mcd_horticulture, "
            "mcd_public_health, ndmc_civil, ndmc_sanitation, ndmc_horticulture, "
            "dcb_civic, djb, pwd, ifcd, dda, delhi_police, nhai."
        )
        ZONE_DESC = "MCD zone name: South, Rohini, Civil Lines, Shahdara, East, West, North, Central, Najafgarh, Narela, South West, City SP."
        CATEGORY_DESC = "Category slug: roads_streets, water_sewer_drainage, garbage_sanitation, lights_electrical, parks_public_space, public_safety_hazard, animals_other."
        TYPE_DESC = "Issue type: waterlogging, pothole, road_damage, sewer_overflow, drain_overflow, drain_blockage, pipe_burst, water_supply_issue, garbage_dump, overflowing_bin, streetlight_outage, open_manhole, fallen_wire, tree_fall, park_damage, encroachment_road, footpath_damage, dead_animal."

        return [
            # 1. aggregate stats
            gt.FunctionDeclaration(
                name="get_issue_stats",
                description=(
                    "Aggregate statistics with flexible filters. Returns totals, status/severity breakdown, "
                    "chronic/safety/false-closure counts, and top_urgent_issues list "
                    "(top 10 most urgent open issues with full details including id, title, ward, zone, "
                    "authority, severity, days_open, urgency_score, corroborations, type). "
                    "Use as the entry point for any overview question."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "ward_name": str_prop("Ward name filter."),
                    "status": str_prop("submitted | in_progress | resolved | reopened | rejected."),
                    "category": str_prop(CATEGORY_DESC),
                    "issue_type_slug": str_prop(TYPE_DESC),
                    "severity": str_prop("low | medium | high | critical"),
                    "days_ago": int_prop("Only issues filed in last N days."),
                }),
            ),

            # 2. individual issue detail
            gt.FunctionDeclaration(
                name="get_issue_detail",
                description=(
                    "Full expanded detail for ONE specific issue — like the citizen expanded issue view. "
                    "Returns: title, description, AI summary, status, severity, urgency, corroboration count, "
                    "total reports merged, days open, full location (ward, zone, locality, landmark, lat/lng), "
                    "classification (category/type/persistence), all safety flags, authority assignment "
                    "with routing confidence, SLA status (target, breach, breach_by_hours), "
                    "and complete event timeline (status changes, assignments, actor). "
                    "Call this when the user references a specific issue ID or wants to 'expand' or 'show details' of one issue."
                ),
                parameters=obj(
                    {"issue_id": str_prop("The issue ID (UUID string) to look up.")},
                    required=["issue_id"],
                ),
            ),

            # 3. advanced issue search
            gt.FunctionDeclaration(
                name="search_issues",
                description=(
                    "Advanced filtered and sorted issue list. Supports every combination of filters. "
                    "Returns up to `limit` issues with full detail (id, title, status, severity, urgency, "
                    "corroborations, days_open, ward, zone, authority, type, persistence, flags). "
                    "USE THIS for: 'issues corroborated by 100+ people', 'unresolved safety hazards', "
                    "'all chronic issues in South Zone', 'issues with no authority', "
                    "'high urgency issues in ward X', 'all false closure suspected issues'. "
                    "sort_by options: urgency | corroborations | days_open | severity | created_at"
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "ward_name": str_prop("Filter to specific ward."),
                    "category": str_prop(CATEGORY_DESC),
                    "issue_type_slug": str_prop(TYPE_DESC),
                    "severity": str_prop("low | medium | high | critical"),
                    "status": str_prop("submitted | in_progress | resolved | reopened | rejected | open (for all open statuses)."),
                    "days_ago": int_prop("Filed in last N days."),
                    "min_corroborations": int_prop("Only issues with at least this many corroborations."),
                    "max_corroborations": int_prop("Only issues with at most this many corroborations."),
                    "min_urgency_score": num_prop("Only issues with urgency >= this value (1.0–10.0)."),
                    "min_days_open": int_prop("Only issues open for at least N days."),
                    "max_days_open": int_prop("Only issues open for at most N days."),
                    "public_safety_only": bool_prop("If true, only return public safety flagged issues."),
                    "health_hazard_only": bool_prop("If true, only return health hazard flagged issues."),
                    "obstruction_only": bool_prop("If true, only return obstruction flagged issues."),
                    "false_closure_only": bool_prop("If true, only false-closure-suspected issues."),
                    "chronic_only": bool_prop("If true, only chronic (same-location recurring) issues."),
                    "recurring_only": bool_prop("If true, recurring OR chronic issues."),
                    "unrouted_only": bool_prop("If true, only issues with no authority assigned."),
                    "sort_by": str_prop("urgency | corroborations | days_open | severity | created_at"),
                    "limit": int_prop("Max results to return (default 20, max 50)."),
                }),
            ),

            # 4. authority scorecard
            gt.FunctionDeclaration(
                name="get_authority_scorecard",
                description=(
                    "Deep performance audit of ONE authority. Returns: resolution rate, SLA breach rate, "
                    "avg resolution days, false closure rate, rejection rate, stalled issues (7d no update), "
                    "chronic/recurring count, safety-flagged open, top categories, open by zone, "
                    "worst 5 open issues. Use for single-authority audit questions."
                ),
                parameters=obj(
                    {"authority_slug": str_prop(AUTHORITY_DESC)},
                    required=["authority_slug"],
                ),
            ),

            # 5. authority comparison
            gt.FunctionDeclaration(
                name="get_authority_comparison",
                description=(
                    "Side-by-side comparison of multiple (or all 14) authorities on every metric: "
                    "total, open, resolved, resolution_rate_pct, sla_breach_rate_pct, "
                    "false_closure_rate_pct, stalled_7d, chronic, avg_urgency, total_corroborations. "
                    "Returns sorted table plus best/worst labels. "
                    "USE THIS for: 'compare A vs B', 'which authority is worst overall', "
                    "'rank all authorities by SLA', 'worst performing department'."
                ),
                parameters=obj({
                    "authority_slugs": {
                        "type": gt.Type.ARRAY,
                        "description": "List of authority slugs to compare. Leave empty to compare all 14.",
                        "items": gt.Schema(type=gt.Type.STRING),
                    },
                }),
            ),

            # 6. category breakdown
            gt.FunctionDeclaration(
                name="get_category_breakdown",
                description=(
                    "Break down issues by category and type. Returns counts by category with "
                    "open/critical/corroboration/chronic sub-counts, top 10 issue types, and safety flags. "
                    "Use to find what kinds of problems dominate a scope."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "ward_name": str_prop("Filter to specific ward."),
                    "category": str_prop(CATEGORY_DESC),
                    "issue_type_slug": str_prop(TYPE_DESC),
                }),
            ),

            # 7. ward health scores
            gt.FunctionDeclaration(
                name="get_ward_health_scores",
                description=(
                    "Civic health score (0–100) for every ward. Score = resolution rate (40%) + "
                    "SLA compliance (40%) - reopen penalty (10%) - chronic penalty (10%). "
                    "Returns all wards ranked worst→best, worst_5, best_5, "
                    "AND worst_false_closure_wards (top wards by false closure rate). "
                    "Each ward includes: false_closure_rate_pct, open, resolved, reopened, chronic, "
                    "sla_breached, avg_urgency, corroborations. "
                    "Use for ward-level governance reports and 'highest false closure rate by ward' queries."
                ),
                parameters=obj({
                    "zone": str_prop("Filter to specific MCD zone. Leave empty for all Delhi."),
                    "local_body_type": str_prop("MCD | NDMC | DCB"),
                }),
            ),

            # 8. zone comparison
            gt.FunctionDeclaration(
                name="get_zone_comparison",
                description=(
                    "Rank ALL zones across every governance metric: resolution rate, SLA breach rate, "
                    "false closure rate, chronic issues, safety flagged, avg urgency, corroborations, "
                    "unrouted issues. Returns zones_ranked_by_resolution plus best/worst labels. "
                    "Use for state-wide geographic governance overview."
                ),
                parameters=obj({}),
            ),

            # 9. SLA analysis
            gt.FunctionDeclaration(
                name="get_sla_analysis",
                description=(
                    "SLA compliance analysis for open issues. Targets: critical=24h, high=72h, medium=7d, low=14d. "
                    "Returns breach count, breach rate %, breaches by severity AND by authority, "
                    "avg breach days, worst 10 breached issues. "
                    "Use for delay analysis, SLA violations, response time questions."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "severity": str_prop("low | medium | high | critical"),
                    "category": str_prop(CATEGORY_DESC),
                    "issue_type_slug": str_prop(TYPE_DESC),
                }),
            ),

            # 10. escalation analysis
            gt.FunctionDeclaration(
                name="get_escalation_analysis",
                description=(
                    "False closure and escalation patterns. Returns: reopen_rate_pct, false_closure_rate_pct, "
                    "reopened_by_authority, false_closure_by_authority, false_closure_by_zone, "
                    "top 10 escalated issues. "
                    "Use for accountability audits and identifying which authorities/zones have worst resolution quality."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "ward_name": str_prop("Filter to specific ward."),
                }),
            ),

            # 11. stalled issues
            gt.FunctionDeclaration(
                name="get_stalled_issues",
                description=(
                    "Issues stuck in assigned/in_progress/pending_verification with no status update for N days. "
                    "Returns: total stalled, breakdown by authority and status, worst_stalled list "
                    "(with days_since_update, days_open, authority, urgency, corroborations). "
                    "USE THIS for: 'issues with no movement', 'stuck issues', 'assigned but ignored', "
                    "'bureaucratic bottleneck', 'no action taken'. Default threshold: 7 days."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "min_days_stalled": int_prop("Minimum days with no status update (default 7)."),
                }),
            ),

            # 12. chronic hotspots
            gt.FunctionDeclaration(
                name="get_chronic_hotspots",
                description=(
                    "Locations where the same civic problems keep recurring. "
                    "Returns worst wards (by persistence_score = chronic*3 + recurring) with dominant categories, "
                    "and worst localities with dominant issue types. "
                    "USE THIS for: 'problem locations', 'recurring issues', 'chronic hotspots', "
                    "'same place keeps getting reported', 'systemic infrastructure failure'."
                ),
                parameters=obj({
                    "zone": str_prop(ZONE_DESC),
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "category": str_prop(CATEGORY_DESC),
                    "limit": int_prop("Number of worst locations to return (default 15)."),
                }),
            ),

            # 13. rejection analysis
            gt.FunctionDeclaration(
                name="get_rejection_analysis",
                description=(
                    "Analyse rejected issues — especially suspicious high-corroboration rejections. "
                    "Returns: rejection rate %, by authority, by category, "
                    "most_suspicious_rejections (sorted by corroboration count). "
                    "High-corroboration rejections = citizens widely confirmed an issue that was rejected — "
                    "major accountability red flag. "
                    "USE THIS for: 'rejected complaints', 'dismissed issues', 'accountability gap', "
                    "'which authority rejects the most', 'citizens ignored by authorities'."
                ),
                parameters=obj({
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "min_corroborations": int_prop("Only rejected issues with at least this many corroborations."),
                }),
            ),

            # 14. safety hazard report
            gt.FunctionDeclaration(
                name="get_safety_hazard_report",
                description=(
                    "Triage board for ALL open issues with public_safety, health_hazard, or obstruction flags. "
                    "Returns: counts by flag type, by issue type, by authority, and critical_safety_issues list "
                    "(sorted by urgency, with SLA breach status). "
                    "USE THIS for: 'safety emergencies', 'health hazards', 'open manholes', 'fallen wires', "
                    "'what needs immediate action', 'life-threatening issues'."
                ),
                parameters=obj({
                    "zone": str_prop(ZONE_DESC),
                    "authority_slug": str_prop(AUTHORITY_DESC),
                }),
            ),

            # 15. unrouted issues
            gt.FunctionDeclaration(
                name="get_unrouted_issues",
                description=(
                    "Issues with no primary authority assigned — falling through governance gaps. "
                    "Returns: total unrouted, rate %, breakdown by category/zone/type, "
                    "safety_flagged_unrouted count, top unrouted issues by urgency. "
                    "USE THIS for: 'routing gaps', 'no authority responsible', 'orphan issues', "
                    "'who is responsible', 'issues that no department owns'."
                ),
                parameters=obj({
                    "zone": str_prop(ZONE_DESC),
                    "category": str_prop(CATEGORY_DESC),
                }),
            ),

            # 16. citizen engagement
            gt.FunctionDeclaration(
                name="get_citizen_engagement",
                description=(
                    "Citizen participation and trust metrics. Returns: total corroborations, "
                    "avg corroborations per issue, corroboration distribution (0/1-4/5-9/10-19/20-49/50-99/100+), "
                    "citizen_trust_rate_pct (how often resolutions are accepted without dispute), "
                    "most_corroborated_open (issues with most citizen backing that are still unresolved — "
                    "major accountability signal), most_corroborated_overall. "
                    "USE THIS for: 'citizen engagement', 'public support', 'most corroborated issues', "
                    "'100+ corroborations unresolved', 'citizen trust', 'participatory governance'."
                ),
                parameters=obj({
                    "zone": str_prop(ZONE_DESC),
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "category": str_prop(CATEGORY_DESC),
                    "days_ago": int_prop("Limit to issues filed in last N days."),
                }),
            ),

            # 17. trend analysis
            gt.FunctionDeclaration(
                name="get_trend_analysis",
                description=(
                    "Time-bucketed filing and resolution trend data. Returns trend rows with "
                    "period, filed, resolved, sla_breached_filed, critical_filed, net_backlog_change. "
                    "Also returns trajectory: increasing | decreasing | stable. "
                    "USE THIS for: 'getting better or worse', 'trend over time', 'seasonal patterns', "
                    "'monthly comparison', 'backlog growing', 'improvement over last quarter'."
                ),
                parameters=obj({
                    "group_by": str_prop("Time bucket: day | week | month (default week)."),
                    "authority_slug": str_prop(AUTHORITY_DESC),
                    "zone": str_prop(ZONE_DESC),
                    "category": str_prop(CATEGORY_DESC),
                    "issue_type_slug": str_prop(TYPE_DESC),
                    "days": int_prop("Number of past days to analyse (default 90)."),
                }),
            ),

            # 18. commissioner accountability
            gt.FunctionDeclaration(
                name="get_commissioner_accountability",
                description=(
                    "Accountability report broken down by MCD zonal commissioner. "
                    "Each of Delhi's 5 Additional Commissioners oversees 2–3 MCD zones. "
                    "Returns accountability_table with per-commissioner: resolution rate, SLA breach rate, "
                    "false closure rate, chronic issues, safety-flagged open, corroborations, "
                    "avg urgency, and their 5 worst open issues. Also returns worst_sla_commissioner "
                    "and best_resolution_commissioner. "
                    "USE THIS for: 'who is the commissioner responsible', 'hold commissioner accountable', "
                    "'commissioner performance', 'which commissioner has worst record', "
                    "'MCD Additional Commissioner audit', 'political accountability', "
                    "'escalate to commissioner', 'governance accountability by official'."
                ),
                parameters=obj({
                    "commissioner_name": str_prop(
                        "Filter to a specific commissioner by name (partial match). "
                        "Leave empty to return all 5 MCD commissioners. "
                        "Names: Sachin Shinde, Jitender Yadav, Nidhi Malik, Dr. Tariq Thomas, Pankaj Naresh Agrawal."
                    ),
                }),
            ),
        ]
