"use client";
import { statusLabel, categoryLabel, severityLabel } from "@/lib/labels";

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
        mapId="civikta_feed"
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
        <div className="absolute bottom-0 left-0 right-0 rounded-t-xl bg-paper p-3 shadow-2xl">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate font-medium text-sm">{selected.title}</p>
              <p className="mt-0.5 text-xs text-slate-500">
                {statusLabel(selected.status)} · {selected.corroboration_count} corroborations
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

// ── Locality stats card — replaces the issue list below the map ────────────

function LocalityStatsCard({ issues }: { issues: IssueSummary[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (issues.length === 0) {
    return (
      <div className="px-4 py-6 text-center text-sm text-slate-400">No open issues nearby.</div>
    );
  }

  const bySeverity: Record<string, number> = {};
  const byCategory: Record<string, IssueSummary[]> = {};
  let totalCorroborations = 0;

  for (const i of issues) {
    bySeverity[i.severity] = (bySeverity[i.severity] ?? 0) + 1;
    const cat = i.issue_category_slug ?? "other";
    (byCategory[cat] ??= []).push(i);
    totalCorroborations += i.corroboration_count;
  }

  const topCategories = Object.entries(byCategory).sort((a, b) => b[1].length - a[1].length);

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-slate-900">{issues.length}</span>
        <span className="text-sm text-slate-500">open issue{issues.length !== 1 ? "s" : ""} nearby</span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {(["critical", "high", "medium", "low"] as const).map((sev) =>
          bySeverity[sev] ? (
            <span
              key={sev}
              className="rounded-full px-2.5 py-1 text-xs font-semibold"
              style={{ backgroundColor: `${SEV_PIN[sev]?.bg}22`, color: SEV_PIN[sev]?.bg }}
            >
              {bySeverity[sev]} {severityLabel(sev)}
            </span>
          ) : null
        )}
      </div>

      <div className="space-y-0.5">
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">By category</p>
        {topCategories.map(([slug, list]) => (
          <div key={slug}>
            <button
              onClick={() => setExpanded(expanded === slug ? null : slug)}
              className="flex w-full items-center justify-between rounded-lg py-2 text-sm active:bg-cream"
            >
              <span className="text-slate-700">{categoryLabel(slug)}</span>
              <span className="flex items-center gap-1 text-slate-400">
                {list.length}
                <svg
                  viewBox="0 0 16 16"
                  className={`h-3 w-3 transition-transform ${expanded === slug ? "rotate-180" : ""}`}
                  fill="none"
                >
                  <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </button>
            {expanded === slug && (
              <div className="space-y-1.5 pb-2">
                {list.slice(0, 6).map((i) => (
                  <Link
                    key={i.id}
                    href={`/issues/${i.id}`}
                    className="block truncate rounded-lg border border-slate-200 bg-cream px-3 py-2 text-xs font-medium text-brand active:bg-slate-100"
                  >
                    {i.title}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <p className="border-t border-slate-100 pt-3 text-xs text-slate-500">
        ✓ {totalCorroborations} corroboration{totalCorroborations !== 1 ? "s" : ""} from neighbours nearby
      </p>
    </div>
  );
}

// ── Public export ──────────────────────────────────────────────────────────

export function MapPlaceholder({ issues }: { issues: IssueSummary[] }) {
  // Map view is for "what's still a problem nearby" — resolved/rejected
  // issues are noise here; full detail (including closed issues) lives
  // in the feed view already.
  const unresolved = issues.filter((i) => i.status !== "resolved" && i.status !== "rejected");

  const mapView = MAPS_KEY ? (
    <APIProvider apiKey={MAPS_KEY}>
      <FeedMapInner issues={unresolved} />
    </APIProvider>
  ) : (
    <FeedMapFallback issues={unresolved} />
  );

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-paper">
      {mapView}
      <LocalityStatsCard issues={unresolved} />
    </div>
  );
}
