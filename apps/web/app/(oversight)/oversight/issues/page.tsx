"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { OversightBanner } from "@/components/OversightBanner";

const STATUSES = ["", "submitted", "assigned", "in_progress", "pending_verification", "resolved", "reopened", "rejected"];
const SEVERITIES = ["", "critical", "high", "medium", "low"];

export default function OversightIssueQueuePage() {
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const [sort, setSort] = useState("urgency");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.authorityQueue({ status: status || undefined, severity: severity || undefined, sort })
      .then(setIssues)
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, [status, severity, sort]);

  const reopenedCount = issues.filter((i) => i.status === "reopened").length;

  return (
    <>
    <OversightBanner />
    <main className="dashboard-shell pt-6">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-slate-900">All Issues</h1>
        {reopenedCount > 0 && (
          <p className="flex items-center gap-1 text-xs text-rose-700 font-medium mt-0.5">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376C1.83 17.815 2.91 19.5 4.5 19.5h15c1.59 0 2.67-1.685 1.803-3.374L13.803 5.126c-.795-1.541-2.811-1.541-3.606 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            {reopenedCount} escalated / reopened
          </p>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s === "" ? "All statuses" : s.replace(/_/g, " ")}</option>
          ))}
        </select>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>{s === "" ? "All severities" : s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="urgency">Sort: Urgency</option>
          <option value="corroboration">Sort: Corroboration</option>
          <option value="recent">Sort: Recent</option>
        </select>
        {(status || severity) && (
          <button
            onClick={() => { setStatus(""); setSeverity(""); }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-500 hover:bg-slate-50"
          >
            Clear filters ×
          </button>
        )}
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Issue</th>
                <th className="p-3">Ward</th>
                <th className="p-3">Authority</th>
                <th className="p-3">Status</th>
                <th className="p-3">Severity</th>
                <th className="p-3 text-right">Corrob.</th>
                <th className="p-3 text-right">Urgency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {issues.map((i) => (
                <tr
                  key={i.id}
                  className={`hover:bg-slate-50 ${i.status === "reopened" ? "bg-rose-50" : ""}`}
                >
                  <td className="p-3">
                    <Link href={`/oversight/issues/${i.id}`} className="font-medium text-indigo-800 hover:underline">
                      {i.title}
                    </Link>
                  </td>
                  <td className="p-3 text-slate-500">{i.ward_name ?? "—"}</td>
                  <td className="p-3 text-slate-500">{authorityLabel(i.primary_authority_slug)}</td>
                  <td className="p-3"><StatusBadge status={i.status} /></td>
                  <td className="p-3"><SeverityBadge severity={i.severity} /></td>
                  <td className="p-3 text-right">{i.corroboration_count}</td>
                  <td className="p-3 text-right font-semibold">{i.urgency_score.toFixed(1)}</td>
                </tr>
              ))}
              {issues.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-400">No issues found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </main>
    </>
  );
}
