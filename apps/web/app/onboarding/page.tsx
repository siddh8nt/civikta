"use client";

import { useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { markOnboardingComplete } from "@/lib/user";

const SLIDES = [
  {
    icon: (
      <svg viewBox="0 0 64 64" fill="none" className="h-24 w-24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="32" cy="32" r="30" fill="#0f172a" />
        <path d="M20 34l8 8L44 24" stroke="#34d399" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    eyebrow: "Welcome to",
    headline: "CIVIKTA",
    sub: "Delhi's civic issue transparency and accountability platform. Your report goes straight to the authority responsible — no middlemen, no black holes.",
    accent: "text-emerald-400",
    bg: "from-slate-900 to-slate-800",
  },
  {
    icon: (
      <svg viewBox="0 0 64 64" fill="none" className="h-24 w-24">
        <circle cx="32" cy="32" r="30" fill="#1e3a5f" />
        <rect x="18" y="22" width="28" height="20" rx="3" stroke="#60a5fa" strokeWidth="2.5" />
        <circle cx="32" cy="32" r="4" fill="#60a5fa" />
        <path d="M32 22v-5M32 47v-5M18 32h-5M51 32h-5" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
    eyebrow: "Step 1",
    headline: "Report in 30 seconds",
    sub: "Describe the issue, drop your location, add a photo. Gemini AI classifies it and routes it to the exact authority — MCD, DJB, PWD — automatically.",
    accent: "text-blue-400",
    bg: "from-slate-900 to-blue-950",
  },
  {
    icon: (
      <svg viewBox="0 0 64 64" fill="none" className="h-24 w-24">
        <circle cx="32" cy="32" r="30" fill="#2d1b4e" />
        <circle cx="20" cy="28" r="5" fill="#a78bfa" />
        <circle cx="32" cy="22" r="5" fill="#a78bfa" />
        <circle cx="44" cy="28" r="5" fill="#a78bfa" />
        <path d="M20 33c0 6 5 9 12 9s12-3 12-9" stroke="#a78bfa" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    ),
    eyebrow: "Step 2",
    headline: "Community amplifies you",
    sub: "When your neighbours corroborate the same issue, it becomes a priority signal. The urgency score rises — authorities are pushed to act faster.",
    accent: "text-violet-400",
    bg: "from-slate-900 to-violet-950",
  },
  {
    icon: (
      <svg viewBox="0 0 64 64" fill="none" className="h-24 w-24">
        <circle cx="32" cy="32" r="30" fill="#1a2e1a" />
        <path d="M22 44V28l10-10 10 10v16" stroke="#4ade80" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="27" y="34" width="10" height="10" rx="1" stroke="#4ade80" strokeWidth="2" />
        <path d="M20 44h24" stroke="#4ade80" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    ),
    eyebrow: "Step 3",
    headline: "Track every action",
    sub: "Watch your issue move through the system in real time — field visits, repair schedules, rejections. Full transparency. No more reporting into the void.",
    accent: "text-green-400",
    bg: "from-slate-900 to-green-950",
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [slide, setSlide] = useState(0);
  const [exiting, setExiting] = useState(false);

  // Prefetch the signup route's JS as soon as onboarding mounts, so "Get
  // Started" navigates instantly instead of waiting on an on-demand fetch.
  useEffect(() => {
    router.prefetch("/onboarding/signup");
  }, [router]);

  // ── Swipe gesture state ──────────────────────────────────────────────────
  const viewportRef = useRef<HTMLDivElement>(null);
  const [viewportWidth, setViewportWidth] = useState(0);
  const [dragX, setDragX] = useState(0);
  const [dragging, setDragging] = useState(false);
  const startRef = useRef<{ x: number; y: number } | null>(null);
  const horizontalRef = useRef<boolean | null>(null); // null = undecided yet

  // Measure the actual rendered width so the track can be sized in px —
  // avoids flexbox % sizing ambiguity in nested flex containers.
  useEffect(() => {
    function measure() {
      if (viewportRef.current) setViewportWidth(viewportRef.current.offsetWidth);
    }
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  function goTo(i: number) {
    setSlide(Math.max(0, Math.min(SLIDES.length - 1, i)));
  }

  function onPointerDown(e: React.PointerEvent) {
    startRef.current = { x: e.clientX, y: e.clientY };
    horizontalRef.current = null;
    setDragging(true);
  }

  function onPointerMove(e: React.PointerEvent) {
    if (!startRef.current) return;
    const dx = e.clientX - startRef.current.x;
    const dy = e.clientY - startRef.current.y;

    // Decide gesture direction once movement is big enough to be intentional
    if (horizontalRef.current === null && (Math.abs(dx) > 8 || Math.abs(dy) > 8)) {
      horizontalRef.current = Math.abs(dx) > Math.abs(dy);
    }
    if (!horizontalRef.current) return; // vertical/ambiguous — ignore

    (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
    // Rubber-band resistance at the edges
    const atStart = slide === 0 && dx > 0;
    const atEnd = slide === SLIDES.length - 1 && dx < 0;
    setDragX(atStart || atEnd ? dx * 0.35 : dx);
  }

  function endDrag() {
    if (horizontalRef.current) {
      const threshold = 60;
      if (dragX <= -threshold) goTo(slide + 1);
      else if (dragX >= threshold) goTo(slide - 1);
    }
    setDragging(false);
    setDragX(0);
    startRef.current = null;
    horizontalRef.current = null;
  }

  function next() {
    if (slide < SLIDES.length - 1) {
      setSlide(slide + 1);
    } else {
      finish();
    }
  }

  function finish() {
    setExiting(true);
    router.replace("/onboarding/signup");
  }

  const s = SLIDES[slide];
  const isLast = slide === SLIDES.length - 1;

  return (
    <div
      className={`relative flex h-dvh flex-col bg-gradient-to-b ${s.bg} transition-colors duration-500 overflow-hidden`}
      style={{ maxWidth: 480, margin: "0 auto" }}
    >
      {/* Content wrapper — fades out on exit while the dark gradient behind it
          stays solid, so the transition never flashes the page's light body bg */}
      <div className={`flex h-full flex-col transition-opacity duration-150 ${exiting ? "opacity-0" : "opacity-100"}`}>
      {/* Skip */}
      <div className="flex justify-end px-6 pt-6">
        <button
          onClick={finish}
          className="text-xs font-medium text-slate-400 hover:text-slate-200"
        >
          Skip
        </button>
      </div>

      {/* Swipeable slide track */}
      <div
        ref={viewportRef}
        className="relative flex-1 overflow-hidden touch-pan-y"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onPointerLeave={() => dragging && endDrag()}
      >
        <div
          className="flex h-full"
          style={{
            width: viewportWidth ? SLIDES.length * viewportWidth : undefined,
            transform: `translateX(${viewportWidth ? -(slide * viewportWidth) + dragX : 0}px)`,
            transition: dragging ? "none" : "transform 380ms cubic-bezier(.22,1,.36,1)",
          }}
        >
          {SLIDES.map((slideData, i) => (
            <div
              key={i}
              className="flex h-full shrink-0 flex-col items-center justify-center px-8 pb-8 text-center select-none"
              style={{ width: viewportWidth || "100%" }}
            >
              <div className="mb-8">{slideData.icon}</div>

              <p className={`mb-2 text-xs font-bold uppercase tracking-widest ${slideData.accent}`}>
                {slideData.eyebrow}
              </p>
              <h1 className="mb-4 text-3xl font-extrabold tracking-tight text-white">
                {slideData.headline}
              </h1>
              <p className="max-w-xs text-sm leading-relaxed text-slate-300">{slideData.sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom nav */}
      <div className="shrink-0 px-8 pb-10">
        {/* Dots */}
        <div className="mb-8 flex justify-center gap-2">
          {SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => setSlide(i)}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === slide ? "w-6 bg-white" : "w-1.5 bg-slate-600"
              }`}
            />
          ))}
        </div>

        {/* CTA */}
        <button
          onClick={next}
          className={`w-full rounded-2xl py-4 text-sm font-bold tracking-wide transition-all ${
            isLast
              ? "bg-emerald-500 text-white hover:bg-emerald-400"
              : "bg-white/10 text-white hover:bg-white/20 border border-white/10"
          }`}
        >
          {isLast ? "Get Started →" : "Next"}
        </button>
      </div>
      </div>
    </div>
  );
}
