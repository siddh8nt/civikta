"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueDetail } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";

const ACTIONS = [
  { status: "in_progress", label: "Mark in progress" },
  { status: "resolved", label: "Mark resolved" },
  { status: "rejected", label: "Reject" },
];

export default function AuthorityIssueDetailPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [busy, setBusy] = useState(false);

  const load = () => api.issue(params.id).then(setIssue).catch(() => setIssue(null));
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function setStatus(status: string) {
    setBusy(true);
    try {
      const updated = await api.updateStatus(params.id, { status });
      setIssue(updated);
    } finally {
      setBusy(false);
    }
  }

  if (!issue) return <main className="dashboard-shell text-sm text-slate-400">Loading…</main>;

  return (
    <main className="dashboard-shell">
      <Link href="/authority/issues" className="text-sm text-slate-500">← Queue</Link>
      <div className="mt-3 grid gap-6 md:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <div>
            <div className="mb-2 flex gap-1.5">
              <StatusBadge status={issue.status} />
              <SeverityBadge severity={issue.severity} />
            </div>
            <h1 className="text-xl font-bold">{issue.title}</h1>
            <p className="text-sm text-slate-500">
              {issue.locality_name} · Ward {issue.ward_no} · {issue.issue_type_slug}
            </p>
          </div>
          {issue.media_urls[0] && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={issue.media_urls[0]} alt="" className="max-h-72 rounded-xl object-cover" />
          )}
          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="font-medium">AI summary</p>
            <p className="mt-1 text-slate-600">{issue.ai_summary}</p>
          </div>
          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="mb-1 font-medium">Timeline</p>
            <ol className="space-y-1 text-slate-600">
              {issue.timeline.map((e, i) => (
                <li key={i}>
                  {e.event_type.replace(/_/g, " ")} ·{" "}
                  <span className="text-xs text-slate-400">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                </li>
              ))}
            </ol>
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border border-slate-200 p-4 text-sm">
            <p className="mb-2 font-medium">Routing & signals</p>
            <Row k="Primary" v={issue.primary_authority_slug ?? "—"} />
            {issue.secondary_authority_slug && <Row k="Secondary" v={issue.secondary_authority_slug} />}
            <Row k="Routing conf." v={`${Math.round((issue.routing_confidence ?? 0) * 100)}%`} />
            <Row k="Corroborations" v={String(issue.corroboration_count)} />
            <Row k="Urgency" v={issue.urgency_score.toFixed(1)} />
          </div>
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="mb-2 text-sm font-medium">Update status</p>
            <div className="space-y-2">
              {ACTIONS.map((a) => (
                <button
                  key={a.status}
                  disabled={busy}
                  onClick={() => setStatus(a.status)}
                  className="w-full rounded-lg border border-slate-300 py-2 text-sm font-medium hover:border-brand disabled:opacity-40"
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3 py-0.5">
      <span className="text-slate-400">{k}</span>
      <span className="text-right font-medium capitalize">{v.replace(/_/g, " ")}</span>
    </div>
  );
}
