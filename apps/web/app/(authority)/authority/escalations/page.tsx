"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { getAuthorityContext, getAuthorityMeta } from "@/lib/authority-context";
import { AuthorityBanner } from "@/components/AuthorityBanner";

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

const AUTHORITY_SLUGS: Record<string, string[]> = {
  mcd:    ["mcd_sanitation", "mcd_engineering", "mcd_horticulture", "mcd_public_health"],
  ndmc:   ["ndmc_civil", "ndmc_sanitation", "ndmc_horticulture"],
  dcb:    ["dcb_civic"],
  djb:    ["djb"],
  pwd:    ["pwd"],
  ifcd:   ["ifcd"],
  dda:    ["dda"],
  police: ["delhi_police"],
  nhai:   ["nhai"],
};

type Tab = "undealt" | "disputed";

export default function AuthorityEscalationsPage() {
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("undealt");
  const [ctx, setCtx] = useState<{ authority: string; zone: string | null } | null>(null);

  useEffect(() => {
    const saved = getAuthorityContext();
    setCtx(saved);

    api.authorityEscalations()
      .then((all) => {
        if (!saved) { setIssues(all); return; }
        const slugs = AUTHORITY_SLUGS[saved.authority] ?? [saved.authority];
        setIssues(all.filter((i) => i.primary_authority_slug != null && slugs.includes(i.primary_authority_slug)));
      })
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, []);

  const meta = getAuthorityMeta(ctx?.authority ?? "");

  const undealt  = issues.filter((i) => i.status === "submitted");
  const disputed = issues.filter((i) => i.status === "resolved");
  const shown    = tab === "undealt" ? undealt : disputed;

  const dashParams = new URLSearchParams({ authority: ctx?.authority ?? "" });
  if (ctx?.zone) dashParams.set("zone", ctx.zone);

  return (
    <>
      <AuthorityBanner />
      <main className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Citizen Escalations</h1>
            <p className="text-sm text-slate-500">
              {ctx ? `${meta.full}${ctx.zone ? ` · ${ctx.zone} Zone` : ""}` : "Your department"} · Issues flagged for urgent attention
            </p>
          </div>
          <Link
            href={`/authority/dashboard?${dashParams.toString()}`}
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            ← Dashboard
          </Link>
        </div>

        {/* Tabs */}
        <div className="mb-5 flex gap-1 rounded-xl border border-slate-200 bg-slate-100 p-1">
          {(["undealt", "disputed"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 rounded-lg py-2 text-sm font-semibold transition ${
                tab === t
                  ? "bg-white shadow text-slate-900"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {t === "undealt"
                ? `Undealt Issues (${undealt.length})`
                : `Disputed Resolutions (${disputed.length})`}
            </button>
          ))}
        </div>

        <p className="mb-4 text-xs text-slate-400">
          {tab === "undealt"
            ? "Issues submitted more than 1 hour ago with no authority action."
            : "Resolved issues with ≥100 citizen corroborations — likely still unresolved."}
        </p>

        {loading ? (
          <p className="py-10 text-center text-sm text-slate-400">Loading escalations…</p>
        ) : shown.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-200 py-12 text-center text-sm text-slate-400">
            No {tab === "undealt" ? "undealt" : "disputed"} escalations for your department.
          </div>
        ) : (
          <div className="space-y-3">
            {shown.map((i) => (
              <Link
                key={i.id}
                href={`/authority/issues/${i.id}`}
                className="flex items-start justify-between rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm hover:border-rose-300 hover:shadow transition"
              >
                <div className="min-w-0 flex-1">
                  <div className="mb-1 flex flex-wrap items-center gap-2">
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                      tab === "undealt"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-rose-100 text-rose-700"
                    }`}>
                      {tab === "undealt" ? "Undealt" : "Disputed"}
                    </span>
                    <span className="truncate font-medium text-slate-800">{i.title}</span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {[i.locality_name, i.ward_name].filter(Boolean).join(" · ") || "Location unknown"}
                  </p>
                </div>
                <div className="ml-4 shrink-0 text-right">
                  <p className="text-xs text-slate-400">{timeAgo(i.created_at)}</p>
                  <p className="text-xs font-semibold text-slate-600">{i.urgency_score.toFixed(1)} urgency</p>
                  {tab === "undealt" && (
                    <p className="text-[10px] text-rose-500">Action overdue</p>
                  )}
                  {tab === "disputed" && (
                    <p className="text-[10px] text-rose-500">{i.corroboration_count} corroborations</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
