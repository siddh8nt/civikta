"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getProfile } from "@/lib/user";

const STAGES = [
  { label: "Connecting to DigiLocker", duration: 900 },
  { label: "Retrieving Aadhaar records", duration: 1400 },
  { label: "Performing KYC verification", duration: 1500 },
  { label: "Finalising your profile", duration: 1200 },
];

const TOTAL = STAGES.reduce((s, x) => s + x.duration, 0); // ~5000 ms

export default function KycPage() {
  const router = useRouter();
  const routerRef = useRef(router);
  const profile = getProfile();

  const [progress, setProgress] = useState(0);      // 0-100
  const [stageIdx, setStageIdx] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let elapsed = 0;
    let currentStage = 0;
    const interval = setInterval(() => {
      elapsed += 50;
      // Advance stage
      let stageCursor = 0;
      for (let i = 0; i < STAGES.length; i++) {
        stageCursor += STAGES[i].duration;
        if (elapsed < stageCursor) { currentStage = i; break; }
        currentStage = STAGES.length - 1;
      }
      setStageIdx(currentStage);
      const p = Math.min(100, Math.round((elapsed / TOTAL) * 100));
      setProgress(p);
      if (elapsed >= TOTAL) {
        clearInterval(interval);
        setDone(true);
        setTimeout(() => routerRef.current.replace("/onboarding/location"), 700);
      }
    }, 50);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-8"
      style={{ maxWidth: 480, margin: "0 auto" }}
    >
      {/* DigiLocker logo area */}
      <div className="mb-10 flex flex-col items-center gap-3">
        <div className="relative flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-600/10 border border-blue-500/20">
          {/* Pulsing ring */}
          {!done && (
            <span className="absolute inset-0 animate-ping rounded-3xl border border-blue-500/30" />
          )}
          <svg viewBox="0 0 48 48" fill="none" className="h-10 w-10">
            <rect x="8" y="4" width="32" height="40" rx="4" fill="#1d4ed8" opacity="0.15" stroke="#3b82f6" strokeWidth="1.5" />
            <path d="M16 16h16M16 22h16M16 28h10" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" />
            <circle cx="34" cy="32" r="8" fill="#1e40af" stroke="#3b82f6" strokeWidth="1.5" />
            <path d="M30.5 32l2.5 2.5 4-4" stroke="#60a5fa" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-blue-400">DigiLocker</p>
          <p className="text-xs text-slate-600 mt-0.5">Government of India</p>
        </div>
      </div>

      {/* Name */}
      {profile?.name && (
        <p className="mb-6 text-base font-semibold text-white">
          Verifying <span className="text-emerald-400">{profile.name}</span>
        </p>
      )}

      {/* Progress bar */}
      <div className="w-full mb-4">
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-400 transition-all duration-150"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-2 flex justify-between text-[10px] text-slate-600">
          <span>{done ? "Verified" : STAGES[stageIdx]?.label}…</span>
          <span className="tabular-nums">{progress}%</span>
        </div>
      </div>

      {/* Stage dots */}
      <div className="flex gap-2 mt-2">
        {STAGES.map((s, i) => (
          <div
            key={i}
            className={`h-1 rounded-full transition-all duration-300 ${
              i < stageIdx
                ? "w-6 bg-emerald-400"
                : i === stageIdx
                ? "w-6 bg-blue-400"
                : "w-2 bg-slate-700"
            }`}
          />
        ))}
      </div>

      {/* Done state */}
      {done && (
        <div className="mt-8 flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/30">
            <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-emerald-400" stroke="currentColor" strokeWidth={2.5}>
              <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-emerald-400">KYC Complete</p>
        </div>
      )}

      <p className="mt-8 text-center text-xs text-slate-700 leading-relaxed">
        Your data is encrypted end-to-end and governed under the Digital Personal Data Protection Act, 2023.
      </p>
    </div>
  );
}
