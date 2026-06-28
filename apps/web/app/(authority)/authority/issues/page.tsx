"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { IssueSearchBar } from "@/components/IssueSearchBar";
import { AuthorityBanner } from "@/components/AuthorityBanner";

const AUTHORITIES = ["", "djb", "pwd", "mcd_sanitation", "mcd_engineering", "mcd_public_health",
  "mcd_horticulture", "ndmc_civil", "ndmc_sanitation", "ifcd", "dda", "delhi_police", "nhai", "dcb_civic"];

export default function AuthorityQueuePage() {
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [authority, setAuthority] = useState("");
  const [sort, setSort] = useState("urgency");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .authorityQueue({ authority: authority || undefined, sort })
      .then(setIssues)
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, [authority, sort]);

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
        <select
          value={authority}
          onChange={(e) => setAuthority(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          {AUTHORITIES.map((a) => (
            <option key={a} value={a}>
              {a === "" ? "All authorities" : authorityLabel(a)}
            </option>
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
