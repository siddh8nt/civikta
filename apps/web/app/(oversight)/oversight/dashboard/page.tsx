"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { OversightAlert } from "@/lib/types";
import { IssueSearchBar } from "@/components/IssueSearchBar";

// ── helpers ──────────────────────────────────────────────────────────────────
const SEV_STYLE: Record<string, string> = {
  watch:    "border-yellow-200 bg-yellow-50 text-yellow-900",
  alert:    "border-orange-200 bg-orange-50 text-orange-900",
  critical: "border-red-200 bg-red-50 text-red-900",
};
const SEV_DOT: Record<string, string> = {
  watch: "bg-yellow-400", alert: "bg-orange-400", critical: "bg-red-500",
};

const CAT_LABEL: Record<string, string> = {
  roads_streets: "Roads", water_sewer_drainage: "Water/Drain",
  garbage_sanitation: "Sanitation", lights_electrical: "Electrical",
  parks_public_space: "Parks", public_safety_hazard: "Safety", animals_other: "Other",
};
const SEV_LABEL: Record<string, string> = {
  low: "Low", medium: "Medium", high: "High", critical: "Critical",
};
const SEV_PILL: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  high:     "bg-orange-100 text-orange-700",
  medium:   "bg-yellow-100 text-yellow-700",
  low:      "bg-slate-100 text-slate-600",
};

function catLabel(s: string | null) { return CAT_LABEL[s ?? ""] ?? s ?? "—"; }
function sevLabel(s: string)        { return SEV_LABEL[s]         ?? s; }

// ── skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-slate-200 ${className ?? ""}`} />;
}

// ── stat card ─────────────────────────────────────────────────────────────────
function StatCard({
  label, value, sub, accent,
}: { label: string; value: number | string | null; sub?: string; accent?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {value === null
        ? <Skeleton className="mb-1 h-8 w-16" />
        : <div className={`text-2xl font-bold ${accent ?? "text-violet-700"}`}>{value}</div>}
      <div className="text-xs font-medium text-slate-500">{label}</div>
      {sub && <div className="mt-0.5 text-xs text-slate-400">{sub}</div>}
    </div>
  );
}

// ── types ─────────────────────────────────────────────────────────────────────
type Summary = {
  total_issues: number;
  open_issues: number;
  resolved_issues: number;
  unresolved_over_7d: number;
  reopened_issues: number;
  sla_breached_open: number;
  sla_breach_rate_pct: number;
  false_closures: number;
  safety_flagged_open: number;
  total_corroborations: number;
  open_by_severity: Record<string, number>;
  open_by_category: Record<string, number>;
  authority_table: { slug: string; name: string; open: number; total: number; sla_breached: number; sla_breach_rate_pct: number }[];
  most_corroborated: { id: string; title: string; corroboration_count: number; urgency_score: number; ward: string; authority: string; severity: string; days_open: number }[];
};

// ── page ─────────────────────────────────────────────────────────────────────
export default function OversightDashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [alerts, setAlerts]   = useState<OversightAlert[] | null>(null);
  const [alertsLoading, setAlertsLoading] = useState(true);

  useEffect(() => {
    // Fire both requests in parallel — don't let one block the other
    api.oversightSummary()
      .then((s) => setSummary(s as unknown as Summary))
      .catch(() => setSummary(null));

    api.oversightAlerts()
      .then((a) => setAlerts(a))
      .catch(() => setAlerts([]))
      .finally(() => setAlertsLoading(false));
  }, []);

  const s = summary;

  return (
    <main className="dashboard-shell space-y-6">
      {/* ── header ── */}
      <div className="flex items-center justify-between">
        <div>
          <Link href="/" className="mb-1 inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition-colors">
            ← Delhi Civic Portal
          </Link>
          <h1 className="text-xl font-bold text-slate-800">Oversight Dashboard</h1>
          <p className="text-xs text-slate-400 mt-0.5">State-wide civic accountability · NCT Delhi</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="w-56">
            <IssueSearchBar urlPrefix="/oversight/issues" />
          </div>
          <Link
            href="/oversight/escalations"
            className="rounded-lg bg-rose-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-rose-700 transition-colors"
          >
            🚨 Escalations
          </Link>
          <Link
            href="/oversight/analytics"
            className="rounded-lg bg-violet-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-violet-700 transition-colors"
          >
            Analytics Agent
          </Link>
          <Link href="/oversight/issues" className="text-sm text-slate-500 hover:text-slate-700">All issues →</Link>
          <Link href="/oversight/hotspots" className="text-sm text-slate-500 hover:text-slate-700">Hotspots →</Link>
        </div>
      </div>

      {/* ── primary stats ── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total issues"    value={s?.total_issues    ?? null} />
        <StatCard label="Open"            value={s?.open_issues     ?? null} accent="text-orange-600" />
        <StatCard label="SLA breached"    value={s?.sla_breached_open ?? null} accent="text-red-600"
          sub={s ? `${s.sla_breach_rate_pct}% of open` : undefined} />
        <StatCard label="Corroborations"  value={s?.total_corroborations ?? null} accent="text-violet-700" />
      </div>

      {/* ── secondary stats ── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Resolved"          value={s?.resolved_issues   ?? null} accent="text-green-600" />
        <StatCard label="Unresolved >7d"    value={s?.unresolved_over_7d ?? null} accent="text-orange-500" />
        <StatCard label="False closures"    value={s?.false_closures    ?? null} accent="text-red-500"
          sub="Resolutions disputed" />
        <StatCard label="Safety-flagged open" value={s?.safety_flagged_open ?? null} accent="text-red-700"
          sub="Health / public safety" />
      </div>

      {/* ── main content: alerts + most corroborated ── */}
      <div className="grid gap-4 lg:grid-cols-2">

        {/* AI Anomaly Alerts */}
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-700">⚡ AI Anomaly Alerts</span>
            <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs text-violet-700">proactive</span>
          </div>

          {alertsLoading ? (
            <div className="space-y-2">
              {[1,2,3].map(i => <Skeleton key={i} className="h-16 w-full" />)}
            </div>
          ) : !alerts || alerts.length === 0 ? (
            <p className="text-sm text-slate-400">No anomalies detected.</p>
          ) : (
            <div className="space-y-2">
              {alerts.map((a, i) => (
                <div key={i} className={`rounded-lg border p-3 text-sm ${SEV_STYLE[a.severity]}`}>
                  <div className="flex items-start gap-2">
                    <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${SEV_DOT[a.severity]}`} />
                    <div className="min-w-0">
                      <p className="font-medium leading-snug">{a.headline}</p>
                      <p className="mt-1 text-xs opacity-70">
                        {a.ward_name} · {catLabel(a.category_slug)} · {a.metrics.total_corroborations} corroborations · {a.metrics.oldest_unresolved_days}d oldest
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Most corroborated open issues */}
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 text-sm font-semibold text-slate-700">🔥 Most corroborated open</div>
          {!s ? (
            <div className="space-y-2">{[1,2,3,4,5].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>
          ) : s.most_corroborated.length === 0 ? (
            <p className="text-sm text-slate-400">No open issues.</p>
          ) : (
            <div className="space-y-2">
              {s.most_corroborated.map((m) => (
                <Link
                  key={m.id}
                  href={`/oversight/issues/${m.id}`}
                  className="flex items-start justify-between rounded-lg border border-slate-100 p-2.5 text-sm hover:border-violet-200 hover:bg-violet-50 transition-colors"
                >
                  <div className="min-w-0 pr-2">
                    <p className="truncate font-medium text-slate-700">{m.title}</p>
                    <p className="mt-0.5 text-xs text-slate-400">{m.ward} · {m.authority}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="text-xs font-semibold text-violet-700">✓ {m.corroboration_count}</div>
                    <div className={`mt-0.5 rounded px-1 py-0.5 text-xs ${SEV_PILL[m.severity] ?? ""}`}>
                      {sevLabel(m.severity)}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── authority table ── */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="mb-3 text-sm font-semibold text-slate-700">Authority workload</div>
        {!s ? (
          <div className="space-y-2">{[1,2,3,4,5].map(i => <Skeleton key={i} className="h-8 w-full" />)}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs text-slate-400">
                  <th className="pb-2 text-left font-medium">Authority</th>
                  <th className="pb-2 text-right font-medium">Open</th>
                  <th className="pb-2 text-right font-medium">Total</th>
                  <th className="pb-2 text-right font-medium">SLA breached</th>
                  <th className="pb-2 text-right font-medium">Breach rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {s.authority_table.slice(0, 10).map((auth) => (
                  <tr key={auth.slug} className="hover:bg-slate-50">
                    <td className="py-2 font-medium text-slate-700">{auth.name}</td>
                    <td className="py-2 text-right text-orange-600 font-semibold">{auth.open}</td>
                    <td className="py-2 text-right text-slate-500">{auth.total}</td>
                    <td className="py-2 text-right text-red-500">{auth.sla_breached}</td>
                    <td className="py-2 text-right">
                      <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        auth.sla_breach_rate_pct >= 70 ? "bg-red-100 text-red-700"
                        : auth.sla_breach_rate_pct >= 40 ? "bg-orange-100 text-orange-700"
                        : "bg-green-100 text-green-700"
                      }`}>
                        {auth.sla_breach_rate_pct}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── category + severity breakdown ── */}
      {s && (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 text-sm font-semibold text-slate-700">Open by category</div>
            <div className="space-y-1.5">
              {Object.entries(s.open_by_category).slice(0, 6).map(([cat, count]) => {
                const max = Math.max(...Object.values(s.open_by_category));
                return (
                  <div key={cat} className="flex items-center gap-2 text-xs">
                    <span className="w-28 shrink-0 text-slate-500 truncate">{catLabel(cat)}</span>
                    <div className="flex-1 rounded-full bg-slate-100 h-1.5">
                      <div
                        className="h-1.5 rounded-full bg-violet-500"
                        style={{ width: `${(count / max) * 100}%` }}
                      />
                    </div>
                    <span className="w-6 text-right font-medium text-slate-700">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-3 text-sm font-semibold text-slate-700">Open by severity</div>
            <div className="space-y-1.5">
              {(["critical","high","medium","low"] as const).map((sev) => {
                const count = s.open_by_severity[sev] ?? 0;
                const max = Math.max(...Object.values(s.open_by_severity));
                return (
                  <div key={sev} className="flex items-center gap-2 text-xs">
                    <span className="w-14 shrink-0 text-slate-500 capitalize">{sev}</span>
                    <div className="flex-1 rounded-full bg-slate-100 h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          sev === "critical" ? "bg-red-500"
                          : sev === "high"   ? "bg-orange-400"
                          : sev === "medium" ? "bg-yellow-400"
                          : "bg-slate-300"
                        }`}
                        style={{ width: max ? `${(count / max) * 100}%` : "0%" }}
                      />
                    </div>
                    <span className="w-6 text-right font-medium text-slate-700">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
