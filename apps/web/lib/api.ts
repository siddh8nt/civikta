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

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type DemoRole = "citizen" | "authority" | "oversight";

function headers(role: DemoRole = "citizen"): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Demo-User": `demo-${role}`,
    "X-Demo-Role": role,
  };
}

async function req<T>(path: string, init?: RequestInit, role: DemoRole = "citizen"): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...headers(role), ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} on ${path}`);
  return res.json() as Promise<T>;
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

  // raise flow
  createDraft: (body: { raw_description: string; latitude: number; longitude: number; media_urls?: string[] }) =>
    req<{ report_id: string }>(`/api/reports/draft`, { method: "POST", body: JSON.stringify(body) }),
  analyze: (reportId: string) =>
    req<AnalyzeResult>(`/api/reports/${reportId}/analyze`, { method: "POST" }),
  checkDuplicate: (reportId: string) =>
    req<DuplicateResult>(`/api/reports/${reportId}/check-duplicate`, { method: "POST" }),
  submit: (reportId: string, body: { corroborate: boolean; target_issue_id?: string; still_unresolved?: boolean }) =>
    req<SubmitResult>(`/api/reports/${reportId}/submit`, { method: "POST", body: JSON.stringify(body) }),

  // authority
  authorityQueue: (params: { authority?: string; sort?: string } = {}) => {
    const q = new URLSearchParams(params as Record<string, string>).toString();
    return req<IssueSummary[]>(`/api/authority/issues?${q}`, {}, "authority");
  },
  updateStatus: (id: string, body: { status: string; status_reason?: string }) =>
    req<IssueDetail>(`/api/authority/issues/${id}/status`, { method: "POST", body: JSON.stringify(body) }, "authority"),

  // oversight
  oversightSummary: () => req<Record<string, unknown>>(`/api/oversight/summary`, {}, "oversight"),
  oversightHotspots: () => req<Record<string, unknown>[]>(`/api/oversight/hotspots`, {}, "oversight"),
  oversightAlerts: () => req<OversightAlert[]>(`/api/oversight/alerts`, {}, "oversight"),
};
