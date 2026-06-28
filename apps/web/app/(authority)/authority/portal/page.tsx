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

const CATEGORIES = [
  {
    key: "municipal",
    label: "Municipal Authorities",
    tagline: "MCD · NDMC · Delhi Cantonment Board",
    description:
      "Access ward-level issue queues for the three municipal bodies governing Delhi's residential, commercial, and planned areas. Includes zone-specific routing for MCD.",
    href: "/authority/portal/municipal",
    borderColor: "border-blue-200",
    tagBg: "bg-blue-100 text-blue-700",
    btnClass: "bg-blue-600 hover:bg-blue-700",
    icon: (
      <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
      </svg>
    ),
  },
  {
    key: "service",
    label: "Service Departments",
    tagline: "DJB · PWD · IFCD · DDA",
    description:
      "City-wide infrastructure and utility departments responsible for water supply, arterial roads, storm drainage, and land development across all of Delhi.",
    href: "/authority/portal/service",
    borderColor: "border-teal-200",
    tagBg: "bg-teal-100 text-teal-700",
    btnClass: "bg-teal-600 hover:bg-teal-700",
    icon: (
      <svg className="h-8 w-8 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
      </svg>
    ),
  },
  {
    key: "police",
    label: "Delhi Police",
    tagline: "Law Enforcement",
    description:
      "Traffic signal failures, footpath and road encroachments, vehicle removals, noise complaints, and civil enforcement issues across Delhi.",
    href: "/authority/login?authority=police",
    borderColor: "border-slate-300",
    tagBg: "bg-slate-100 text-slate-700",
    btnClass: "bg-slate-800 hover:bg-slate-900",
    icon: (
      <svg className="h-8 w-8 text-slate-800" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
      </svg>
    ),
  },
  {
    key: "nhai",
    label: "NHAI",
    tagline: "National Highways Authority of India",
    description:
      "National highway infrastructure issues — NH-8 (Gurgaon), NH-44 (Sonepat), NH-48, Delhi–Meerut Expressway, and the Delhi urban expressway network.",
    href: "/authority/login?authority=nhai",
    borderColor: "border-amber-200",
    tagBg: "bg-amber-100 text-amber-700",
    btnClass: "bg-amber-600 hover:bg-amber-700",
    icon: (
      <svg className="h-8 w-8 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
      </svg>
    ),
  },
];

export default function PortalPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <GovHeader />

      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <p className="mb-1 text-xs font-bold uppercase tracking-widest text-slate-400">Authority Access</p>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Departmental Portal</h1>
          <p className="mt-2 text-sm text-slate-500">Select your authority category to access your assigned issue queue.</p>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          {CATEGORIES.map((c) => (
            <div key={c.key} className={`flex flex-col rounded-2xl border-2 bg-white p-7 shadow-sm ${c.borderColor}`}>
              <div className="mb-4">{c.icon}</div>
              <span className={`mb-3 inline-block self-start rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest ${c.tagBg}`}>
                {c.tagline}
              </span>
              <h2 className="mb-2 text-xl font-bold text-slate-900">{c.label}</h2>
              <p className="mb-7 flex-1 text-sm leading-relaxed text-slate-500">{c.description}</p>
              <Link
                href={c.href}
                className={`flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white transition-opacity ${c.btnClass}`}
              >
                Enter
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
