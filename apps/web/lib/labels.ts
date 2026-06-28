// ── Issue categories ──────────────────────────────────────────────────────────
const CATEGORY_LABELS: Record<string, string> = {
  water_sewer_drainage:  "Water & Drainage",
  roads_streets:         "Roads & Streets",
  garbage_sanitation:    "Garbage & Sanitation",
  lights_electrical:     "Street Lights & Electrical",
  parks_public_space:    "Parks & Public Spaces",
  public_safety_hazard:  "Public Safety Hazard",
  encroachment:          "Encroachment",
  environmental_hazard:  "Environmental Hazard",
};

export function categoryLabel(slug: string | null | undefined): string {
  if (!slug) return "—";
  return CATEGORY_LABELS[slug] ?? slug.replace(/_/g, " ");
}

// ── Issue types ───────────────────────────────────────────────────────────────
const ISSUE_TYPE_LABELS: Record<string, string> = {
  sewer_overflow:          "Sewer Overflow",
  pothole_major_road:      "Pothole on Major Road",
  pothole_local_road:      "Pothole on Local Lane",
  no_water_supply:         "No Water Supply",
  footpath_encroachment:   "Footpath Encroachment",
  tree_hazard:             "Dangerous Tree",
  dead_animal:             "Dead Animal on Road",
  garbage_not_collected:   "Garbage Not Collected",
  road_obstruction:        "Road Obstruction",
  broken_footpath:         "Broken Footpath",
  contaminated_water:      "Contaminated Water Supply",
  stray_dog_issue:         "Stray Dog Menace",
  waterlogging:            "Waterlogging",
  illegal_dumping:         "Illegal Waste Dumping",
  park_maintenance_issue:  "Park Maintenance",
  streetlight_not_working: "Streetlight Not Working",
  clogged_local_drain:     "Clogged Local Drain",
  road_cave_in:            "Road Cave-In",
  road_subsidence:         "Road Sinking",
  hanging_wire:            "Dangerous Hanging Wire",
  electricity_hazard:      "Electrical Hazard",
  public_toilet_issue:     "Public Toilet Issue",
  dengue_breeding:         "Dengue Breeding Site",
  collapsed_structure:     "Collapsed Structure",
  drain_pollution:         "Drain Pollution",
};

export function issueTypeLabel(slug: string | null | undefined): string {
  if (!slug) return "—";
  return ISSUE_TYPE_LABELS[slug] ?? slug.replace(/_/g, " ");
}

// ── Statuses ──────────────────────────────────────────────────────────────────
const STATUS_LABELS: Record<string, string> = {
  submitted:            "Submitted",
  pending_verification: "Under Verification",
  assigned:             "Assigned",
  in_progress:          "Work in Progress",
  resolved:             "Resolved",
  reopened:             "Reopened",
  rejected:             "Rejected",
  manual_review:        "Under Review",
};

export function statusLabel(status: string | null | undefined): string {
  if (!status) return "—";
  return STATUS_LABELS[status] ?? status.replace(/_/g, " ");
}

// ── Severity ──────────────────────────────────────────────────────────────────
const SEVERITY_LABELS: Record<string, string> = {
  low:      "Low",
  medium:   "Medium",
  high:     "High",
  critical: "Critical",
};

export function severityLabel(s: string | null | undefined): string {
  if (!s) return "—";
  return SEVERITY_LABELS[s] ?? s;
}

// ── Timeline event types ──────────────────────────────────────────────────────
const EVENT_LABELS: Record<string, string> = {
  created:                    "Issue Reported",
  classified:                 "AI Classification Done",
  assigned:                   "Assigned to Authority",
  issue_corroborated:         "Community Corroboration",
  urgency_score_updated:      "Urgency Score Updated",
  authority_acknowledged:     "Authority Acknowledged",
  resolved:                   "Marked as Resolved",
  reopened:                   "Reopened by Citizen",
  still_unresolved_confirmed: "Citizen Confirmed Still Unresolved",
  field_visit_scheduled:      "Field Visit Scheduled",
  field_visit_completed:      "Field Visit Completed",
  tanker_deployed:            "Water Tanker Deployed",
  repair_scheduled:           "Repair Scheduled",
  sample_collected:           "Water Sample Collected",
  cctv_inspection_done:       "CCTV Inspection Done",
  resolution_confirmed:       "Resolution Confirmed by Citizen",
  verification_requested:     "Sent for Verification",
  routed:                     "Routed to Authority",
  authority_rejected:         "Authority Rejected Responsibility",
  rerouted:                   "Re-routed to Different Authority",
  manual_review_triggered:    "Flagged for Manual Review",
  joint_inspection_done:      "Joint Inspection Completed",
  pump_engineer_dispatched:   "Pump Engineer Dispatched",
  diplomatic_note_raised:     "Escalated via Diplomatic Channel",
  notice_issued:              "Legal Notice Issued to Violator",
  djb_rejection:              "Delhi Jal Board Rejected Responsibility",
  delhi_police_informed:      "Delhi Police Notified",
  // deadline & escalation
  deadline_set:               "Deadline Set by Authority",
  deadline_breached:          "Deadline Breached — Escalating",
  in_progress_update:         "Authority Progress Update",
  escalated_to_oversight:     "Escalated to Oversight Authority",
  false_resolution_escalated: "False Resolution Flagged — Escalated",
};

export function eventLabel(eventType: string | null | undefined): string {
  if (!eventType) return "—";
  return EVENT_LABELS[eventType] ?? eventType.replace(/_/g, " ");
}

// ── Merge decision ────────────────────────────────────────────────────────────
const MERGE_LABELS: Record<string, string> = {
  merged:    "Merged with similar report",
  canonical: "Primary report",
  rejected:  "Rejected (duplicate)",
  pending:   "Awaiting review",
};

export function mergeLabel(decision: string | null | undefined): string {
  if (!decision || decision === "—") return "—";
  return MERGE_LABELS[decision] ?? decision.replace(/_/g, " ");
}
