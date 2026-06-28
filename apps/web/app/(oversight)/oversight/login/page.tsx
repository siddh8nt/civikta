"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const STEPS = [
  { label: "Establishing secure connection", pct: 18, duration: 550 },
  { label: "Verifying secretariat credentials", pct: 44, duration: 750 },
  { label: "Validating oversight authority", pct: 68, duration: 650 },
  { label: "Loading statewide intelligence", pct: 90, duration: 600 },
  { label: "Access granted", pct: 100, duration: 350 },
];

function OversightLoginContent() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let elapsed = 0;
    const timers: ReturnType<typeof setTimeout>[] = [];

    STEPS.forEach((step, i) => {
      elapsed += step.duration;
      const timer = setTimeout(() => {
        setCurrentStep(i);
        setProgress(step.pct);
        if (i === STEPS.length - 1) {
          setDone(true);
          const redirect = setTimeout(() => router.push("/oversight/dashboard"), 700);
          timers.push(redirect);
        }
      }, elapsed);
      timers.push(timer);
    });

    return () => timers.forEach(clearTimeout);
  }, [router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-12">
      <div className="mb-10 flex items-center gap-2 opacity-40">
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-[10px] font-bold text-slate-900">CV</div>
        <span className="text-xs font-bold tracking-widest text-white">CIVIKTA</span>
        <span className="text-slate-600">.</span>
        <span className="text-[10px] uppercase tracking-widest text-slate-400">Secure Portal</span>
      </div>

      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl border-2 border-rose-500/40 bg-white/5">
            <svg className="h-9 w-9 text-white/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.4}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3 4.5 6.25v5.25c0 4.55 3.2 8.8 7.5 10 4.3-1.2 7.5-5.45 7.5-10V6.25L12 3Z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 12.25 11.25 13.75 14.75 10.25" />
            </svg>
          </div>
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Authenticating</p>
          <h1 className="mt-1 text-2xl font-extrabold text-white">Oversight Secretariat</h1>
          <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-400" />
            <span className="text-xs text-slate-400">NCT Delhi Statewide Access</span>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-7 backdrop-blur-sm">
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs text-slate-500">Verification progress</span>
              <span className="text-xs font-bold tabular-nums text-white">{progress}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-rose-500 transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <div className="space-y-3.5">
            {STEPS.map((step, i) => {
              const isComplete = i < currentStep || (i === currentStep && done);
              const isActive = i === currentStep && !done;
              const isPending = i > currentStep;

              return (
                <div
                  key={step.label}
                  className={`flex items-center gap-3 transition-opacity duration-400 ${isPending ? "opacity-25" : "opacity-100"}`}
                >
                  <div
                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-white ${
                      isComplete ? "bg-green-500" : isActive ? "bg-rose-500" : "bg-white/10"
                    }`}
                  >
                    {isComplete ? (
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                    ) : isActive ? (
                      <div className="h-2 w-2 animate-spin rounded-full border border-white border-t-transparent" />
                    ) : null}
                  </div>
                  <span className={`text-sm ${isComplete ? "text-slate-400" : isActive ? "font-medium text-white" : "text-slate-600"}`}>
                    {step.label}
                    {isActive ? "..." : ""}
                  </span>
                </div>
              );
            })}
          </div>

          {done && (
            <div className="mt-6 rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-center">
              <p className="text-sm font-semibold text-green-400">Identity verified - entering dashboard</p>
            </div>
          )}
        </div>

        <p className="mt-5 text-center text-[10px] text-slate-700">
          CIVIKTA . Secure Government Portal . NCT Delhi
        </p>
      </div>
    </div>
  );
}

export default function OversightLoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-slate-950">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white" />
        </div>
      }
    >
      <OversightLoginContent />
    </Suspense>
  );
}