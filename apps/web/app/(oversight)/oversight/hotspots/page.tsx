"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { OversightBanner } from "@/components/OversightBanner";

export default function HotspotsPage() {
  const [hotspots, setHotspots] = useState<Record<string, any>[]>([]);

  useEffect(() => {
    api.oversightHotspots().then((h) => setHotspots(h as Record<string, any>[])).catch(() => {});
  }, []);

  return (
    <>
    <OversightBanner />
    <main className="dashboard-shell pt-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Hotspots</h1>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="p-3">Ward</th>
              <th className="p-3">Locality</th>
              <th className="p-3 text-right">Open issues</th>
              <th className="p-3 text-right">Corroborations</th>
              <th className="p-3 text-right">Max urgency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {hotspots.map((h, i) => (
              <tr key={i} className="hover:bg-slate-50">
                <td className="p-3">{h.ward_name ?? "—"}</td>
                <td className="p-3 text-slate-500">{h.locality_name ?? "—"}</td>
                <td className="p-3 text-right font-semibold">{h.open_count}</td>
                <td className="p-3 text-right">{h.total_corroborations}</td>
                <td className="p-3 text-right">{Number(h.max_urgency).toFixed(1)}</td>
              </tr>
            ))}
            {hotspots.length === 0 && (
              <tr>
                <td colSpan={5} className="p-6 text-center text-slate-400">No hotspots.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
    </>
  );
}
