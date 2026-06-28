"use client";

import Link from "next/link";

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

const DEPARTMENTS = [
  {
    slug: "djb",
    short: "DJB",
    full: "Delhi Jal Board",
    dept: "Water Supply &amp; Sewerage",
    description: "All water and sewer infrastructure across Delhi — pipelines, sewer overflow, manholes, water supply disruptions, contamination, and public taps.",
    scope: "Citywide · All local body types",
    sla: "12 hrs",
    borderColor: "border-teal-200",
    tagBg: "bg-teal-100 text-teal-700",
    slaColor: "text-teal-700 bg-teal-50",
    btnClass: "bg-teal-600 hover:bg-teal-700",
    icon: (
      <svg className="h-7 w-7 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c-1.2 5.4-6 7.8-6 12a6 6 0 0 0 12 0c0-4.2-4.8-6.6-6-12Z" />
      </svg>
    ),
  },
  {
    slug: "pwd",
    short: "PWD",
    full: "Public Works Department",
    dept: "Roads, Bridges &amp; Public Buildings",
    description: "Arterial roads, ring roads, flyovers, bridges, road dividers, and state-owned public buildings. Issues on collector and arterial road classes.",
    scope: "Arterial & collector roads · Citywide",
    sla: "72 hrs",
    borderColor: "border-orange-200",
    tagBg: "bg-orange-100 text-orange-700",
    slaColor: "text-orange-700 bg-orange-50",
    btnClass: "bg-orange-500 hover:bg-orange-600",
    icon: (
      <svg className="h-7 w-7 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
      </svg>
    ),
  },
  {
    slug: "ifcd",
    short: "IFCD",
    full: "Irrigation &amp; Flood Control Department",
    dept: "Storm Drains &amp; Flood Infrastructure",
    description: "Trunk drains, nallahs, Yamuna embankments, and flood control infrastructure. Primary authority for major waterlogging and seasonal flooding incidents.",
    scope: "Trunk drains · Yamuna embankments",
    sla: "48 hrs",
    borderColor: "border-cyan-200",
    tagBg: "bg-cyan-100 text-cyan-700",
    slaColor: "text-cyan-700 bg-cyan-50",
    btnClass: "bg-cyan-600 hover:bg-cyan-700",
    icon: (
      <svg className="h-7 w-7 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 0 0 4.5 4.5H18a3.75 3.75 0 0 0 1.332-7.257 3 3 0 0 0-3.758-3.848 5.25 5.25 0 0 0-10.233 2.33A4.502 4.502 0 0 0 2.25 15Z" />
      </svg>
    ),
  },
  {
    slug: "dda",
    short: "DDA",
    full: "Delhi Development Authority",
    dept: "Land, Housing &amp; Parks",
    description: "DDA-owned parks, housing colonies, land parcels, and public spaces. Encroachments on DDA land, park maintenance, and broken public fixtures.",
    scope: "DDA parks, housing & land",
    sla: "168 hrs",
    borderColor: "border-violet-200",
    tagBg: "bg-violet-100 text-violet-700",
    slaColor: "text-violet-700 bg-violet-50",
    btnClass: "bg-violet-600 hover:bg-violet-700",
    icon: (
      <svg className="h-7 w-7 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12 11.204 3.045c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
  },
];

export default function ServicePortalPage() {
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
          <p className="mb-1 text-xs font-bold uppercase tracking-widest text-teal-600">Service Departments</p>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Infrastructure &amp; Utility Departments</h1>
          <p className="mt-2 text-sm text-slate-500">City-wide authorities responsible for water, roads, drainage, and land — select your department.</p>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          {DEPARTMENTS.map((d) => (
            <div key={d.slug} className={`flex flex-col rounded-2xl border-2 bg-white p-7 shadow-sm ${d.borderColor}`}>
              <div className="mb-4 flex items-start justify-between">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl border ${d.borderColor} bg-white`}>
                  {d.icon}
                </div>
                <span className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest ${d.slaColor}`}>
                  SLA {d.sla}
                </span>
              </div>

              <span className={`mb-2 inline-block self-start rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest ${d.tagBg}`}>
                {d.short}
              </span>

              <h2 className="mt-1 text-xl font-bold text-slate-900" dangerouslySetInnerHTML={{ __html: d.full }} />
              <p className="mt-0.5 text-xs font-medium text-slate-500" dangerouslySetInnerHTML={{ __html: d.dept }} />
              <p className="mt-3 flex-1 text-sm leading-relaxed text-slate-500">{d.description}</p>

              <div className="mt-4 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2">
                <p className="text-[10px] font-medium text-slate-500" dangerouslySetInnerHTML={{ __html: d.scope }} />
              </div>

              <Link
                href={`/authority/login?authority=${d.slug}`}
                className={`mt-5 flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white transition ${d.btnClass}`}
              >
                Enter {d.short} Portal
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                </svg>
              </Link>
            </div>
          ))}
        </div>
      </div>

      <footer className="border-t border-slate-200 bg-white py-5 text-center">
        <p className="text-xs text-slate-400">National Capital Territory of Delhi (NCT) · Civikta Central Routing Engine</p>
      </footer>
    </div>
  );
}
