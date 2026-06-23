"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { OversightAlert } from "@/lib/types";

const SEV_STYLE: Record<string, string> = {
  watch: "border-yellow-300 bg-yellow-50 text-yellow-900",
  alert: "border-orange-300 bg-orange-50 text-orange-900",
  critical: "border-red-300 bg-red-50 text-red-900",
};

export default function OversightDashboardPage() {
  const [summary, setSummary] = useState<Record<string, any> | null>(null);
  const [alerts, setAlerts] = useState<OversightAlert[]>([]);

  useEffect(() => {
    api.oversightSummary().then((s) => setSummary(s as Record<string, any>)).catch(() => {});
    api.oversightAlerts().then(setAlerts).catch(() => {});
  }, []);

  return (
    <main className="dashboard-shell">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-brand">Oversight Cockpit</h1>
        <Link href="/oversight/hotspots" className="text-sm text-slate-500">
          Hotspots →
        </Link>
      </div>

      {summary && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Total issues" value={summary.total_issues} />
          <Stat label="Open" value={summary.open_issues} />
          <Stat label="Unresolved >7d" value={summary.unresolved_over_7d} />
          <Stat label="Reopened" value={summary.reopened_issues} />
        </div>
      )}

      {/* Predictive / proactive AI alerts (PRD §10.4) */}
      <h2 className="mb-2 mt-6 flex items-center gap-2 text-sm font-semibold text-slate-600">
        ⚡ AI Anomaly Alerts
        <span className="rounded-full bg-brand/10 px-2 py-0.5 text-xs text-brand">proactive</span>
      </h2>
      <div className="space-y-2">
        {alerts.length === 0 && <p className="text-sm text-slate-400">No anomalies detected.</p>}
        {alerts.map((a, i) => (
          <div key={i} className={`rounded-xl border p-3 text-sm ${SEV_STYLE[a.severity]}`}>
            <div className="flex items-center justify-between">
              <span className="font-semibold uppercase">{a.severity}</span>
              <span className="text-xs">
                Ward {a.ward_name} · {a.category_slug}
              </span>
            </div>
            <p className="mt-1">{a.headline}</p>
            <p className="mt-1 text-xs opacity-70">
              {a.metrics.total_corroborations} corroborations · {a.metrics.open_count} open ·
              oldest {a.metrics.oldest_unresolved_days}d
            </p>
          </div>
        ))}
      </div>

      {summary?.most_corroborated && (
        <>
          <h2 className="mb-2 mt-6 text-sm font-semibold text-slate-600">Most corroborated open issues</h2>
          <div className="space-y-2">
            {summary.most_corroborated.map((m: any) => (
              <div
                key={m.id}
                className="flex items-center justify-between rounded-lg border border-slate-200 p-3 text-sm"
              >
                <span className="truncate">{m.title}</span>
                <span className="ml-3 shrink-0 text-slate-500">
                  ✓ {m.corroboration_count} · 🔥 {Number(m.urgency_score).toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="text-2xl font-bold text-brand">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}
