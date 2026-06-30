"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LocationStep } from "@/components/LocationStep";
import { api } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { getProfile, saveUserLocation, markOnboardingComplete, getUserId } from "@/lib/user";

type LatLng = { lat: number; lng: number };
type WardInfo = {
  ward_no: number | null;
  ward_name: string | null;
  zone: string | null;
  local_body_type: string | null;
  locality_name: string | null;
  in_delhi: boolean;
};

type PageState = "map" | "confirming" | "complete";

const DELHI_DEFAULT: LatLng = { lat: 28.6139, lng: 77.2090 }; // Delhi centre

export default function LocationPage() {
  const router = useRouter();
  const profile = getProfile();

  const [loc, setLoc] = useState<LatLng>(DELHI_DEFAULT);
  const [pageState, setPageState] = useState<PageState>("map");
  const [wardInfo, setWardInfo] = useState<WardInfo | null>(null);
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);

  // Try GPS once on load to start centred on user
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLoc({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {},
        { timeout: 5000 },
      );
    }
  }, []);

  async function handleConfirmPin() {
    setResolving(true);
    setResolveError(null);
    try {
      const res = await api.geoResolve(loc.lat, loc.lng);
      setWardInfo(res);
      setPageState("confirming");
    } catch {
      setResolveError("Couldn't resolve location — check connection and try again.");
    } finally {
      setResolving(false);
    }
  }

  async function handleConfirmLocation() {
    if (!wardInfo) return;
    saveUserLocation({
      lat: loc.lat,
      lng: loc.lng,
      ward_no: wardInfo.ward_no,
      ward_name: wardInfo.ward_name,
      zone: wardInfo.zone,
      local_body_type: wardInfo.local_body_type,
    });

    // Sync to the backend BEFORE declaring onboarding complete — this used
    // to be fire-and-forget, which meant a stale/expired auth token at this
    // exact moment would silently fail and leave the account with no
    // server-side record at all, even though the UI looked successful.
    // Future sign-ins on any other device would then never find this
    // account's location.
    setSyncing(true);
    setSyncError(null);
    const profile = getProfile();
    const payload = {
      name: profile?.name,
      phone: profile?.phone,
      ward_no: wardInfo.ward_no,
      ward_name: wardInfo.ward_name,
      zone: wardInfo.zone,
      local_body_type: wardInfo.local_body_type,
      home_lat: loc.lat,
      home_lng: loc.lng,
    };

    async function trySync(): Promise<boolean> {
      try {
        await api.upsertMe(payload);
        return true;
      } catch {
        return false;
      }
    }

    let ok = await trySync();
    if (!ok) {
      // Token may have been stale at the first attempt — force a refresh
      // and retry once before giving up.
      try { await supabase.auth.refreshSession(); } catch { /* not signed in */ }
      ok = await trySync();
    }

    setSyncing(false);
    if (!ok) {
      setSyncError("Couldn't save your locality to the server. Check your connection and try again.");
      return;
    }

    markOnboardingComplete();
    setPageState("complete");
    setTimeout(() => {
      router.replace(`/my-locality?lat=${loc.lat}&lng=${loc.lng}`);
    }, 2200);
  }

  const firstName = profile?.name?.split(" ")[0] ?? "there";

  // ── Profile complete screen ──────────────────────────────────────────────
  if (pageState === "complete") {
    return (
      <div
        className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-8 text-center"
        style={{ maxWidth: 480, margin: "0 auto" }}
      >
        {/* Animated checkmark */}
        <div className="relative mb-8">
          <svg viewBox="0 0 80 80" className="h-24 w-24" fill="none">
            <circle cx="40" cy="40" r="36" stroke="#10b981" strokeWidth="3" strokeDasharray="226" strokeDashoffset="226"
              style={{ animation: "circle-draw 0.6s ease forwards" }} />
            <path d="M24 40l12 12 20-24" stroke="#10b981" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"
              strokeDasharray="60" strokeDashoffset="60"
              style={{ animation: "check-draw 0.4s ease 0.5s forwards" }} />
          </svg>
          <style>{`
            @keyframes circle-draw { to { stroke-dashoffset: 0; } }
            @keyframes check-draw  { to { stroke-dashoffset: 0; } }
          `}</style>
        </div>

        <p className="text-xs font-bold uppercase tracking-widest text-emerald-400 mb-2">Profile Complete</p>
        <h1 className="text-2xl font-extrabold text-white">
          Welcome, {firstName}!
        </h1>
        {wardInfo?.ward_name && (
          <p className="mt-3 text-sm text-slate-400">
            Your locality: <span className="text-slate-200 font-medium">{wardInfo.ward_name}</span>
          </p>
        )}
        <p className="mt-6 text-xs text-slate-600">Taking you to your locality…</p>
      </div>
    );
  }

  return (
    <div className="flex h-dvh flex-col bg-paper overflow-hidden" style={{ maxWidth: 480, margin: "0 auto" }}>

      {/* Header */}
      <div className="flex items-center gap-3 border-b border-slate-100 px-4 py-3">
        <button
          onClick={() => router.back()}
          className="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100"
        >
          ←
        </button>
        <div>
          <h1 className="text-sm font-bold text-slate-900">Set your locality</h1>
          <p className="text-[11px] text-slate-400">Drag the map to place the pin on your home</p>
        </div>
      </div>

      {/* Map — fills remaining space */}
      <div className="flex-1 px-3 pt-3 pb-2">
        <LocationStep value={loc} onChange={setLoc} />
      </div>

      {/* Bottom CTA */}
      <div className="border-t border-slate-100 px-4 pb-8 pt-3 space-y-2">
        {resolveError && (
          <p className="text-xs text-rose-500 text-center">{resolveError}</p>
        )}
        <button
          onClick={handleConfirmPin}
          disabled={resolving}
          className="w-full rounded-2xl bg-slate-900 py-4 text-sm font-bold text-white transition active:scale-95 disabled:opacity-50"
        >
          {resolving ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Identifying location…
            </span>
          ) : (
            "Confirm pin location →"
          )}
        </button>
      </div>

      {/* ── Location confirm bottom sheet ────────────────────────────── */}
      {pageState === "confirming" && wardInfo && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end" style={{ maxWidth: 480, margin: "0 auto" }}>
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setPageState("map")}
          />

          {/* Sheet */}
          <div className="relative rounded-t-3xl bg-paper px-6 pb-10 pt-5 shadow-2xl"
            style={{ animation: "slide-up 0.3s cubic-bezier(.4,0,.2,1) forwards" }}>
            <style>{`@keyframes slide-up { from { transform: translateY(100%); } to { transform: translateY(0); } }`}</style>

            {/* Handle */}
            <div className="mx-auto mb-5 h-1 w-10 rounded-full bg-slate-200" />

            {/* Ward info */}
            <div className="mb-5 rounded-2xl bg-cream p-4 space-y-2.5">
              {wardInfo.locality_name && (
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Area</span>
                  <span className="text-sm font-bold text-slate-900">{wardInfo.locality_name}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Ward</span>
                <span className="text-sm font-medium text-slate-700">
                  {wardInfo.ward_name ?? "—"}{wardInfo.ward_no ? ` (#${wardInfo.ward_no})` : ""}
                </span>
              </div>
              {wardInfo.zone && (
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Zone</span>
                  <span className="text-sm font-medium text-slate-700">{wardInfo.zone}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Authority</span>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                  wardInfo.local_body_type === "NDMC"
                    ? "bg-blue-50 text-blue-700"
                    : wardInfo.local_body_type === "DCB"
                    ? "bg-amber-50 text-amber-700"
                    : "bg-emerald-50 text-emerald-700"
                }`}>
                  {wardInfo.local_body_type ?? "—"}
                </span>
              </div>
              <div className="flex items-center justify-between border-t border-slate-100 pt-2.5">
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Coordinates</span>
                <span className="text-[11px] text-slate-500 tabular-nums">
                  {loc.lat.toFixed(4)}, {loc.lng.toFixed(4)}
                </span>
              </div>
            </div>

            <p className="mb-5 text-xs text-slate-500 text-center">
              Is this your correct locality? Civic issues and alerts will be personalised to this area.
            </p>

            {syncError && (
              <p className="mb-3 text-xs text-rose-500 text-center">{syncError}</p>
            )}

            <div className="space-y-2">
              <button
                onClick={handleConfirmLocation}
                disabled={syncing}
                className="w-full rounded-2xl bg-emerald-500 py-4 text-sm font-bold text-white transition hover:bg-emerald-400 active:scale-95 disabled:opacity-60"
              >
                {syncing ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Saving…
                  </span>
                ) : syncError ? (
                  "Try again"
                ) : (
                  "✓ Confirm location"
                )}
              </button>
              <button
                onClick={() => setPageState("map")}
                disabled={syncing}
                className="w-full rounded-2xl border border-slate-200 py-3.5 text-sm font-semibold text-slate-600 transition hover:bg-cream disabled:opacity-60"
              >
                Change location
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
