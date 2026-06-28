"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { api } from "@/lib/api";
import type { IssueDetail } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { issueTypeLabel, eventLabel } from "@/lib/labels";
import { AuthorityBanner } from "@/components/AuthorityBanner";

const REJECTION_REASONS = [
  "Duplicate — already being handled",
  "Out of jurisdiction — wrong authority",
  "Invalid complaint — not a civic issue",
  "Issue already resolved prior to report",
  "Insufficient information to act",
];

const REROUTE_AUTHORITIES = [
  "mcd_sanitation", "mcd_engineering", "mcd_horticulture", "mcd_public_health",
  "ndmc_civil", "ndmc_sanitation", "ndmc_horticulture",
  "dcb_civic", "djb", "pwd", "ifcd", "dda", "delhi_police", "nhai",
];

type ActionPanel = "none" | "in_progress" | "resolve" | "reject" | "reroute";

function addHours(h: number): string {
  return new Date(Date.now() + h * 3600_000).toISOString().slice(0, 16);
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((res, rej) => {
    const reader = new FileReader();
    reader.onload = () => res((reader.result as string).split(",")[1]);
    reader.onerror = rej;
    reader.readAsDataURL(file);
  });
}

function payloadString(payload: Record<string, unknown>, key: string): string | null {
  const value = payload[key];
  return typeof value === "string" && value.length > 0 ? value : null;
}

function AuthorityIssueDetailInner({ id }: { id: string }) {
  const searchParams = useSearchParams();
  const authoritySlug = searchParams.get("authority") ?? "";

  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [busy, setBusy] = useState(false);
  const [panel, setPanel] = useState<ActionPanel>("none");

  // In-progress form state
  const [ipTitle, setIpTitle] = useState("");
  const [ipDescription, setIpDescription] = useState("");
  const [ipDeadline, setIpDeadline] = useState(addHours(1));
  const [ipPhoto, setIpPhoto] = useState<string | null>(null);
  const [ipPhotoPreview, setIpPhotoPreview] = useState<string | null>(null);
  const ipFileRef = useRef<HTMLInputElement>(null);

  // Resolve form state
  const [resolveNote, setResolveNote] = useState("");
  const [resolvePhoto, setResolvePhoto] = useState<string | null>(null);
  const [resolvePhotoPreview, setResolvePhotoPreview] = useState<string | null>(null);
  const [resolveDeadline, setResolveDeadline] = useState(addHours(24));
  const resolveFileRef = useRef<HTMLInputElement>(null);

  // Reject / reroute form state
  const [rejectReason, setRejectReason] = useState(REJECTION_REASONS[0]);
  const [rerouteSlug, setRerouteSlug] = useState(REROUTE_AUTHORITIES[0]);
  const [rerouteNote, setRerouteNote] = useState("");

  const load = () => api.issue(id).then(setIssue).catch(() => setNotFound(true));
  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handlePhotoChange(
    file: File,
    setData: (v: string) => void,
    setPreview: (v: string) => void,
  ) {
    setPreview(URL.createObjectURL(file));
    const b64 = await fileToBase64(file);
    setData(b64);
  }

  async function doStatus(
    status: string,
    extra: {
      reason?: string;
      deadline_iso?: string;
      update_title?: string;
      update_description?: string;
      proof_image_data?: string;
      reroute_to_authority?: string;
    } = {},
  ) {
    setBusy(true);
    try {
      const updated = await api.updateStatus(id, {
        status,
        status_reason: extra.reason,
        deadline_iso: extra.deadline_iso,
        update_title: extra.update_title,
        update_description: extra.update_description,
        proof_image_data: extra.proof_image_data,
        reroute_to_authority: extra.reroute_to_authority,
      });
      setIssue(updated);
      setPanel("none");
      // reset form state
      setIpTitle(""); setIpDescription(""); setIpDeadline(addHours(1));
      setIpPhoto(null); setIpPhotoPreview(null);
      setResolveNote(""); setResolvePhoto(null); setResolvePhotoPreview(null);
    } finally {
      setBusy(false);
    }
  }

  function togglePanel(p: ActionPanel) {
    setPanel((cur) => (cur === p ? "none" : p));
  }

  if (notFound) return (
    <><AuthorityBanner /><main className="dashboard-shell">
      <p className="mb-2 text-sm text-rose-500 font-semibold">Issue not found.</p>
      <p className="text-xs text-slate-400">Check the ID and try again — enter only the digits after CIV-</p>
    </main></>
  );
  if (!issue) return <main className="dashboard-shell text-sm text-slate-400">Loading…</main>;

  const status = issue.status;
  const canMarkInProgress = ["submitted", "assigned", "reopened"].includes(status);
  const canResolve = ["in_progress", "submitted", "assigned", "reopened"].includes(status);
  const canReject = !["rejected", "closed"].includes(status);
  const canReroute = !["resolved", "rejected", "closed"].includes(status);
  const isTerminal = ["resolved", "rejected", "closed"].includes(status);

  const ipFormValid = ipTitle.trim().length > 0 && ipDescription.trim().length > 0 && !!ipDeadline;
  const resolveFormValid = resolveNote.trim().length > 0 && !!resolvePhoto;

  return (
    <>
      <AuthorityBanner />
      <main className="dashboard-shell">
      <div className="mb-4">
        <Link href="/authority/issues" className="text-sm text-slate-500">← Back to queue</Link>
      </div>

      <div className="grid gap-6 md:grid-cols-[1fr_340px]">

        {/* ── LEFT: Issue content ── */}
        <div className="space-y-4">
          <div>
            <IssueIdChip id={issue.id} />
            <div className="mb-2 flex flex-wrap gap-1.5">
              <StatusBadge status={issue.status} />
              <SeverityBadge severity={issue.severity} />
              {issue.corroboration_count > 0 && (
                <span className="rounded-full bg-teal-100 px-2 py-0.5 text-xs font-semibold text-teal-700">
                  {issue.corroboration_count} corroborations
                </span>
              )}
            </div>
            <h1 className="text-xl font-bold text-slate-900">{issue.title}</h1>
            <p className="text-sm text-slate-500">
              {issue.locality_name} · Ward {issue.ward_no} · {issueTypeLabel(issue.issue_type_slug)}
            </p>
          </div>

          {issue.media_urls[0] && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={issue.media_urls[0]} alt="" className="max-h-72 w-full rounded-xl object-cover" />
          )}

          {/* AI Summary */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Gemini AI Summary</p>
            <p className="text-sm text-slate-700">{issue.ai_summary ?? issue.canonical_description ?? "No summary available."}</p>
            {issue.ai_confidence != null && (
              <p className="mt-1 text-xs text-slate-400">Confidence: {Math.round(issue.ai_confidence * 100)}%</p>
            )}
          </div>

          {/* Routing reasoning */}
          {issue.routing_reason && Object.keys(issue.routing_reason).length > 0 && (
            <div className="rounded-xl border border-blue-100 bg-blue-50 p-4">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-600">Routing Rationale</p>
              <div className="space-y-1">
                {Object.entries(issue.routing_reason).map(([k, v]) => (
                  <div key={k} className="flex gap-2 text-xs">
                    <span className="text-slate-400">{k.replace(/_/g, " ")}:</span>
                    <span className="text-slate-700">{v != null ? String(v) : "—"}</span>
                  </div>
                ))}
              </div>
              {issue.routing_confidence != null && (
                <p className="mt-2 text-xs text-blue-500">
                  Routing confidence: {Math.round(issue.routing_confidence * 100)}%
                </p>
              )}
            </div>
          )}

          {/* Track Issue Progress */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Track Issue Progress</p>
            {issue.timeline.length === 0 ? (
              <p className="text-sm text-slate-400">No events yet.</p>
            ) : (
              <ol className="space-y-3 border-l-2 border-slate-200 pl-4">
                {issue.timeline
                  .filter(e => !["issue_corroborated", "urgency_score_updated"].includes(e.event_type))
                  .map((e, i) => (
                    <li key={i} className="relative text-sm">
                      <span className={`absolute -left-[21px] top-1.5 h-2 w-2 rounded-full ${
                        e.event_type === "deadline_set" ? "bg-amber-400" :
                        e.event_type === "deadline_breached" ? "bg-red-500" :
                        e.event_type === "escalated_to_oversight" ? "bg-red-600" :
                        e.event_type === "resolved" ? "bg-green-500" :
                        e.event_type === "in_progress_update" ? "bg-blue-400" :
                        "bg-slate-400"
                      }`} />
                      <span className="font-medium text-slate-800">{eventLabel(e.event_type)}</span>
                      {e.actor_type !== "system" && (
                        <span className="ml-1.5 rounded bg-slate-100 px-1 py-0.5 text-[10px] text-slate-500">
                          {e.actor_type}
                        </span>
                      )}
                      <span className="ml-2 text-xs text-slate-400">
                        {new Date(e.created_at).toLocaleString()}
                      </span>
                      {/* Deadline display */}
                      {e.event_type === "deadline_set" && payloadString(e.payload, "deadline") && (
                        <p className="mt-0.5 text-xs text-amber-700 font-medium">
                          Due by: {new Date(String(payloadString(e.payload, "deadline"))).toLocaleString()}
                        </p>
                      )}
                      {/* In-progress update details */}
                      {e.event_type === "in_progress_update" && (
                        <div className="mt-1 rounded-lg bg-blue-50 p-2 space-y-0.5">
                          {payloadString(e.payload, "title") && <p className="text-xs font-semibold text-blue-800">{payloadString(e.payload, "title")}</p>}
                          {payloadString(e.payload, "description") && <p className="text-xs text-blue-700">{payloadString(e.payload, "description")}</p>}
                          {payloadString(e.payload, "image_data") && (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={`data:image/jpeg;base64,${payloadString(e.payload, "image_data")}`}
                              alt="Update photo"
                              className="mt-1 max-h-32 rounded object-cover"
                            />
                          )}
                        </div>
                      )}
                      {/* Resolved proof photo */}
                      {e.event_type === "resolved" && payloadString(e.payload, "proof_image_data") && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={`data:image/jpeg;base64,${payloadString(e.payload, "proof_image_data")}`}
                          alt="Resolution proof"
                          className="mt-1 max-h-40 rounded-lg object-cover"
                        />
                      )}
                      {e.payload?.status_reason != null && (
                        <p className="mt-0.5 text-xs text-slate-500 italic">"{String(e.payload.status_reason)}"</p>
                      )}
                    </li>
                  ))}
              </ol>
            )}
          </div>
        </div>

        {/* ── RIGHT: Signals + Actions ── */}
        <aside className="space-y-4">

          {/* Signals */}
          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Signals</p>
            {issue.local_body_type && (
              <>
                <Row k="Local body" v={issue.local_body_type} />
                {issue.mcd_zone && (
                  <Row k="Zone" v={issue.mcd_zone} />
                )}
              </>
            )}
            <Row k="Primary authority" v={authorityLabel(issue.primary_authority_slug)} />
            {issue.secondary_authority_slug && (
              <Row k="Secondary" v={authorityLabel(issue.secondary_authority_slug)} />
            )}
            <Row k="Urgency score" v={issue.urgency_score.toFixed(1)} />
            <Row k="Corroborations" v={String(issue.corroboration_count)} />
            <Row k="Total reports" v={String(issue.total_report_count)} />
            <Row k="Filed" v={new Date(issue.created_at).toLocaleDateString()} />
          </div>

          {/* Action panel */}
          {!isTerminal && (
            <div className="rounded-xl border border-slate-200 p-4">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Actions</p>
              <div className="space-y-2">

                {/* ── Mark in progress ── */}
                {canMarkInProgress && (
                  <div>
                    <button
                      disabled={busy}
                      onClick={() => togglePanel("in_progress")}
                      className={`w-full rounded-lg py-2.5 text-sm font-semibold transition ${
                        panel === "in_progress"
                          ? "bg-blue-700 text-white"
                          : "bg-blue-600 text-white hover:bg-blue-700"
                      } disabled:opacity-40`}
                    >
                      Mark in progress
                    </button>
                    {panel === "in_progress" && (
                      <div className="mt-2 space-y-3 rounded-lg border border-blue-200 bg-blue-50 p-3">
                        <p className="text-xs font-semibold text-blue-800">Update details (required)</p>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-blue-700">Update title *</label>
                          <input
                            type="text"
                            value={ipTitle}
                            onChange={(e) => setIpTitle(e.target.value)}
                            placeholder="e.g. Repair crew dispatched"
                            className="w-full rounded-md border border-blue-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
                          />
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-blue-700">Description *</label>
                          <textarea
                            value={ipDescription}
                            onChange={(e) => setIpDescription(e.target.value)}
                            rows={2}
                            placeholder="Describe the action being taken…"
                            className="w-full rounded-md border border-blue-300 bg-white p-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
                          />
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-blue-700">
                            Deadline for next update *
                          </label>
                          <input
                            type="datetime-local"
                            value={ipDeadline}
                            onChange={(e) => setIpDeadline(e.target.value)}
                            min={new Date().toISOString().slice(0, 16)}
                            className="w-full rounded-md border border-blue-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                          />
                          <p className="mt-0.5 text-[10px] text-blue-600">Default: 1 hour from now</p>
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-blue-700">
                            Progress photo (optional)
                          </label>
                          <input
                            ref={ipFileRef}
                            type="file" accept="image/*" capture="environment"
                            className="hidden"
                            onChange={(e) => {
                              const f = e.target.files?.[0];
                              if (f) handlePhotoChange(f, setIpPhoto, setIpPhotoPreview);
                            }}
                          />
                          {ipPhotoPreview ? (
                            <div className="relative">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img src={ipPhotoPreview} alt="" className="max-h-32 w-full rounded-md object-cover" />
                              <button
                                onClick={() => { setIpPhoto(null); setIpPhotoPreview(null); }}
                                className="absolute right-1 top-1 rounded-full bg-black/60 px-1.5 py-0.5 text-[10px] text-white"
                              >✕</button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => ipFileRef.current?.click()}
                              className="flex w-full items-center justify-center gap-2 rounded-md border border-dashed border-blue-300 py-3 text-xs text-blue-600 hover:bg-blue-100 transition"
                            >
                              📷 Attach photo
                            </button>
                          )}
                        </div>

                        <button
                          disabled={busy || !ipFormValid}
                          onClick={() => doStatus("in_progress", {
                            deadline_iso: new Date(ipDeadline).toISOString(),
                            update_title: ipTitle.trim(),
                            update_description: ipDescription.trim(),
                            proof_image_data: ipPhoto ?? undefined,
                          })}
                          className="w-full rounded-lg bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-40"
                        >
                          {busy ? "Saving…" : "Confirm — mark in progress"}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* ── Mark resolved ── */}
                {canResolve && (
                  <div>
                    <button
                      disabled={busy}
                      onClick={() => togglePanel("resolve")}
                      className={`w-full rounded-lg py-2.5 text-sm font-semibold transition ${
                        panel === "resolve"
                          ? "bg-green-600 text-white"
                          : "border border-green-500 text-green-700 hover:bg-green-50"
                      } disabled:opacity-40`}
                    >
                      Mark resolved
                    </button>
                    {panel === "resolve" && (
                      <div className="mt-2 space-y-3 rounded-lg border border-green-200 bg-green-50 p-3">
                        <p className="text-xs font-semibold text-green-800">Photo evidence required</p>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-green-700">
                            Proof photo *
                          </label>
                          <input
                            ref={resolveFileRef}
                            type="file" accept="image/*" capture="environment"
                            className="hidden"
                            onChange={(e) => {
                              const f = e.target.files?.[0];
                              if (f) handlePhotoChange(f, setResolvePhoto, setResolvePhotoPreview);
                            }}
                          />
                          {resolvePhotoPreview ? (
                            <div className="relative">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img src={resolvePhotoPreview} alt="" className="max-h-40 w-full rounded-md object-cover" />
                              <button
                                onClick={() => { setResolvePhoto(null); setResolvePhotoPreview(null); }}
                                className="absolute right-1 top-1 rounded-full bg-black/60 px-1.5 py-0.5 text-[10px] text-white"
                              >✕</button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => resolveFileRef.current?.click()}
                              className="flex w-full items-center justify-center gap-2 rounded-md border border-dashed border-green-300 py-4 text-xs text-green-700 hover:bg-green-100 transition"
                            >
                              📸 Capture resolution proof photo
                            </button>
                          )}
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-green-700">Resolution note *</label>
                          <textarea
                            value={resolveNote}
                            onChange={(e) => setResolveNote(e.target.value)}
                            rows={2}
                            placeholder="Describe what was done to resolve this issue…"
                            className="w-full rounded-md border border-green-300 bg-white p-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-green-400"
                          />
                        </div>

                        <div>
                          <label className="mb-1 block text-xs font-medium text-green-700">
                            Citizen verification deadline
                          </label>
                          <input
                            type="datetime-local"
                            value={resolveDeadline}
                            onChange={(e) => setResolveDeadline(e.target.value)}
                            min={new Date().toISOString().slice(0, 16)}
                            className="w-full rounded-md border border-green-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-green-400"
                          />
                          <p className="mt-0.5 text-[10px] text-green-600">Citizen can dispute within this window</p>
                        </div>

                        {!resolvePhoto && (
                          <p className="rounded-md bg-amber-50 border border-amber-200 px-3 py-1.5 text-xs text-amber-700">
                            ⚠ Proof photo is mandatory before marking resolved
                          </p>
                        )}

                        <button
                          disabled={busy || !resolveFormValid}
                          onClick={() => doStatus("resolved", {
                            reason: resolveNote.trim(),
                            deadline_iso: new Date(resolveDeadline).toISOString(),
                            proof_image_data: resolvePhoto ?? undefined,
                          })}
                          className="w-full rounded-lg bg-green-600 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-40"
                        >
                          {busy ? "Saving…" : "Confirm resolution"}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* ── Reroute ── */}
                {canReroute && (
                  <div>
                    <button
                      disabled={busy}
                      onClick={() => togglePanel("reroute")}
                      className={`w-full rounded-lg py-2.5 text-sm font-semibold transition ${
                        panel === "reroute"
                          ? "bg-amber-500 text-white"
                          : "border border-slate-300 text-slate-700 hover:bg-slate-50"
                      } disabled:opacity-40`}
                    >
                      Reroute to another authority
                    </button>
                    {panel === "reroute" && (
                      <div className="mt-2 space-y-2 rounded-lg border border-amber-200 bg-amber-50 p-3">
                        <label className="text-xs font-medium text-amber-800">Transfer to</label>
                        <select
                          value={rerouteSlug}
                          onChange={(e) => setRerouteSlug(e.target.value)}
                          className="w-full rounded-md border border-amber-300 bg-white p-2 text-sm focus:outline-none focus:ring-1 focus:ring-amber-400"
                        >
                          {REROUTE_AUTHORITIES.map((a) => (
                            <option key={a} value={a}>{authorityLabel(a)}</option>
                          ))}
                        </select>
                        <textarea
                          value={rerouteNote}
                          onChange={(e) => setRerouteNote(e.target.value)}
                          rows={2}
                          placeholder="Reason for transfer…"
                          className="w-full rounded-md border border-amber-300 bg-white p-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                        />
                        <button
                          disabled={busy}
                          onClick={() => doStatus("assigned", { 
                            reason: `Rerouted to ${authorityLabel(rerouteSlug)}. ${rerouteNote}`,
                            reroute_to_authority: rerouteSlug
                          })}
                          className="w-full rounded-lg bg-amber-500 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-40"
                        >
                          {busy ? "Saving…" : "Confirm reroute"}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* ── Reject ── */}
                {canReject && (
                  <div>
                    <button
                      disabled={busy}
                      onClick={() => togglePanel("reject")}
                      className={`w-full rounded-lg py-2.5 text-sm font-semibold transition ${
                        panel === "reject"
                          ? "bg-rose-600 text-white"
                          : "border border-rose-300 text-rose-600 hover:bg-rose-50"
                      } disabled:opacity-40`}
                    >
                      Reject
                    </button>
                    {panel === "reject" && (
                      <div className="mt-2 space-y-2 rounded-lg border border-rose-200 bg-rose-50 p-3">
                        <label className="text-xs font-medium text-rose-800">Rejection reason</label>
                        <select
                          value={rejectReason}
                          onChange={(e) => setRejectReason(e.target.value)}
                          className="w-full rounded-md border border-rose-300 bg-white p-2 text-sm focus:outline-none focus:ring-1 focus:ring-rose-400"
                        >
                          {REJECTION_REASONS.map((r) => (
                            <option key={r} value={r}>{r}</option>
                          ))}
                        </select>
                        <button
                          disabled={busy}
                          onClick={() => doStatus("rejected", { reason: rejectReason })}
                          className="w-full rounded-lg bg-rose-600 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-40"
                        >
                          {busy ? "Saving…" : "Confirm rejection"}
                        </button>
                      </div>
                    )}
                  </div>
                )}

              </div>
            </div>
          )}

          {/* Terminal state notice */}
          {isTerminal && (
            <div className={`rounded-xl border p-4 text-sm ${
              status === "resolved" ? "border-green-200 bg-green-50 text-green-800" :
              status === "rejected" ? "border-rose-200 bg-rose-50 text-rose-800" :
              "border-slate-200 bg-slate-50 text-slate-600"
            }`}>
              <p className="font-semibold">
                {status === "resolved" ? "Marked as resolved" :
                 status === "rejected" ? "Issue rejected" : "Issue closed"}
              </p>
              {issue.status_reason && (
                <p className="mt-1 text-xs opacity-80">"{issue.status_reason}"</p>
              )}
            </div>
          )}

        </aside>
      </div>
    </main>
    </>
  );
}

export default function AuthorityIssueDetailPage({ params }: { params: { id: string } }) {
  return (
    <Suspense fallback={<><AuthorityBanner /><main className="dashboard-shell text-sm text-slate-400">Loading…</main></>}>
      <AuthorityIssueDetailInner id={params.id} />
    </Suspense>
  );
}

function IssueIdChip({ id }: { id: string }) {
  const short = id.slice(0, 8).toUpperCase();
  return (
    <div className="mb-2 inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Issue ID</span>
      <span className="font-mono text-xs font-bold text-slate-700">CIV-{short}</span>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3 py-0.5 text-sm">
      <span className="text-slate-400">{k}</span>
      <span className="text-right font-medium text-slate-700">{v}</span>
    </div>
  );
}
