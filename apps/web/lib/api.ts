// Typed client for the CIVIKTA backend.
// Demo auth: sends X-Demo-User / X-Demo-Role headers that the backend's StubAuth
// trusts. Swap for a Firebase ID token (Authorization: Bearer ...) when
// CIVIKTA_AUTH=firebase is wired.

import type {
  AnalyzeResult,
  DuplicateResult,
  IssueDetail,
  IssueSummary,
  OversightAlert,
  SubmitResult,
} from "./types";
import { supabase } from "./supabase";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export type DemoRole = "citizen" | "authority" | "oversight";

async function headers(role: DemoRole = "citizen"): Promise<HeadersInit> {
  if (role === "citizen") {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.access_token}`,
      };
    }
  }
  // Authority / oversight portals use demo headers (no real auth needed)
  return {
    "Content-Type": "application/json",
    "X-Demo-User": `demo-${role}`,
    "X-Demo-Role": role,
  };
}

// Strip stray symbols Gemini occasionally injects as title separators
const TITLE_JUNK = /[◆◇•·▪▸►→]/g;
function scrubTitles<T>(data: T): T {
  if (!data || typeof data !== "object") return data;
  if (Array.isArray(data)) return data.map(scrubTitles) as unknown as T;
  const obj = data as Record<string, unknown>;
  if ("title" in obj && typeof obj.title === "string") {
    obj.title = obj.title.replace(TITLE_JUNK, " ").replace(/\s{2,}/g, " ").trim();
  }
  return obj as T;
}

async function req<T>(path: string, init?: RequestInit, role: DemoRole = "citizen"): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...(await headers(role)), ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return scrubTitles(await res.json() as T);
}

export const api = {
  // citizen
  feedNearby: (lat: number, lng: number, radius = 3000) =>
    req<IssueSummary[]>(`/api/feed/nearby?lat=${lat}&lng=${lng}&radius=${radius}`),
  mapIssues: (b: { minLat: number; minLng: number; maxLat: number; maxLng: number }) =>
    req<IssueSummary[]>(
      `/api/map/issues?minLat=${b.minLat}&minLng=${b.minLng}&maxLat=${b.maxLat}&maxLng=${b.maxLng}`,
    ),
  issue: (id: string) => req<IssueDetail>(`/api/issues/${id}`),
  corroborate: (id: string, body: { still_unresolved?: boolean; affected_too?: boolean; note?: string }) =>
    req(`/api/issues/${id}/corroborate`, { method: "POST", body: JSON.stringify(body) }),
  requestEscalation: (id: string) =>
    req<{ status: string }>(`/api/issues/${id}/request-escalation`, { method: "POST" }),

  // raise flow
  validateImages: (imageData: string[]) =>
    req<{ valid: boolean; civic_issue_detected: boolean; rejection_reason: string; issue_hint: string; confidence: number }>(
      `/api/reports/validate-images`,
      { method: "POST", body: JSON.stringify({ image_data: imageData }) },
    ),
  createDraft: (body: { raw_description?: string; latitude: number; longitude: number; media_urls?: string[]; image_data?: string[]; audio_data?: string }) =>
    req<{ report_id: string }>(`/api/reports/draft`, { method: "POST", body: JSON.stringify(body) }),
  analyze: (reportId: string) =>
    req<AnalyzeResult>(`/api/reports/${reportId}/analyze`, { method: "POST" }),
  checkDuplicate: (reportId: string) =>
    req<DuplicateResult>(`/api/reports/${reportId}/check-duplicate`, { method: "POST" }),
  submit: (reportId: string, body: { corroborate: boolean; target_issue_id?: string; still_unresolved?: boolean }) =>
    req<SubmitResult>(`/api/reports/${reportId}/submit`, { method: "POST", body: JSON.stringify(body) }),

  // authority
  authorityQueue: (params: { authority?: string; sort?: string; status?: string; severity?: string } = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
    ).toString();
    return req<IssueSummary[]>(`/api/authority/issues?${q}`, {}, "authority");
  },
  updateStatus: (id: string, body: {
    status: string;
    status_reason?: string;
    deadline_iso?: string;
    update_title?: string;
    update_description?: string;
    proof_image_data?: string;
    reroute_to_authority?: string;
  }) =>
    req<IssueDetail>(`/api/authority/issues/${id}/status`, { method: "POST", body: JSON.stringify(body) }, "authority"),
  authorityEscalations: () =>
    req<IssueSummary[]>(`/api/authority/escalations`, {}, "authority"),

  // users
  upsertMe: (body: { name?: string; phone?: string; password_hash?: string; ward_no?: number | null; ward_name?: string | null; zone?: string | null; local_body_type?: string | null; home_lat?: number | null; home_lng?: number | null }) =>
    req<{ id: string }>(`/api/users/me`, { method: "POST", body: JSON.stringify(body) }),
  getMe: () => req<{ id: string; name?: string; role: string }>(`/api/users/me`),
  signin: (body: { phone: string; password_hash: string }) =>
    req<{ id: string; name?: string; phone?: string; home_lat?: number | null; home_lng?: number | null; ward_no?: number | null; ward_name?: string | null; zone?: string | null; local_body_type?: string | null }>(
      `/api/users/signin`,
      { method: "POST", body: JSON.stringify(body) },
    ),

  // citizen reports
  myReports: () => req<Record<string, unknown>[]>(`/api/reports/mine`),

  // geo
  geoResolve: (lat: number, lng: number) =>
    req<{ ward_no: number | null; ward_name: string | null; zone: string | null; local_body_type: string | null; locality_name: string | null; in_delhi: boolean; confidence: number }>(
      `/api/geo/resolve?lat=${lat}&lng=${lng}`,
    ),

  // oversight
  oversightSummary: () => req<Record<string, unknown>>(`/api/oversight/summary`, {}, "oversight"),
  oversightHotspots: () => req<Record<string, unknown>[]>(`/api/oversight/hotspots`, {}, "oversight"),
  oversightAlerts: () => req<OversightAlert[]>(`/api/oversight/alerts`, {}, "oversight"),

  // analytics chatbot
  analyticsQuery: (
    question: string,
    context: Record<string, string> = {},
    history: { role: "user" | "assistant"; text: string }[] = [],
  ) =>
    req<{
      answer: string;
      tool_calls: { name: string; args: Record<string, unknown>; result: unknown }[];
      suggested_questions: string[];
    }>(
      `/api/analytics/query`,
      { method: "POST", body: JSON.stringify({ question, context, history }) },
      "oversight",
    ),
};
