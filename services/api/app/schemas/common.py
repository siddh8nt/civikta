"""Shared enums + value objects. Keep these stable — they are the vocabulary the
whole system (and the future agent's tools) speaks."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IssueStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    pending_verification = "pending_verification"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"
    reopened = "reopened"
    manual_review = "manual_review"


class ReportRole(str, Enum):
    original = "original"
    corroboration = "corroboration"


class MergeDecision(str, Enum):
    pending = "pending"
    merged = "merged"
    forced_new = "forced_new"
    manual_review = "manual_review"


class EventType(str, Enum):
    created = "created"
    classified = "classified"
    assigned = "assigned"
    verified = "verified"
    resolved = "resolved"
    reopened = "reopened"
    duplicate_candidate_found = "duplicate_candidate_found"
    community_verification_prompt_shown = "community_verification_prompt_shown"
    issue_corroborated = "issue_corroborated"
    issue_merged = "issue_merged"
    urgency_score_updated = "urgency_score_updated"
    still_unresolved_confirmed = "still_unresolved_confirmed"
    # authority / field actions
    authority_acknowledged = "authority_acknowledged"
    authority_rejected = "authority_rejected"
    field_visit_scheduled = "field_visit_scheduled"
    field_visit_completed = "field_visit_completed"
    repair_scheduled = "repair_scheduled"
    routed = "routed"
    rerouted = "rerouted"
    manual_review_triggered = "manual_review_triggered"
    joint_inspection_done = "joint_inspection_done"
    resolution_confirmed = "resolution_confirmed"
    verification_requested = "verification_requested"
    # deadline + escalation
    deadline_set = "deadline_set"
    deadline_breached = "deadline_breached"
    in_progress_update = "in_progress_update"
    escalated_to_oversight = "escalated_to_oversight"
    false_resolution_escalated = "false_resolution_escalated"
    # utility / specialized
    tanker_deployed = "tanker_deployed"
    pump_engineer_dispatched = "pump_engineer_dispatched"
    sample_collected = "sample_collected"
    cctv_inspection_done = "cctv_inspection_done"
    notice_issued = "notice_issued"
    djb_rejection = "djb_rejection"
    delhi_police_informed = "delhi_police_informed"
    diplomatic_note_raised = "diplomatic_note_raised"


class GeoPoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
