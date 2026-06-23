"use client";

import { useEffect, useState } from "react";

// Demo: my-reports lists the current demo user's submissions. The backend
// endpoint is /api/reports/mine; seeded demo issues belong to seed users, so a
// fresh demo citizen sees only what they submit in this session.
export default function MyReportsPage() {
  const [reports, setReports] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    fetch(`${base}/api/reports/mine`, {
      headers: { "X-Demo-User": "demo-citizen", "X-Demo-Role": "citizen" },
      cache: "no-store",
    })
      .then((r) => r.json())
      .then(setReports)
      .catch(() => setReports([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="p-4">
      <h1 className="mb-4 text-lg font-bold text-brand">My Reports</h1>
      {loading && <p className="text-sm text-slate-400">Loading…</p>}
      {!loading && reports.length === 0 && (
        <p className="py-10 text-center text-sm text-slate-400">
          You haven’t raised any issues yet.
        </p>
      )}
      <div className="space-y-2">
        {reports.map((r) => (
          <div key={String(r.id)} className="rounded-lg border border-slate-200 p-3 text-sm">
            <p className="font-medium">{String(r.raw_description ?? "Report")}</p>
            <p className="mt-1 text-xs text-slate-500">
              {String(r.issue_type_slug ?? "pending")} · {String(r.merge_decision ?? "—")}
            </p>
          </div>
        ))}
      </div>
    </main>
  );
}
