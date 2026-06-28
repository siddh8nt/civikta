"use client";

import { useState } from "react";
import Link from "next/link";

// ── Demo personas ──────────────────────────────────────────────────────────


// ── SVG icons ──────────────────────────────────────────────────────────────

function IconCitizen() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7 text-green-600" stroke="currentColor" strokeWidth={1.8}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" strokeLinecap="round" />
    </svg>
  );
}

function IconAuthority() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7 text-amber-600" stroke="currentColor" strokeWidth={1.8}>
      <rect x="8" y="2" width="8" height="4" rx="1" />
      <rect x="4" y="6" width="16" height="16" rx="2" />
      <path d="M9 12h6M9 16h4" strokeLinecap="round" />
    </svg>
  );
}

function IconOversight() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7 text-rose-600" stroke="currentColor" strokeWidth={1.8}>
      <path d="M12 3l8 3.5v5C20 16 16.5 20.5 12 22 7.5 20.5 4 16 4 11.5v-5L12 3z" />
      <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ── Card ───────────────────────────────────────────────────────────────────

function RoleCard({
  icon,
  label,
  title,
  description,
  selectLabel,
  options,
  staticName,
  staticBadge,
  href,
  btnText,
  btnClass,
}: {
  icon: React.ReactNode;
  label: string;
  title: string;
  description: string;
  selectLabel?: string;
  options?: string[];
  staticName?: string;
  staticBadge?: string;
  href: string;
  btnText: string;
  btnClass: string;
}) {
  const [selected, setSelected] = useState(options?.[0] ?? "");

  return (
    <div className="flex flex-col rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
      {/* Icon */}
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl border border-slate-100 bg-slate-50">
        {icon}
      </div>

      {/* Label + title */}
      <p className="mb-1 text-xs font-bold tracking-widest text-slate-400 uppercase">{label}</p>
      <h2 className="mb-3 text-lg font-bold text-slate-900">{title}</h2>

      {/* Description */}
      <p className="mb-6 flex-1 text-sm leading-relaxed text-slate-500">{description}</p>

      {/* Persona selector or credential display */}
      {options && selectLabel && (
        <div className="mb-4">
          <p className="mb-1.5 text-[10px] font-bold tracking-widest text-slate-400 uppercase">{selectLabel}</p>
          <div className="relative">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-700 focus:border-slate-400 focus:outline-none"
            >
              {options.map((o) => <option key={o}>{o}</option>)}
            </select>
            <svg className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </div>
        </div>
      )}

      {staticName && (
        <div className="mb-4">
          <p className="mb-1.5 text-[10px] font-bold tracking-widest text-slate-400 uppercase">Authorized Credentials</p>
          <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
            <span className="text-sm font-medium text-slate-700">{staticName}</span>
            {staticBadge && (
              <span className="rounded bg-rose-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-rose-700">
                {staticBadge}
              </span>
            )}
          </div>
        </div>
      )}

      {/* CTA */}
      <Link href={href} className={`flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 ${btnClass}`}>
        {btnText}
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
      </Link>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────

export default function Home() {

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">
            CV
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold tracking-wider text-slate-900">CIVIKTA</span>
              <span className="rounded bg-teal-50 px-2 py-0.5 text-[10px] font-bold tracking-widest text-teal-700 border border-teal-200">
                DELHI STATE PORTAL
              </span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-wide">Delhi Civic Issue Transparency &amp; Routing Platform</p>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-3xl px-6 py-14 text-center">
        <h1 className="mb-4 text-4xl font-extrabold tracking-tight text-slate-900">
          Delhi Civic Services Unified Gateway
        </h1>
        <p className="text-base leading-relaxed text-slate-500">
          A state-of-the-art decentralized pipeline bridging localized complaints with direct
          authority dispatch operators and state-level audit controllers. To begin, select your
          authorized portal route below.
        </p>
      </section>

      {/* Role cards */}
      <section className="mx-auto grid max-w-6xl grid-cols-1 gap-5 px-6 pb-16 md:grid-cols-3">
        <RoleCard
          icon={<IconCitizen />}
          label="Citizen"
          title="Citizen Portal"
          description="Report civic issues in your area, verify reports from neighbours, and track resolutions — all in one transparent feed."
          href="/onboarding"
          btnText="Enter Citizen Portal"
          btnClass="bg-green-600 hover:bg-green-700"
        />

        <RoleCard
          icon={<IconAuthority />}
          label="Local Authority"
          title="Departmental Portal"
          description="Receive geographically routed complaint feeds, dispatch localized work crews, update public resolution timelines, and report progress closures."
          href="/authority/portal"
          btnText="Enter Departmental Portal →"
          btnClass="bg-slate-900 hover:bg-slate-700"
        />

        <RoleCard
          icon={<IconOversight />}
          label="Oversight Secretariat"
          title="Secretariat Portal"
          description="Supervise department efficiency metrics, analyze anomalous localized volume spikes via active Gemini agents, and check inter-departmental accountability routing."
          href="/oversight/login"
          btnText="Enter Secretariat Portal"
          btnClass="bg-rose-600 hover:bg-rose-700"
        />
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-5 text-center">
        <p className="text-xs text-slate-400">
          National Capital Territory of Delhi (NCT) &bull; Civikta Central Routing Engine
        </p>
        <p className="mt-0.5 text-xs text-slate-300">
          Built with Google AI Studio &bull; Gemini 2.5 Flash &bull; Vibe2Ship Hackathon 2026
        </p>
      </footer>
    </div>
  );
}
