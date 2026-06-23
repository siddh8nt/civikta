// Mirrors the FastAPI contracts (services/api/app/schemas). Keep in sync, or
// generate from the backend OpenAPI later (packages/shared-types).

export type IssueStatus =
  | "draft" | "submitted" | "pending_verification" | "assigned"
  | "in_progress" | "resolved" | "rejected" | "reopened" | "manual_review";

export type Severity = "low" | "medium" | "high" | "critical";

export interface IssueSummary {
  id: string;
  title: string | null;
  public_summary: string | null;
  status: IssueStatus;
  latitude: number | null;
  longitude: number | null;
  ward_no: number | null;
  ward_name: string | null;
  locality_name: string | null;
  issue_category_slug: string | null;
  issue_type_slug: string | null;
  severity: Severity;
  urgency_score: number;
  corroboration_count: number;
  total_report_count: number;
  primary_authority_slug: string | null;
  secondary_authority_slug: string | null;
  created_at: string;
  cover_media_url: string | null;
  distance_m: number | null;
}

export interface TimelineEvent {
  event_type: string;
  actor_type: string;
  created_at: string;
  payload: Record<string, unknown>;
}

export interface IssueDetail extends IssueSummary {
  updated_at: string;
  canonical_description: string | null;
  routing_confidence: number | null;
  routing_reason: Record<string, unknown>;
  ai_summary: string | null;
  ai_confidence: number | null;
  last_corroborated_at: string | null;
  media_urls: string[];
  timeline: TimelineEvent[];
}

export interface ComplaintAnalysis {
  title: string;
  summary: string;
  issue_category: string;
  issue_type: string;
  asset_type: string | null;
  severity: Severity;
  obstruction_flag: boolean;
  health_hazard_flag: boolean;
  public_safety_flag: boolean;
  confidence: number;
  needs_manual_review: boolean;
}

export interface DuplicateCandidate {
  issue_id: string;
  title: string | null;
  distance_m: number;
  issue_type_slug: string | null;
  status: string | null;
  corroboration_count: number;
  score: number;
}

export interface DuplicateResult {
  has_candidate: boolean;
  best_candidate: DuplicateCandidate | null;
  candidates: DuplicateCandidate[];
  recommendation: "none" | "possible" | "strong";
}

export interface GeoResolution {
  local_body_type: string | null;
  ward_no: number | null;
  ward_name: string | null;
  locality_name: string | null;
  in_delhi: boolean;
  confidence: number;
}

export interface AnalyzeResult {
  report_id: string;
  analysis: ComplaintAnalysis;
  geo: GeoResolution;
  duplicates: DuplicateResult;
}

export interface SubmitResult {
  outcome: "created" | "corroborated";
  issue_id: string;
  status: IssueStatus;
}

export interface OversightAlert {
  ward_no: number | null;
  ward_name: string | null;
  category_slug: string | null;
  severity: "watch" | "alert" | "critical";
  headline: string;
  metrics: Record<string, number>;
}
