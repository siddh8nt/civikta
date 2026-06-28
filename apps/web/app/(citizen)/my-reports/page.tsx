"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueDetail } from "@/lib/types";
import { IssueCard } from "@/components/IssueCard";

type Report = {
  id: string;
  created_at: string;
  raw_description: string | null;
  merged_into_issue_id: string | null;
};

export default function MyReportsPage() {
  const [issues, setIssues] = useState<IssueDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.myReports()
      .then(async (data) => {
        const reports = data as Report[];

        // Collect unique issue IDs from submitted reports
        const issueIds = [...new Set(
          reports
            .map((r) => r.merged_into_issue_id)
            .filter((id): id is string => !!id)
        )];

        // Fetch all issues in parallel
        const fetched = await Promise.all(
          issueIds.map((id) => api.issue(id).catch(() => null))
        );

        const valid = fetched.filter((i): i is IssueDetail => i !== null);
        // Sort newest first
        valid.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setIssues(valid);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 pb-24" style={{ maxWidth: 480, margin: "0 auto" }}>
      <div className="sticky top-0 z-10 bg-white border-b border-slate-100 px-4 py-3">
        <h1 className="text-base font-bold text-slate-900">My Reports</h1>
        <p className="text-[11px] text-slate-400">Issues you've raised</p>
      </div>

      {loading && (
        <div className="flex flex-col gap-3 p-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="px-4 pt-12 text-center">
          <p className="text-sm text-rose-500">Couldn't load your reports. Check your connection.</p>
        </div>
      )}

      {!loading && !error && issues.length === 0 && (
        <div className="flex flex-col items-center justify-center px-6 pt-24 text-center gap-3">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-3xl">📋</div>
          <p className="text-sm font-semibold text-slate-700">No reports yet</p>
          <p className="text-xs text-slate-400">Issues you raise will appear here</p>
          <Link
            href="/raise"
            className="mt-2 rounded-2xl bg-brand px-6 py-3 text-sm font-bold text-white active:scale-95 transition-transform"
          >
            Raise an issue →
          </Link>
        </div>
      )}

      {!loading && !error && issues.length > 0 && (
        <div className="flex flex-col gap-3 p-4">
          {issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}
    </main>
  );
}
