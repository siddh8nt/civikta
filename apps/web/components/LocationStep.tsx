"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  APIProvider,
  Map,
  useMap,
} from "@vis.gl/react-google-maps";

const MAPS_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? "";

type LatLng = { lat: number; lng: number };

// ── Center pin SVG ─────────────────────────────────────────────────────────

function CenterPin({ lifted }: { lifted: boolean }) {
  return (
    <div
      style={{
        transform: lifted ? "translateY(-10px)" : "translateY(0)",
        transition: "transform 0.18s cubic-bezier(.4,2,.6,1)",
        filter: lifted ? "drop-shadow(0 6px 8px rgba(0,0,0,.35))" : "drop-shadow(0 2px 4px rgba(0,0,0,.25))",
      }}
    >
      <svg width="36" height="48" viewBox="0 0 36 48" fill="none">
        <path
          d="M18 0C8.059 0 0 8.059 0 18c0 7.184 4.132 13.417 10.163 16.544L18 48l7.837-13.456C31.868 31.417 36 25.184 36 18 36 8.059 27.941 0 18 0z"
          fill="#10b981"
        />
        <circle cx="18" cy="18" r="7" fill="white" />
      </svg>
    </div>
  );
}

// ── Shadow dot under pin ───────────────────────────────────────────────────

function PinShadow({ lifted }: { lifted: boolean }) {
  return (
    <div
      className="rounded-full bg-black/20"
      style={{
        width: lifted ? 10 : 14,
        height: lifted ? 4 : 6,
        transition: "all 0.18s",
        marginTop: 2,
      }}
    />
  );
}

type NominatimResult = { lat: string; lon: string; display_name: string };

// Approximate bounding box for NCT of Delhi
const DELHI_BOUNDS = { minLat: 28.40, maxLat: 28.88, minLng: 76.84, maxLng: 77.35 };
const DELHI_CENTER: LatLng = { lat: 28.6139, lng: 77.2090 };

function isInDelhi(lat: number, lng: number): boolean {
  return lat >= DELHI_BOUNDS.minLat && lat <= DELHI_BOUNDS.maxLat
      && lng >= DELHI_BOUNDS.minLng && lng <= DELHI_BOUNDS.maxLng;
}

// ── Inner: map + Nominatim search + GPS ────────────────────────────────────

function LocationStepInner({
  value,
  onChange,
}: {
  value: LatLng;
  onChange: (v: LatLng) => void;
}) {
  const map = useMap();
  const [dragging, setDragging] = useState(false);
  const [coords, setCoords] = useState(value);
  const [gpsState, setGpsState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [notInDelhi, setNotInDelhi] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<NominatimResult[]>([]);
  const [searching, setSearching] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const suppressRef = useRef(false);

  useEffect(() => {
    if (suppressRef.current) { suppressRef.current = false; return; }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length < 3) { setResults([]); return; }
    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&countrycodes=in&format=json&limit=5`,
          { headers: { "Accept-Language": "en" } },
        );
        setResults(await res.json());
      } catch { setResults([]); }
      finally { setSearching(false); }
    }, 500);
  }, [query]);

  function selectResult(r: NominatimResult) {
    const ll = { lat: parseFloat(r.lat), lng: parseFloat(r.lon) };
    map?.panTo(ll);
    map?.setZoom(17);
    suppressRef.current = true;
    setResults([]);
    setQuery(r.display_name.split(",")[0]);
  }

  const handleGPS = useCallback(() => {
    setGpsState("loading");

    function applyLL(ll: LatLng) {
      if (!isInDelhi(ll.lat, ll.lng)) { setNotInDelhi(true); setGpsState("idle"); return; }
      map?.panTo(ll);
      map?.setZoom(18);
      setCoords(ll);
      onChange(ll);
      setGpsState("done");
    }

    // Fallback chain when browser GPS is unavailable (LAN HTTP context on Android Chrome)
    async function fallbackGeolocate(): Promise<void> {
      // 1. Google Geolocation API — WiFi/cell accurate, works on HTTP, needs key + billing
      if (MAPS_KEY) {
        try {
          const res = await fetch(
            `https://www.googleapis.com/geolocation/v1/geolocate?key=${MAPS_KEY}`,
            { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
          );
          if (res.ok) {
            const d = await res.json();
            if (d.location?.lat != null) { applyLL({ lat: d.location.lat, lng: d.location.lng }); return; }
          }
        } catch { /* network error */ }
      }
      // 2. IP geolocation — city-level, no key needed
      try {
        const res = await fetch("https://ipapi.co/json/", { headers: { "Accept": "application/json" } });
        if (res.ok) {
          const d = await res.json();
          if (d.latitude != null) { applyLL({ lat: d.latitude, lng: d.longitude }); return; }
        }
      } catch { /* blocked / offline */ }
      // 3. Second free IP service
      try {
        const res = await fetch("https://ip-api.com/json/?fields=lat,lon,status");
        if (res.ok) {
          const d = await res.json();
          if (d.status === "success") { applyLL({ lat: d.lat, lng: d.lon }); return; }
        }
      } catch { /* blocked */ }
      setGpsState("error");
    }

    // On secure contexts (HTTPS / localhost) try native GPS first; fall back to IP.
    // On insecure contexts (LAN HTTP) Chrome blocks GPS immediately — skip straight to IP.
    const secure = typeof window !== "undefined" && window.isSecureContext;
    if (secure && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => applyLL({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => { fallbackGeolocate(); },
        { timeout: 6000 },
      );
    } else {
      fallbackGeolocate();
    }
  }, [map, onChange]);

  return (
    <div className="flex flex-col gap-2">
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          {searching
            ? <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
            : "🔍"}
        </span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search address, locality or landmark…"
          className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-9 pr-4 text-sm text-slate-800 shadow-sm placeholder-slate-400 focus:border-brand focus:outline-none"
          autoComplete="off"
        />
        {results.length > 0 && (
          <div className="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-lg">
            {results.map((r, i) => (
              <button
                key={i}
                type="button"
                onClick={() => selectResult(r)}
                className="w-full border-b border-slate-100 px-4 py-2.5 text-left text-sm text-slate-700 last:border-0 hover:bg-slate-50"
              >
                <span className="font-medium">{r.display_name.split(",")[0]}</span>
                <span className="block truncate text-xs text-slate-400">
                  {r.display_name.split(",").slice(1, 3).join(",")}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="relative overflow-hidden rounded-2xl shadow-md" style={{ height: 300 }}>
        <Map
          style={{ height: "100%", width: "100%" }}
          defaultCenter={value}
          defaultZoom={16}
          gestureHandling="greedy"
          disableDefaultUI
          zoomControl
          onCameraChanged={(e) => {
            const c = e.detail.center;
            setCoords({ lat: c.lat, lng: c.lng });
            onChange({ lat: c.lat, lng: c.lng });
          }}
          onDragstart={() => setDragging(true)}
          onDragend={() => setDragging(false)}
        />
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <CenterPin lifted={dragging} />
          <PinShadow lifted={dragging} />
        </div>
        {!dragging && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full bg-white/90 px-3 py-1 text-[11px] text-slate-600 shadow">
            Drag map to adjust pin
          </div>
        )}
      </div>

      <button
        type="button"
        onClick={handleGPS}
        disabled={gpsState === "loading"}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-brand py-3 text-sm font-semibold text-brand transition hover:bg-brand/5 disabled:opacity-50"
      >
        {gpsState === "loading"
          ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand border-t-transparent" />
          : "📍"}
        {gpsState === "loading" ? "Locating…" : gpsState === "done" ? "Drag to fine-tune" : gpsState === "error" ? "GPS unavailable" : "Use my location"}
      </button>

      <p className="text-center text-[11px] tabular-nums text-slate-400">
        {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}
      </p>

      {/* Not-in-Delhi dialog */}
      {notInDelhi && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 px-6">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-2xl">
              🗺️
            </div>
            <h3 className="text-base font-bold text-slate-900">Outside NCT of Delhi</h3>
            <p className="mt-2 text-sm text-slate-500 leading-relaxed">
              Your current GPS location is outside the National Capital Territory of Delhi.
              CIVIKTA only covers Delhi civic issues — please choose a location within Delhi.
            </p>
            <div className="mt-5 space-y-2">
              <button
                onClick={() => {
                  map?.panTo(DELHI_CENTER);
                  map?.setZoom(13);
                  setCoords(DELHI_CENTER);
                  onChange(DELHI_CENTER);
                  setNotInDelhi(false);
                  setGpsState("idle");
                }}
                className="w-full rounded-xl bg-emerald-500 py-3 text-sm font-bold text-white transition hover:bg-emerald-400"
              >
                📍 Place pin in central Delhi
              </button>
              <button
                onClick={() => setNotInDelhi(false)}
                className="w-full rounded-xl border border-slate-200 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Fallback (no API key) ──────────────────────────────────────────────────

function LocationStepFallback({
  value,
  onChange,
}: {
  value: LatLng;
  onChange: (v: LatLng) => void;
}) {
  const [status, setStatus] = useState("");
  const [notInDelhi, setNotInDelhi] = useState(false);

  const detect = () => {
    setStatus("Locating…");
    navigator.geolocation?.getCurrentPosition(
      (pos) => {
        const ll = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        if (!isInDelhi(ll.lat, ll.lng)) {
          setNotInDelhi(true);
          setStatus("");
          return;
        }
        onChange(ll);
        setStatus("Located ✓");
      },
      () => setStatus("GPS denied"),
      { timeout: 5000 },
    );
  };

  return (
    <div className="space-y-3">
      <input
        placeholder="🔍 Map search — add NEXT_PUBLIC_GOOGLE_MAPS_API_KEY"
        className="w-full cursor-not-allowed rounded-xl border border-slate-200 p-3 text-sm text-slate-400"
        disabled
        readOnly
      />
      <div className="relative flex h-56 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-50 to-slate-100">
        <span className="text-4xl">📍</span>
        <span className="absolute bottom-2 left-2 rounded bg-white/90 px-2 py-0.5 text-xs text-slate-500">
          {value.lat.toFixed(5)}, {value.lng.toFixed(5)}
        </span>
      </div>
      <button
        onClick={detect}
        type="button"
        className="w-full rounded-xl border border-brand p-3 text-sm font-semibold text-brand"
      >
        📍 Use my current location
      </button>
      {status && <p className="text-center text-xs text-slate-500">{status}</p>}

      {notInDelhi && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 px-6">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-2xl">
              🗺️
            </div>
            <h3 className="text-base font-bold text-slate-900">Outside NCT of Delhi</h3>
            <p className="mt-2 text-sm text-slate-500 leading-relaxed">
              Your current GPS location is outside the National Capital Territory of Delhi.
              CIVIKTA only covers Delhi civic issues — please choose a location within Delhi.
            </p>
            <div className="mt-5 space-y-2">
              <button
                onClick={() => { onChange(DELHI_CENTER); setNotInDelhi(false); setStatus("Using central Delhi ✓"); }}
                className="w-full rounded-xl bg-emerald-500 py-3 text-sm font-bold text-white transition hover:bg-emerald-400"
              >
                📍 Place pin in central Delhi
              </button>
              <button
                onClick={() => setNotInDelhi(false)}
                className="w-full rounded-xl border border-slate-200 py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Public export ──────────────────────────────────────────────────────────

export function LocationStep({
  value,
  onChange,
}: {
  value: LatLng;
  onChange: (v: LatLng) => void;
}) {
  if (!MAPS_KEY) return <LocationStepFallback value={value} onChange={onChange} />;

  return (
    <APIProvider apiKey={MAPS_KEY}>
      <LocationStepInner value={value} onChange={onChange} />
    </APIProvider>
  );
}
