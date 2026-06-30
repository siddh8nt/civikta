"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { getProfile, getUserLocation, resetOnboarding } from "@/lib/user";
import { supabase } from "@/lib/supabase";

// Pages that show a back-to-locality arrow on the left
const BACK_TO_LOCALITY = new Set(["/raise", "/my-reports"]);

export function TopBar() {
  const path = usePathname();
  const router = useRouter();
  const [accountOpen, setAccountOpen] = useState(false);

  const isLocality = path === "/my-locality";
  const isIssueDetail = path.startsWith("/issues/");
  const showBackToLocality = BACK_TO_LOCALITY.has(path) || isIssueDetail;

  // ── Left slot ────────────────────────────────────────────────────────────

  let left: React.ReactNode;
  if (isLocality) {
    left = (
      <Link
        href="/"
        className="flex items-center gap-1 text-xs font-medium text-slate-500 active:text-brand"
      >
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden>
          <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Main Portal
      </Link>
    );
  } else if (showBackToLocality) {
    left = (
      <button
        onClick={() => router.push("/my-locality")}
        className="flex items-center gap-1 text-sm text-slate-500 active:bg-slate-100 rounded-lg py-1 pr-2"
        aria-label="Back to My Locality"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
          <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Back
      </button>
    );
  } else {
    left = <div className="w-14" />;
  }

  // ── Right slot ───────────────────────────────────────────────────────────

  let right: React.ReactNode;
  if (isLocality) {
    right = (
      <button
        onClick={() => setAccountOpen(true)}
        className="ml-auto flex items-center gap-1.5 rounded-full border border-slate-200 bg-cream px-2.5 py-1 text-xs font-semibold text-slate-600 active:bg-slate-100"
        aria-label="My Account"
      >
        <svg width="14" height="14" viewBox="0 0 20 20" fill="none" aria-hidden>
          <circle cx="10" cy="7" r="3.5" stroke="currentColor" strokeWidth="1.6"/>
          <path d="M3 18c0-3.5 3.1-6 7-6s7 2.5 7 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
        </svg>
        Account
      </button>
    );
  } else {
    right = <div className="w-14" />;
  }

  return (
    <>
      <div className="fixed left-1/2 top-0 z-30 flex h-10 w-full max-w-[480px] -translate-x-1/2 items-center border-b border-slate-200 bg-paper px-3 shadow-sm">
        {left}
        <Link
          href="/my-locality"
          className="absolute left-1/2 -translate-x-1/2 text-[11px] font-black tracking-[0.18em] text-brand"
          aria-label="CIVIKTA home"
        >
          CIVIKTA
        </Link>
        {right}
      </div>

      {/* My Account sheet */}
      {accountOpen && <AccountSheet onClose={() => setAccountOpen(false)} onSignOut={() => {
        supabase.auth.signOut().catch(() => {});
        resetOnboarding();
        setAccountOpen(false);
        router.replace("/");
      }} />}
    </>
  );
}

function AccountSheet({ onClose, onSignOut }: { onClose: () => void; onSignOut: () => void }) {
  const profile = getProfile();
  const location = getUserLocation();
  const sheetRef = useRef<HTMLDivElement>(null);
  const dragStartY = useRef<number | null>(null);
  const currentY = useRef(0);

  function onTouchStart(e: React.TouchEvent) {
    dragStartY.current = e.touches[0].clientY;
    currentY.current = 0;
    if (sheetRef.current) sheetRef.current.style.transition = "none";
  }

  function onTouchMove(e: React.TouchEvent) {
    if (dragStartY.current === null) return;
    const dy = e.touches[0].clientY - dragStartY.current;
    if (dy < 0) return; // don't allow dragging up
    currentY.current = dy;
    if (sheetRef.current) sheetRef.current.style.transform = `translateX(-50%) translateY(${dy}px)`;
  }

  function onTouchEnd() {
    if (currentY.current > 100) {
      onClose();
    } else {
      if (sheetRef.current) {
        sheetRef.current.style.transition = "transform 0.25s ease";
        sheetRef.current.style.transform = "translateX(-50%) translateY(0)";
      }
    }
    dragStartY.current = null;
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Sheet */}
      <div
        ref={sheetRef}
        className="fixed bottom-0 left-1/2 z-50 w-full max-w-[480px] -translate-x-1/2 rounded-t-2xl bg-paper pb-10 shadow-xl"
        style={{ transition: "transform 0.25s ease" }}
      >
        {/* Drag handle */}
        <div
          className="flex w-full justify-center pt-3 pb-2 cursor-grab active:cursor-grabbing touch-none"
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
          onClick={onClose}
        >
          <div className="h-1 w-10 rounded-full bg-slate-300" />
        </div>

        <div className="px-5 pt-3 pb-4">
          {/* Avatar + name */}
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand/10 text-lg font-bold text-brand">
              {profile?.name ? profile.name[0].toUpperCase() : "?"}
            </div>
            <div>
              <p className="font-semibold text-slate-900">{profile?.name ?? "Citizen"}</p>
              <p className="text-xs text-slate-400">{profile?.phone ? `+91 ${profile.phone}` : "—"}</p>
            </div>
          </div>

          {/* Locality details */}
          <div className="mb-5 rounded-xl border border-slate-100 bg-cream divide-y divide-slate-100">
            <Row label="Ward" value={location?.ward_name ?? "—"} />
            <Row label="Ward No." value={location?.ward_no != null ? `#${location.ward_no}` : "—"} />
            <Row label="Zone" value={location?.zone ?? "—"} />
            <Row label="Local body" value={location?.local_body_type ?? "—"} />
            {location?.lat != null && (
              <Row
                label="Coordinates"
                value={`${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}`}
              />
            )}
          </div>

          {/* Sign out */}
          <button
            onClick={onSignOut}
            className="w-full rounded-xl border border-rose-200 py-3 text-sm font-semibold text-rose-500 active:bg-rose-50"
          >
            Sign out
          </button>
        </div>
      </div>
    </>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-3 py-2.5 text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="font-medium text-slate-700">{value}</span>
    </div>
  );
}
