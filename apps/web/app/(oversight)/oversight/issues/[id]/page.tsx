"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueDetail } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { eventLabel } from "@/lib/labels";

export default function OversightIssueDetailPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    api.issue(params.id).then(setIssue).catch(() => setErr(true));
  }, [params.id]);

  if (err) return <main className="dashboard-shell text-sm text-rose-500">Issue not found.</main>;
  if (!issue) return <main className="dashboard-shell text-sm text-slate-400">Loading…</main>;

  const isEscalated = issue.status === "reopened";
  const filedDaysAgo = Math.floor(
    (Date.now() - new Date(issue.created_at).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <main className="dashboard-shell">
      <div className="mb-4 flex items-center gap-3">
        <Link href="/oversight/issues" className="text-sm text-slate-500">← All issues</Link>
        {isEscalated && (
          <span className="rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-bold text-rose-700">
            ⚠ ESCALATED
          </span>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-[1fr_300px]">

        {/* ── LEFT ── */}
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
              {issue.locality_name} · Ward {issue.ward_no} ·{" "}
              Filed {filedDaysAgo}d ago
            </p>
          </div>

          {issue.media_urls[0] && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={issue.media_urls[0]} alt="" className="max-h-64 w-full rounded-xl object-cover" />
          )}

          {/* AI Summary */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Gemini AI Summary</p>
            <p className="text-sm text-slate-700">{issue.ai_summary ?? issue.canonical_description ?? "No summary."}</p>
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
                  Confidence: {Math.round(issue.routing_confidence * 100)}%
                </p>
              )}
            </div>
          )}

          {/* Track Issue Progress */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Track Issue Progress ({issue.timeline.length} events)
            </p>
            {issue.timeline.length === 0 ? (
              <p className="text-sm text-slate-400">No events.</p>
            ) : (
              <ol className="space-y-3 border-l-2 border-slate-200 pl-4">
                {issue.timeline.filter(e => !["issue_corroborated","urgency_score_updated"].includes(e.event_type)).map((e, i) => (
                  <li key={i} className="relative text-sm">
                    <span className={`absolute -left-[21px] top-1.5 h-2 w-2 rounded-full ${
                      e.event_type === "reopened" ? "bg-rose-500" :
                      e.event_type === "resolved" ? "bg-green-500" :
                      e.event_type === "still_unresolved_confirmed" ? "bg-orange-400" :
                      "bg-slate-400"
                    }`} />
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-800">{eventLabel(e.event_type)}</span>
                      <span className="rounded bg-slate-100 px-1 py-0.5 text-[10px] text-slate-500">
                        {e.actor_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{new Date(e.created_at).toLocaleString()}</p>
                    {e.payload?.status_reason != null && (
                      <p className="mt-0.5 text-xs text-slate-500 italic">"{String(e.payload.status_reason)}"</p>
                    )}
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>

        {/* ── RIGHT ── */}
        <aside className="space-y-4">
          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Issue signals</p>
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
            <Row k="Days open" v={String(filedDaysAgo)} />
          </div>

          {isEscalated && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900 space-y-1">
              <p className="font-bold text-xs uppercase tracking-wide text-rose-600">Escalation active</p>
              <p>Citizen disputed the resolution. Authority supervisor has been notified.</p>
              <p className="text-xs text-rose-700 mt-1">
                Monitor this issue until re-resolved or further action taken.
              </p>
            </div>
          )}

          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Oversight actions</p>
            <p className="text-xs text-slate-400 italic">
              Read-only view. Use the analytics chatbot to generate audit reports or policy recommendations.
            </p>
            <Link
              href="/oversight/analytics"
              className="mt-3 block w-full rounded-lg bg-violet-600 py-2 text-center text-sm font-semibold text-white hover:bg-violet-700"
            >
              Open analytics chatbot →
            </Link>
          </div>
        </aside>
      </div>
    </main>
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
