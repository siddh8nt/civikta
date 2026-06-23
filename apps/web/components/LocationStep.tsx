"use client";

/**
 * Uber/Rapido-style location picker (PRD §8.4 Step 2).
 *
 * When NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is set:
 *   - Google Places Autocomplete search box (restricted to India, Delhi-biased)
 *   - Interactive Google Map with a draggable pin (reverse-geocodes on dragend)
 *   - "Use my current location" GPS button that pans the map
 *
 * Without the key: GPS button still works; map shows coordinates as text.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  useMap,
  useMapsLibrary,
} from "@vis.gl/react-google-maps";

const MAPS_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ?? "";

// Rough bounding box for Delhi — biases Places results
const DELHI_BOUNDS = {
  north: 28.88,
  south: 28.4,
  east: 77.35,
  west: 76.84,
};

type LatLng = { lat: number; lng: number };

// ── Places search box ──────────────────────────────────────────────────────

function PlacesSearch({ onSelect }: { onSelect: (v: LatLng) => void }) {
  const places = useMapsLibrary("places");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!places || !inputRef.current) return;
    const ac = new places.Autocomplete(inputRef.current, {
      componentRestrictions: { country: "in" },
      fields: ["geometry", "name"],
      bounds: new google.maps.LatLngBounds(
        { lat: DELHI_BOUNDS.south, lng: DELHI_BOUNDS.west },
        { lat: DELHI_BOUNDS.north, lng: DELHI_BOUNDS.east },
      ),
      strictBounds: false,
    });
    const listener = ac.addListener("place_changed", () => {
      const place = ac.getPlace();
      const loc = place.geometry?.location;
      if (loc) onSelect({ lat: loc.lat(), lng: loc.lng() });
    });
    return () => google.maps.event.removeListener(listener);
  }, [places, onSelect]);

  return (
    <input
      ref={inputRef}
      placeholder="🔍 Search address / locality / landmark…"
      className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-brand focus:outline-none"
      autoComplete="off"
    />
  );
}

// ── Draggable marker (child of <Map> so useMap() works) ────────────────────

function DraggableMarker({
  value,
  onChange,
}: {
  value: LatLng;
  onChange: (v: LatLng) => void;
}) {
  const map = useMap();

  // Pan the map whenever the location changes externally (GPS / Places)
  useEffect(() => {
    if (map) map.panTo(value);
  }, [value, map]);

  return (
    <AdvancedMarker
      position={value}
      draggable
      onDragEnd={(e) => {
        if (e.latLng) onChange({ lat: e.latLng.lat(), lng: e.latLng.lng() });
      }}
    />
  );
}

// ── Full map + search + GPS ────────────────────────────────────────────────

function LocationStepInner({
  value,
  onChange,
}: {
  value: LatLng;
  onChange: (v: LatLng) => void;
}) {
  const [gpsStatus, setGpsStatus] = useState("");

  const detect = useCallback(() => {
    setGpsStatus("Locating…");
    navigator.geolocation?.getCurrentPosition(
      (pos) => {
        onChange({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setGpsStatus("Located via GPS");
      },
      () => setGpsStatus("GPS denied — drag pin or search"),
      { timeout: 5000 },
    );
  }, [onChange]);

  return (
    <div className="space-y-3">
      <PlacesSearch onSelect={onChange} />

      <Map
        style={{ height: "176px", width: "100%", borderRadius: "8px" }}
        defaultCenter={value}
        defaultZoom={16}
        gestureHandling="cooperative"
        disableDefaultUI
        zoomControl
      >
        <DraggableMarker value={value} onChange={onChange} />
      </Map>

      <button
        onClick={detect}
        type="button"
        className="w-full rounded-lg border border-brand p-2.5 text-sm font-medium text-brand"
      >
        📍 Use my current location
      </button>

      <p className="text-center text-xs text-slate-500">
        {gpsStatus || `${value.lat.toFixed(5)}, ${value.lng.toFixed(5)}`}
      </p>
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

  const detect = () => {
    setStatus("Locating…");
    navigator.geolocation?.getCurrentPosition(
      (pos) => {
        onChange({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setStatus("Located via GPS");
      },
      () => setStatus("GPS denied — set NEXT_PUBLIC_GOOGLE_MAPS_API_KEY to enable map search"),
      { timeout: 5000 },
    );
  };

  return (
    <div className="space-y-3">
      <input
        placeholder="🔍 Map search — add NEXT_PUBLIC_GOOGLE_MAPS_API_KEY to enable"
        className="w-full cursor-not-allowed rounded-lg border border-slate-200 p-3 text-sm text-slate-400"
        disabled
        readOnly
      />
      <div className="relative flex h-44 items-center justify-center rounded-lg bg-gradient-to-br from-teal-50 to-slate-100">
        <span className="text-3xl">📍</span>
        <span className="absolute bottom-2 left-2 rounded bg-white/90 px-2 py-0.5 text-xs text-slate-500">
          {value.lat.toFixed(4)}, {value.lng.toFixed(4)}
        </span>
      </div>
      <button
        onClick={detect}
        type="button"
        className="w-full rounded-lg border border-brand p-2.5 text-sm font-medium text-brand"
      >
        📍 Use my current location
      </button>
      {status && <p className="text-center text-xs text-slate-500">{status}</p>}
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
    <APIProvider apiKey={MAPS_KEY} libraries={["places"]}>
      <LocationStepInner value={value} onChange={onChange} />
    </APIProvider>
  );
}
