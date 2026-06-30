"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { IssueSummary } from "@/lib/types";
import { IssueCard } from "@/components/IssueCard";
import { MapPlaceholder } from "@/components/MapPlaceholder";
import { getUserLocation, saveUserLocation, type UserLocation } from "@/lib/user";

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

function IssueCardSkeleton() {
  return (
    <div className="flex gap-2.5 overflow-hidden rounded-xl border border-slate-200 bg-paper p-2 animate-pulse">
      <div className="h-16 w-16 shrink-0 rounded-lg bg-slate-200" />
      <div className="min-w-0 flex-1 space-y-1.5 py-0.5">
        <div className="flex gap-1">
          <div className="h-4 w-14 rounded-full bg-slate-200" />
          <div className="h-4 w-12 rounded-full bg-slate-200" />
        </div>
        <div className="h-4 w-3/4 rounded bg-slate-200" />
        <div className="h-3 w-1/2 rounded bg-slate-200" />
        <div className="h-3 w-2/5 rounded bg-slate-200" />
      </div>
    </div>
  );
}

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

  // Fade + rise in on mount, so arriving here from sign-in (or anywhere
  // else) reads as a continuous transition rather than a hard pop-in.
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  // Account's saved ward, for the Swiggy/Zomato-style "reporting in" strip.
  const [myLocation, setMyLocation] = useState<UserLocation | null>(null);
  useEffect(() => {
    setMyLocation(getUserLocation());
  }, []);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const urlLat = searchParams.get("lat");
    const urlLng = searchParams.get("lng");

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

    function fromCacheOrGps() {
      const saved = getUserLocation();
      if (saved) {
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
    }

    async function resolveLocation() {
      // 1. Explicit coords from just-completed onboarding always win.
      if (urlLat && urlLng) {
        load({ lat: parseFloat(urlLat), lng: parseFloat(urlLng) });
        return;
      }

      // 2. If signed in, the backend record for THIS account is the only
      // authoritative source — `civikta_location` in localStorage is a
      // single device-wide key, so it may belong to a different account
      // that previously used this browser. Never trust it over the
      // authenticated account's own saved location.
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          const me = await api.getMe();
          if (me.home_lat != null && me.home_lng != null) {
            saveUserLocation({
              lat: me.home_lat,
              lng: me.home_lng,
              ward_no: me.ward_no ?? null,
              ward_name: me.ward_name ?? null,
              zone: me.zone ?? null,
              local_body_type: me.local_body_type ?? null,
            });
            setMyLocation(getUserLocation());
            load({ lat: me.home_lat, lng: me.home_lng });
            return;
          }
        }
      } catch {
        // not signed in, or lookup failed — fall through to cache/GPS
      }

      // 3. Guest/demo usage (no session) — cached location, then GPS.
      fromCacheOrGps();
    }

    resolveLocation();
  }, [searchParams]);

  const visible = TEST_MODE ? issues.filter((i) => i.ward_name === "__TEST__") : issues;
  const shown = filter ? visible.filter((i) => i.issue_category_slug === filter) : visible;

  return (
    <main
      className={`transition-all duration-300 ease-out ${
        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
      }`}
    >
      <header className="sticky top-10 z-10 border-b border-slate-200 bg-paper px-4 pb-2 pt-4 shadow-sm">
        <div className="mb-1 flex items-center justify-between gap-2">
          {myLocation && (myLocation.ward_name || myLocation.zone) ? (
            <div className="flex min-w-0 items-center gap-1 text-[11px] font-semibold text-slate-500">
              <svg viewBox="0 0 24 24" fill="none" className="h-3 w-3 shrink-0 text-brand" stroke="currentColor" strokeWidth={2.2}>
                <path d="M12 21s7-7.5 7-12a7 7 0 10-14 0c0 4.5 7 12 7 12z" strokeLinejoin="round" />
                <circle cx="12" cy="9" r="2.2" />
              </svg>
              <span className="truncate">
                <span className="text-slate-600">{myLocation.ward_name ?? "your area"}</span>
                {myLocation.zone && ` · ${myLocation.zone}`}
              </span>
            </div>
          ) : (
            <span />
          )}
          <div className="flex shrink-0 rounded-lg bg-slate-100 p-0.5 text-xs font-medium">
            {(["feed", "map"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-md px-3 py-1 capitalize ${
                  view === v ? "bg-paper text-brand shadow-sm" : "text-slate-500"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
        <h1 className="text-lg font-bold text-brand">My Locality</h1>
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
        {loading && (
          <div className="space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <IssueCardSkeleton key={i} />
            ))}
          </div>
        )}
        {error && (
          <div className="py-10 text-center">
            <p className="text-sm text-rose-500 mb-1">Couldn’t reach the API.</p>
            <p className="text-xs text-slate-400 break-all px-4">{error}</p>
          </div>
        )}
        {!loading && !error && view === "map" && <MapPlaceholder issues={shown} />}
        {!loading && !error && view === "feed" && (
          <div className="space-y-2">
            {shown.length === 0 && (
              <p className="py-10 text-center text-sm text-slate-400">No issues match this filter.</p>
            )}
            {shown.map((i) => (
              <IssueCard key={i.id} issue={i} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

