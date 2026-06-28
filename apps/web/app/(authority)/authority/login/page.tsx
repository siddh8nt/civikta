"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type AuthMeta = {
  name: string;
  full: string;
  progressColor: string;
  ringColor: string;
};

const AUTHORITY_META: Record<string, AuthMeta> = {
  mcd:    { name: "MCD",          full: "Municipal Corporation of Delhi",           progressColor: "bg-blue-500",   ringColor: "border-blue-500/40" },
  ndmc:   { name: "NDMC",         full: "New Delhi Municipal Council",              progressColor: "bg-indigo-500", ringColor: "border-indigo-500/40" },
  dcb:    { name: "DCB",          full: "Delhi Cantonment Board",                   progressColor: "bg-slate-400",  ringColor: "border-slate-400/40" },
  djb:    { name: "Delhi Jal Board", full: "Delhi Jal Board",                       progressColor: "bg-teal-500",   ringColor: "border-teal-500/40" },
  pwd:    { name: "PWD",          full: "Public Works Department",                  progressColor: "bg-orange-500", ringColor: "border-orange-500/40" },
  ifcd:   { name: "IFCD",         full: "Irrigation & Flood Control Department",    progressColor: "bg-cyan-500",   ringColor: "border-cyan-500/40" },
  dda:    { name: "DDA",          full: "Delhi Development Authority",              progressColor: "bg-violet-500", ringColor: "border-violet-500/40" },
  police: { name: "Delhi Police", full: "Delhi Police",                             progressColor: "bg-slate-600",  ringColor: "border-slate-500/40" },
  nhai:   { name: "NHAI",         full: "National Highways Authority of India",     progressColor: "bg-amber-500",  ringColor: "border-amber-500/40" },
};

const STEPS = [
  { label: "Establishing secure connection",     pct: 18,  duration: 550 },
  { label: "Verifying authorized credentials",   pct: 46,  duration: 750 },
  { label: "Validating jurisdiction access",     pct: 70,  duration: 650 },
  { label: "Loading assigned issue queue",       pct: 90,  duration: 600 },
  { label: "Access granted",                     pct: 100, duration: 350 },
];

function LoginContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const authority = searchParams.get("authority") ?? "mcd";
  const zone = searchParams.get("zone");
  const meta = AUTHORITY_META[authority] ?? AUTHORITY_META.mcd;

  const [currentStep, setCurrentStep] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let elapsed = 0;
    const timers: ReturnType<typeof setTimeout>[] = [];

    STEPS.forEach((step, i) => {
      elapsed += step.duration;
      const t = setTimeout(() => {
        setCurrentStep(i);
        setProgress(step.pct);
        if (i === STEPS.length - 1) {
          setDone(true);
          const redirect = setTimeout(() => {
            const params = new URLSearchParams({ authority });
            if (zone) params.set("zone", zone);
            router.push(`/authority/dashboard?${params.toString()}`);
          }, 700);
          timers.push(redirect);
        }
      }, elapsed);
      timers.push(t);
    });

    return () => timers.forEach(clearTimeout);
  }, [authority, zone, router]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-12">
      {/* Brand line */}
      <div className="mb-10 flex items-center gap-2 opacity-40">
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-[10px] font-bold text-slate-900">CV</div>
        <span className="text-xs font-bold tracking-widest text-white">CIVIKTA</span>
        <span className="text-slate-600">·</span>
        <span className="text-[10px] tracking-widest text-slate-400 uppercase">Secure Portal</span>
      </div>

      <div className="w-full max-w-md">
        {/* Authority identity block */}
        <div className="mb-8 text-center">
          <div className={`mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl border-2 ${meta.ringColor} bg-white/5`}>
            <svg className="h-9 w-9 text-white/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.4}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
          </div>
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Authenticating</p>
          <h1 className="mt-1 text-2xl font-extrabold text-white">{meta.full}</h1>
          {zone && (
            <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1">
              <svg className="h-3 w-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
              </svg>
              <span className="text-xs text-slate-400">{zone} Zone</span>
            </div>
          )}
        </div>

        {/* Auth card */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-7 backdrop-blur-sm">
          {/* Progress bar */}
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs text-slate-500">Verification progress</span>
              <span className="text-xs font-bold tabular-nums text-white">{progress}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div
                className={`h-full rounded-full transition-all duration-500 ease-out ${meta.progressColor}`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Step list */}
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
                      isComplete
                        ? "bg-green-500"
                        : isActive
                        ? meta.progressColor
                        : "bg-white/10"
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
                  <span
                    className={`text-sm ${
                      isComplete ? "text-slate-400" : isActive ? "font-medium text-white" : "text-slate-600"
                    }`}
                  >
                    {step.label}
                    {isActive ? "…" : ""}
                  </span>
                </div>
              );
            })}
          </div>

          {done && (
            <div className="mt-6 rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-center">
              <p className="text-sm font-semibold text-green-400">Identity verified — entering dashboard</p>
            </div>
          )}
        </div>

        <p className="mt-5 text-center text-[10px] text-slate-700">
          CIVIKTA · Secure Government Portal · NCT Delhi
        </p>
      </div>
    </div>
  );
}

export default function AuthorityLoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-slate-950">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white" />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
