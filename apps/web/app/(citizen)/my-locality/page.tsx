"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { IssueCard } from "@/components/IssueCard";
import { MapPlaceholder } from "@/components/MapPlaceholder";

// default center: Lajpat Nagar (matches seeded demo data)
const DEFAULT = { lat: 28.5677, lng: 77.2433 };

const FILTERS = [
  { slug: null, label: "All" },
  { slug: "roads_streets", label: "Roads" },
  { slug: "water_sewer_drainage", label: "Water" },
  { slug: "garbage_sanitation", label: "Garbage" },
  { slug: "lights_electrical", label: "Lights" },
  { slug: "parks_public_space", label: "Parks" },
];

export default function MyLocalityPage() {
  const [view, setView] = useState<"feed" | "map">("feed");
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [filter, setFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let center = DEFAULT;
    const load = (c: { lat: number; lng: number }) =>
      api
        .feedNearby(c.lat, c.lng, 8000)
        .then(setIssues)
        .catch((e) => setError(String(e)))
        .finally(() => setLoading(false));

    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => load({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => load(center),
        { timeout: 4000 },
      );
    } else {
      load(center);
    }
  }, []);

  const shown = filter ? issues.filter((i) => i.issue_category_slug === filter) : issues;

  return (
    <main>
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-4 pb-2 pt-4 backdrop-blur">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-bold text-brand">My Locality</h1>
          <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs font-medium">
            {(["feed", "map"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-md px-3 py-1 capitalize ${
                  view === v ? "bg-white text-brand shadow-sm" : "text-slate-500"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-2 flex gap-1.5 overflow-x-auto pb-1">
          {FILTERS.map((f) => (
            <button
              key={f.label}
              onClick={() => setFilter(f.slug)}
              className={`whitespace-nowrap rounded-full border px-3 py-1 text-xs ${
                filter === f.slug
                  ? "border-brand bg-brand text-white"
                  : "border-slate-200 text-slate-600"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </header>

      <div className="p-4">
        {loading && <p className="py-10 text-center text-sm text-slate-400">Loading nearby issues…</p>}
        {error && (
          <p className="py-10 text-center text-sm text-rose-500">
            Couldn’t reach the API. Is the backend running on :8000?
          </p>
        )}
        {!loading && !error && view === "map" && <MapPlaceholder issues={shown} />}
        {!loading && !error && view === "feed" && (
          <div className="space-y-3">
            {shown.length === 0 && (
              <p className="py-10 text-center text-sm text-slate-400">No issues match this filter.</p>
            )}
            {shown.map((i) => (
              <IssueCard key={i.id} issue={i} />
            ))}
          </div>
        )}
      </div>

      <Link
        href="/raise"
        className="fixed bottom-20 left-1/2 z-20 -translate-x-1/2 rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white shadow-lg"
      >
        ➕ Raise an issue
      </Link>
    </main>
  );
}
