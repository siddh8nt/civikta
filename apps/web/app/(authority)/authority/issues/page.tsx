"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { IssueSearchBar } from "@/components/IssueSearchBar";
import { AuthorityBanner } from "@/components/AuthorityBanner";
import { getAuthorityContext } from "@/lib/authority-context";

// Sub-departments within multi-department portals — lets an officer filter
// within their own portal only, never across into a different authority.
const PORTAL_DEPARTMENTS: Record<string, string[]> = {
  mcd: ["mcd_sanitation", "mcd_engineering", "mcd_horticulture", "mcd_public_health"],
  ndmc: ["ndmc_sanitation", "ndmc_civil", "ndmc_horticulture"],
};

export default function AuthorityQueuePage() {
  const [portal, setPortal] = useState<string | null>(null);
  const [department, setDepartment] = useState(""); // "" = all departments in this portal
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [sort, setSort] = useState("urgency");
  const [loading, setLoading] = useState(true);

  // Queue is always scoped to the portal the officer is logged into —
  // never a free choice across other authorities' queues.
  useEffect(() => {
    setPortal(getAuthorityContext()?.authority ?? "");
  }, []);

  useEffect(() => {
    if (portal === null) return; // still resolving portal context
    setLoading(true);
    api
      .authorityQueue({ authority: department || portal || undefined, sort })
      .then(setIssues)
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, [portal, department, sort]);

  const departments = PORTAL_DEPARTMENTS[portal ?? ""] ?? [];

  return (
    <>
    <AuthorityBanner />
    <main className="dashboard-shell">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-brand">Authority Issue Queue</h1>
          <p className="text-xs text-slate-400">Search or filter assigned issues</p>
        </div>
        <Link href="/authority/dashboard" className="text-sm text-slate-500">
          ← Dashboard
        </Link>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {departments.length > 0 && (
          <select
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">All departments</option>
            {departments.map((d) => (
              <option key={d} value={d}>{authorityLabel(d)}</option>
            ))}
          </select>
        )}
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="urgency">Sort: Urgency</option>
          <option value="corroboration">Sort: Corroboration</option>
          <option value="recent">Sort: Recent</option>
        </select>
      </div>

      {loading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="p-3">Issue</th>
                <th className="p-3">Locality</th>
                <th className="p-3">Authority</th>
                <th className="p-3">Status</th>
                <th className="p-3">Severity</th>
                <th className="p-3 text-right">Corrob.</th>
                <th className="p-3 text-right">Urgency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {issues.map((i) => (
                <tr key={i.id} className="hover:bg-slate-50">
                  <td className="p-3">
                    <Link href={`/authority/issues/${i.id}`} className="font-medium text-brand">
                      {i.title}
                    </Link>
                  </td>
                  <td className="p-3 text-slate-500">{i.locality_name}</td>
                  <td className="p-3 text-slate-500">{authorityLabel(i.primary_authority_slug)}</td>
                  <td className="p-3"><StatusBadge status={i.status} /></td>
                  <td className="p-3"><SeverityBadge severity={i.severity} /></td>
                  <td className="p-3 text-right">{i.corroboration_count}</td>
                  <td className="p-3 text-right font-semibold">{i.urgency_score.toFixed(1)}</td>
                </tr>
              ))}
              {issues.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-400">
                    No issues in this queue.
                  </td>
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
