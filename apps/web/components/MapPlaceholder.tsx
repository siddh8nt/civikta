"use client";

/**
 * Feed map (PRD §8.3). When NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is set:
 *   - Google Map centered on the user's position (default: Delhi)
 *   - Coloured pin per issue (severity → colour)
 *   - Tap a pin → bottom-sheet card with title, urgency, link
 *
 * Without the key: shows the existing list-only fallback.
 */

import { useState } from "react";
import Link from "next/link";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
} from "@vis.gl/react-google-maps";
import type { IssueSummary } from "@/lib/types";

const MAPS_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? "";
const DELHI_CENTER = { lat: 28.6139, lng: 77.209 };

const SEV_PIN: Record<string, { bg: string; glyph: string }> = {
  low:      { bg: "#facc15", glyph: "#78350f" },
  medium:   { bg: "#f97316", glyph: "#fff7ed" },
  high:     { bg: "#ef4444", glyph: "#fff" },
  critical: { bg: "#7f1d1d", glyph: "#fca5a5" },
};

const SEV_ICON: Record<string, string> = {
  low: "🟡",
  medium: "🟠",
  high: "🔴",
  critical: "🔴",
};

// ── Real map with markers + bottom-sheet card ──────────────────────────────

function FeedMapInner({ issues }: { issues: IssueSummary[] }) {
  const [selected, setSelected] = useState<IssueSummary | null>(null);

  const center =
    issues.find((i) => i.latitude && i.longitude)
      ? { lat: issues[0].latitude!, lng: issues[0].longitude! }
      : DELHI_CENTER;

  return (
    <div className="relative overflow-hidden rounded-xl" style={{ height: "280px" }}>
      <Map
        style={{ height: "100%", width: "100%" }}
        defaultCenter={center}
        defaultZoom={13}
        gestureHandling="cooperative"
        disableDefaultUI
        zoomControl
        onClick={() => setSelected(null)}
      >
        {issues.map(
          (issue) =>
            issue.latitude &&
            issue.longitude && (
              <AdvancedMarker
                key={issue.id}
                position={{ lat: issue.latitude, lng: issue.longitude }}
                title={issue.title ?? undefined}
                onClick={(e) => {
                  e.stop();
                  setSelected(issue);
                }}
              >
                <Pin
                  background={SEV_PIN[issue.severity]?.bg ?? "#f97316"}
                  glyphColor={SEV_PIN[issue.severity]?.glyph ?? "#fff"}
                  borderColor="transparent"
                />
              </AdvancedMarker>
            ),
        )}
      </Map>

      {/* Bottom-sheet card */}
      {selected && (
        <div className="absolute bottom-0 left-0 right-0 rounded-t-xl bg-white p-3 shadow-2xl">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate font-medium text-sm">{selected.title}</p>
              <p className="mt-0.5 text-xs text-slate-500">
                🔥 {selected.urgency_score.toFixed(1)} · {selected.status.replace(/_/g, " ")} ·{" "}
                {selected.corroboration_count} corroborations
              </p>
            </div>
            <button
              onClick={() => setSelected(null)}
              className="shrink-0 rounded p-0.5 text-slate-400 hover:text-slate-700"
              aria-label="Close"
            >
              ✕
            </button>
          </div>
          <Link
            href={`/issues/${selected.id}`}
            className="mt-2 block text-xs font-semibold text-brand"
          >
            View details →
          </Link>
        </div>
      )}
    </div>
  );
}

// ── Fallback map (no key) ──────────────────────────────────────────────────

function FeedMapFallback({ issues }: { issues: IssueSummary[] }) {
  return (
    <div className="relative flex h-56 items-center justify-center rounded-xl bg-gradient-to-br from-teal-50 to-slate-100">
      <span className="text-xs text-slate-400">
        🗺️ Google Map renders here ({issues.length} markers)
      </span>
      {issues.slice(0, 6).map((i, idx) => (
        <span
          key={i.id}
          className="absolute text-xl"
          style={{ left: `${12 + idx * 14}%`, top: `${25 + (idx % 3) * 22}%` }}
          title={i.title ?? ""}
        >
          {SEV_ICON[i.severity] ?? "📍"}
        </span>
      ))}
    </div>
  );
}

// ── Public export ──────────────────────────────────────────────────────────

export function MapPlaceholder({ issues }: { issues: IssueSummary[] }) {
  const mapView = MAPS_KEY ? (
    <APIProvider apiKey={MAPS_KEY}>
      <FeedMapInner issues={issues} />
    </APIProvider>
  ) : (
    <FeedMapFallback issues={issues} />
  );

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200">
      {mapView}
      {/* Issue list below the map */}
      <div className="divide-y divide-slate-100">
        {issues.map((i) => (
          <Link
            key={i.id}
            href={`/issues/${i.id}`}
            className="flex items-center gap-2 p-2.5 text-sm"
          >
            <span>{SEV_ICON[i.severity] ?? "📍"}</span>
            <span className="flex-1 truncate">{i.title}</span>
            <span className="text-xs text-slate-400">🔥 {i.urgency_score.toFixed(1)}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
