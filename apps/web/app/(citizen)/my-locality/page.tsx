"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { IssueCard } from "@/components/IssueCard";
import { MapPlaceholder } from "@/components/MapPlaceholder";
import { getUserLocation } from "@/lib/user";

// default center: Lajpat Nagar (matches seeded demo data)
const FALLBACK = { lat: 28.5677, lng: 77.2433 };

function distKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const TEST_MODE = false;

const FILTERS = [
  { slug: null, label: "All" },
  { slug: "roads_streets", label: "Roads" },
  { slug: "water_sewer_drainage", label: "Water" },
  { slug: "garbage_sanitation", label: "Garbage" },
  { slug: "lights_electrical", label: "Lights" },
  { slug: "parks_public_space", label: "Parks" },
];

export default function MyLocalityPage() {
  return (
    <Suspense>
      <MyLocalityInner />
    </Suspense>
  );
}

function MyLocalityInner() {
  const searchParams = useSearchParams();
  const [view, setView] = useState<"feed" | "map">("feed");
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [filter, setFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Priority: URL params (from onboarding) → saved location → GPS → fallback
    const urlLat = searchParams.get("lat");
    const urlLng = searchParams.get("lng");
    const saved = getUserLocation();

    const load = (c: { lat: number; lng: number }) =>
      api
        .feedNearby(c.lat, c.lng, 8000)
        .then((issues) => {
          const sorted = [...issues].sort((a, b) => {
            const da = (a.latitude != null && a.longitude != null) ? distKm(c.lat, c.lng, a.latitude, a.longitude) : Infinity;
            const db = (b.latitude != null && b.longitude != null) ? distKm(c.lat, c.lng, b.latitude, b.longitude) : Infinity;
            return da - db;
          });
          setIssues(sorted);
        })
        .catch((e) => setError(String(e)))
        .finally(() => setLoading(false));

    if (urlLat && urlLng) {
      load({ lat: parseFloat(urlLat), lng: parseFloat(urlLng) });
    } else if (saved) {
      load({ lat: saved.lat, lng: saved.lng });
    } else if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => load({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => load(FALLBACK),
        { timeout: 4000 },
      );
    } else {
      load(FALLBACK);
    }
  }, [searchParams]);

  const visible = TEST_MODE ? issues.filter((i) => i.ward_name === "__TEST__") : issues;
  const shown = filter ? visible.filter((i) => i.issue_category_slug === filter) : visible;

  return (
    <main>
      <header className="sticky top-10 z-10 border-b border-slate-200 bg-white/95 px-4 pb-2 pt-4 backdrop-blur">
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
          <div className="py-10 text-center">
            <p className="text-sm text-rose-500 mb-1">Couldn’t reach the API.</p>
            <p className="text-xs text-slate-400 break-all px-4">{error}</p>
          </div>
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

