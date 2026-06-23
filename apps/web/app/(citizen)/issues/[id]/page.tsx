"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueDetail } from "@/lib/types";
import { SeverityBadge, StatusBadge, VerifiedBadge } from "@/components/ui/badges";

export default function IssueDetailPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [err, setErr] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = () => api.issue(params.id).then(setIssue).catch(() => setErr(true));
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function act(body: { still_unresolved?: boolean; affected_too?: boolean }) {
    setBusy(true);
    try {
      await api.corroborate(params.id, body);
      await load();
    } finally {
      setBusy(false);
    }
  }

  if (err) return <main className="p-6 text-sm text-rose-500">Issue not found.</main>;
  if (!issue) return <main className="p-6 text-sm text-slate-400">Loading…</main>;

  return (
    <main className="pb-24">
      {issue.media_urls[0] && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={issue.media_urls[0]} alt="" className="h-52 w-full object-cover" />
      )}
      <div className="space-y-5 p-4">
        <div>
          <div className="mb-2 flex flex-wrap gap-1.5">
            <StatusBadge status={issue.status} />
            <SeverityBadge severity={issue.severity} />
            <VerifiedBadge count={issue.corroboration_count} />
          </div>
          <h1 className="text-lg font-bold leading-snug">{issue.title}</h1>
          <p className="mt-1 text-xs text-slate-500">
            {issue.locality_name ?? "Delhi"} · Ward {issue.ward_no ?? "—"} ·{" "}
            {new Date(issue.created_at).toLocaleDateString()}
          </p>
        </div>

        <Section title="Summary">
          <p className="text-sm text-slate-600">{issue.ai_summary ?? issue.public_summary}</p>
        </Section>

        <Section title="Routing">
          <div className="rounded-lg bg-slate-50 p-3 text-sm">
            <Row k="Primary" v={issue.primary_authority_slug ?? "—"} />
            {issue.secondary_authority_slug && <Row k="Secondary" v={issue.secondary_authority_slug} />}
            <Row k="Confidence" v={`${Math.round((issue.routing_confidence ?? 0) * 100)}%`} />
            <Row k="Urgency score" v={issue.urgency_score.toFixed(1)} />
          </div>
        </Section>

        <Section title="Community Verification">
          <div className="rounded-lg border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
            <p>✓ Corroborated by {issue.corroboration_count} residents</p>
            <p className="text-xs">
              {issue.total_report_count} total reports
              {issue.last_corroborated_at &&
                ` · latest ${new Date(issue.last_corroborated_at).toLocaleString()}`}
            </p>
          </div>
        </Section>

        <Section title="Timeline">
          <ol className="space-y-2 border-l-2 border-slate-200 pl-4 text-sm">
            {issue.timeline.map((e, i) => (
              <li key={i} className="relative">
                <span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-brand" />
                <span className="font-medium">{e.event_type.replace(/_/g, " ")}</span>
                <span className="ml-2 text-xs text-slate-400">
                  {new Date(e.created_at).toLocaleString()}
                </span>
              </li>
            ))}
          </ol>
        </Section>
      </div>

      <div className="fixed bottom-16 left-1/2 z-20 flex w-full max-w-[480px] -translate-x-1/2 gap-2 border-t border-slate-200 bg-white p-3">
        <button
          disabled={busy}
          onClick={() => act({ affected_too: true })}
          className="flex-1 rounded-lg border border-brand py-2.5 text-sm font-semibold text-brand disabled:opacity-40"
        >
          I’m affected too
        </button>
        <button
          disabled={busy}
          onClick={() => act({ still_unresolved: true })}
          className="flex-1 rounded-lg bg-brand py-2.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          Still unresolved
        </button>
      </div>

      <Link href="/my-locality" className="block px-4 text-xs text-slate-400">
        ← Back to locality
      </Link>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</h2>
      {children}
    </section>
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
