"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";

export default function AuthorityDashboardPage() {
  const [issues, setIssues] = useState<IssueSummary[]>([]);

  useEffect(() => {
    api.authorityQueue({ sort: "urgency" }).then(setIssues).catch(() => setIssues([]));
  }, []);

  const open = issues.filter((i) => !["resolved", "rejected"].includes(i.status));
  const urgent = issues.filter((i) => i.urgency_score >= 5);
  const reopened = issues.filter((i) => i.status === "reopened");

  return (
    <main className="dashboard-shell">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-brand">Authority Dashboard</h1>
        <Link href="/authority/issues" className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white">
          Open queue →
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Open issues" value={open.length} />
        <Stat label="Urgent (≥5)" value={urgent.length} />
        <Stat label="Reopened" value={reopened.length} />
        <Stat label="Total" value={issues.length} />
      </div>

      <h2 className="mb-2 mt-6 text-sm font-semibold text-slate-500">Top by urgency</h2>
      <div className="space-y-2">
        {issues.slice(0, 5).map((i) => (
          <Link
            key={i.id}
            href={`/authority/issues/${i.id}`}
            className="flex items-center justify-between rounded-lg border border-slate-200 p-3 text-sm hover:border-brand"
          >
            <span className="truncate">{i.title}</span>
            <span className="ml-3 shrink-0 font-semibold">🔥 {i.urgency_score.toFixed(1)}</span>
          </Link>
        ))}
      </div>
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
