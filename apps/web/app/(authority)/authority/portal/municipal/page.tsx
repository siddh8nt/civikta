"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const MCD_ZONES = [
  "Narela",
  "Rohini",
  "Civil Lines",
  "Keshavpuram",
  "Karol Bagh",
  "West",
  "Najafgarh",
  "Centre",
  "SP-City",
  "South",
  "Shahdara South",
  "Shahdara North",
];

function GovHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">CV</div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold tracking-wider text-slate-900">CIVIKTA</span>
              <span className="rounded border border-teal-200 bg-teal-50 px-2 py-0.5 text-[10px] font-bold tracking-widest text-teal-700">DELHI STATE PORTAL</span>
            </div>
            <p className="text-[10px] tracking-wide text-slate-400">Delhi Civic Issue Transparency &amp; Routing Platform</p>
          </div>
        </div>
        <Link href="/" className="text-xs text-slate-500 hover:text-slate-700">← Home</Link>
      </div>
    </header>
  );
}

export default function MunicipalPortalPage() {
  const [zone, setZone] = useState("South");
  const router = useRouter();

  return (
    <div className="min-h-screen bg-slate-50">
      <GovHeader />

      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <Link href="/authority/portal" className="mb-4 inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700">
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
            Departmental Portal
          </Link>
          <p className="mb-1 text-xs font-bold uppercase tracking-widest text-blue-600">Municipal</p>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Municipal Authorities</h1>
          <p className="mt-2 text-sm text-slate-500">Select your municipal body and — for MCD — your assigned zone.</p>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

          {/* MCD */}
          <div className="flex flex-col rounded-2xl border-2 border-blue-300 bg-white p-7 shadow-sm">
            <div className="mb-4 flex items-start justify-between">
              <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-blue-700">Municipal</span>
              <span className="text-[10px] text-slate-400">272 wards · 12 zones</span>
            </div>

            <h2 className="text-2xl font-extrabold text-slate-900">MCD</h2>
            <p className="mt-0.5 text-sm font-semibold text-blue-700">Municipal Corporation of Delhi</p>
            <p className="mt-3 text-xs leading-relaxed text-slate-500">
              Governs ~95% of Delhi's residential and commercial areas. Four departments — Sanitation, Engineering, Horticulture, and Public Health.
            </p>

            <div className="mt-2 space-y-1 text-[10px] text-slate-400">
              <p>· Largest urban municipal body in India</p>
              <p>· 12 administrative zones</p>
              <p>· SLA: 24–72 hrs by department</p>
            </div>

            <div className="mt-5">
              <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-400">Select Your Zone</p>
              <div className="relative">
                <select
                  value={zone}
                  onChange={(e) => setZone(e.target.value)}
                  className="w-full appearance-none rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 pr-8 text-sm text-slate-700 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  {MCD_ZONES.map((z) => (
                    <option key={z}>{z}</option>
                  ))}
                </select>
                <svg className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <p className="mt-1.5 text-[10px] text-slate-400">You will see issues assigned within this zone only.</p>
            </div>

            <button
              onClick={() => router.push(`/authority/login?authority=mcd&zone=${encodeURIComponent(zone)}`)}
              className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              Enter MCD Portal
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </button>
          </div>

          {/* NDMC */}
          <div className="flex flex-col rounded-2xl border-2 border-indigo-200 bg-white p-7 shadow-sm">
            <div className="mb-4">
              <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-indigo-700">Municipal</span>
            </div>

            <h2 className="text-2xl font-extrabold text-slate-900">NDMC</h2>
            <p className="mt-0.5 text-sm font-semibold text-indigo-700">New Delhi Municipal Council</p>
            <p className="mt-3 flex-1 text-xs leading-relaxed text-slate-500">
              Governs Lutyens' Delhi — Connaught Place, India Gate precinct, Khan Market, Chanakyapuri embassies, and surrounding planned zones.
            </p>

            <div className="mt-4 space-y-1 text-[10px] text-slate-400">
              <p>· 3 administrative wards</p>
              <p>· Unified civil + sanitation + horticulture</p>
              <p>· SLA: 24–72 hrs</p>
            </div>

            <div className="mt-4 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2.5">
              <p className="text-[10px] font-medium text-indigo-600">Jurisdiction: NDMC Central · NDMC South · NDMC West</p>
            </div>

            <Link
              href="/authority/login?authority=ndmc"
              className="mt-5 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700"
            >
              Enter NDMC Portal
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </div>

          {/* DCB */}
          <div className="flex flex-col rounded-2xl border-2 border-slate-200 bg-white p-7 shadow-sm">
            <div className="mb-4">
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-slate-600">Cantonment</span>
            </div>

            <h2 className="text-2xl font-extrabold text-slate-900">DCB</h2>
            <p className="mt-0.5 text-sm font-semibold text-slate-600">Delhi Cantonment Board</p>
            <p className="mt-3 flex-1 text-xs leading-relaxed text-slate-500">
              Governs Delhi Cantonment, Dhaula Kuan, Naraina, and designated cantonment areas. Operates under Ministry of Defence purview.
            </p>

            <div className="mt-4 space-y-1 text-[10px] text-slate-400">
              <p>· Ministry of Defence jurisdiction</p>
              <p>· Single unified board</p>
              <p>· SLA: 72 hrs</p>
            </div>

            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
              <p className="text-[10px] font-medium text-slate-500">Jurisdiction: Delhi Cantonment · Dhaula Kuan · Naraina</p>
            </div>

            <Link
              href="/authority/login?authority=dcb"
              className="mt-5 flex items-center justify-center gap-2 rounded-xl bg-slate-700 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            >
              Enter DCB Portal
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </div>
        </div>
      </div>

      <footer className="border-t border-slate-200 bg-white py-5 text-center">
        <p className="text-xs text-slate-400">National Capital Territory of Delhi (NCT) · Civikta Central Routing Engine</p>
      </footer>
    </div>
  );
}
