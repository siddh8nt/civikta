"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { IssueSearchBar } from "@/components/IssueSearchBar";
import { saveAuthorityContext, getAuthorityContext, AUTHORITY_META as SHARED_META, DEFAULT_META as SHARED_DEFAULT } from "@/lib/authority-context";

// Re-export with badge field for dashboard-specific use
type AuthMeta = {
  name: string;
  full: string;
  headerBg: string;
  headerText: string;
  accent: string;
  badge: string;
};

function toAuthMeta(slug: string): AuthMeta {
  const m = SHARED_META[slug] ?? SHARED_DEFAULT;
  const BADGES: Record<string, string> = {
    mcd: "bg-blue-100 text-blue-700", ndmc: "bg-indigo-100 text-indigo-700",
    dcb: "bg-slate-100 text-slate-600", djb: "bg-teal-100 text-teal-700",
    pwd: "bg-orange-100 text-orange-700", ifcd: "bg-cyan-100 text-cyan-700",
    dda: "bg-violet-100 text-violet-700", police: "bg-slate-100 text-slate-700",
    nhai: "bg-amber-100 text-amber-700",
  };
  return { ...m, headerText: "text-white", badge: BADGES[slug] ?? "bg-slate-100 text-slate-600" };
}



function DashboardContent() {
  const searchParams = useSearchParams();

  // URL params are authoritative; fall back to localStorage when missing (e.g. direct navigation)
  const [authority, setAuthority] = useState(searchParams.get("authority") ?? "");
  const [zone, setZone] = useState(searchParams.get("zone") ?? null);

  useEffect(() => {
    const urlAuthority = searchParams.get("authority") ?? "";
    const urlZone = searchParams.get("zone") ?? null;

    if (urlAuthority) {
      // URL has params — save and use them
      setAuthority(urlAuthority);
      setZone(urlZone);
      saveAuthorityContext({ authority: urlAuthority, zone: urlZone });
    } else {
      // No URL params — restore from localStorage
      const saved = getAuthorityContext();
      if (saved) {
        setAuthority(saved.authority);
        setZone(saved.zone);
      }
    }
  }, [searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  const meta = toAuthMeta(authority);

  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load all issues to debug if filtering is the issue
    api.authorityQueue({ sort: "urgency" })
      .then(setIssues)
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, []);

  const open     = issues.filter((i) => !["resolved", "rejected"].includes(i.status));
  const urgent   = issues.filter((i) => i.urgency_score >= 5);
  const reopened = issues.filter((i) => i.status === "reopened");

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Authority header bar */}
      <header className={`${meta.headerBg} ${meta.headerText}`}>
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/20 text-xs font-bold">CV</div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold tracking-wider">CIVIKTA</span>
                  <span className="rounded bg-white/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest">
                    {meta.name}
                  </span>
                  {zone && (
                    <span className="rounded bg-white/10 px-2 py-0.5 text-[10px] font-medium">
                      {zone} Zone
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-white/60 tracking-wide">{meta.full} · Issue Dashboard</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-56">
              <IssueSearchBar urlPrefix="/authority/issues" />
            </div>
            <Link
              href="/authority/portal"
              className="rounded-lg border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/80 hover:bg-white/20 transition"
            >
              Change Portal
            </Link>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-8">
        {/* Page title row */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Issue Dashboard</h1>
            <p className="text-sm text-slate-500">
              {zone ? `${meta.full} · ${zone} Zone` : meta.full}
            </p>
          </div>
          <Link
            href="/authority/issues"
            className={`rounded-lg ${meta.headerBg} px-4 py-2 text-sm font-semibold text-white hover:opacity-90 transition`}
          >
            Open queue →
          </Link>
        </div>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Open Issues"  value={loading ? "—" : String(open.length)} />
          <Stat label="Urgent (≥5)"  value={loading ? "—" : String(urgent.length)} />
          <Stat label="Reopened"     value={loading ? "—" : String(reopened.length)} />
          <Stat label="Total"        value={loading ? "—" : String(issues.length)} />
        </div>

        {/* Escalation notice */}
        <Link
          href="/authority/escalations"
          className="mb-4 flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm hover:bg-rose-100 transition"
        >
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-rose-500" />
            <span className="font-semibold text-rose-800">Citizen Escalations</span>
            <span className="text-xs text-rose-600">— deadline breaches &amp; disputed resolutions</span>
          </div>
          <span className="text-xs text-rose-500">View →</span>
        </Link>

        {/* Top urgent issues */}
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-slate-400">Top by urgency score</h2>
          {loading ? (
            <p className="py-8 text-center text-sm text-slate-400">Loading issue queue…</p>
          ) : issues.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">No issues assigned to this authority.</p>
          ) : (
            <div className="space-y-2">
              {issues.slice(0, 8).map((i) => (
                <Link
                  key={i.id}
                  href={`/authority/issues/${i.id}`}
                  className="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm hover:border-slate-300 hover:shadow-sm transition"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                      i.status === "in_progress" ? "bg-blue-100 text-blue-700" :
                      i.status === "submitted"   ? "bg-amber-100 text-amber-700" :
                      i.status === "reopened"    ? "bg-rose-100 text-rose-700" :
                      "bg-slate-100 text-slate-600"
                    }`}>
                      {i.status.replace("_", " ")}
                    </span>
                    <span className="truncate text-slate-800">{i.title}</span>
                  </div>
                  <span className="ml-4 shrink-0 font-bold text-slate-700">{i.urgency_score.toFixed(1)}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="text-3xl font-extrabold text-slate-900">{value}</div>
      <div className="mt-0.5 text-xs text-slate-500">{label}</div>
    </div>
  );
}

export default function AuthorityDashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-slate-50">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-slate-200 border-t-slate-700" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
