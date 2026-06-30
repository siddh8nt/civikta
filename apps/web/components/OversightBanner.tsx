"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { IssueSearchBar } from "@/components/IssueSearchBar";

const NAV = [
  { href: "/oversight/dashboard", label: "Dashboard" },
  { href: "/oversight/issues", label: "All Issues" },
  { href: "/oversight/hotspots", label: "Hotspots" },
];

function AnalyticsIcon() {
  return (
    <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456Z" />
    </svg>
  );
}

function EscalationIcon() {
  return (
    <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376C1.83 17.815 2.91 19.5 4.5 19.5h15c1.59 0 2.67-1.685 1.803-3.374L13.803 5.126c-.795-1.541-2.811-1.541-3.606 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
  );
}

export function OversightBanner() {
  const pathname = usePathname();

  return (
    <div className="border-b border-slate-200 bg-white">
      <div className="dashboard-shell flex flex-wrap items-center justify-between gap-3 py-3">
        <Link href="/" className="inline-flex shrink-0 items-center gap-1.5 text-sm font-bold tracking-wide text-slate-900">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-[10px] font-bold text-white">CV</div>
          CIVIKTA
          <span className="hidden text-xs font-medium text-slate-400 sm:inline">Oversight</span>
        </Link>

        <div className="flex flex-wrap items-center gap-2">
          <div className="w-52">
            <IssueSearchBar urlPrefix="/oversight/issues" />
          </div>

          <nav className="flex flex-wrap items-center gap-1.5">
            {NAV.map((n) => {
              const active = pathname === n.href;
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                    active
                      ? "border-slate-300 bg-slate-100 text-slate-900"
                      : "border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  {n.label}
                </Link>
              );
            })}
            <Link
              href="/oversight/analytics"
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold text-white transition-colors ${
                pathname === "/oversight/analytics" ? "bg-indigo-800" : "bg-indigo-700 hover:bg-indigo-800"
              }`}
            >
              <AnalyticsIcon />
              Analytics Agent
            </Link>
            <Link
              href="/oversight/escalations"
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold text-white transition-colors ${
                pathname === "/oversight/escalations" ? "bg-rose-800" : "bg-rose-700 hover:bg-rose-800"
              }`}
            >
              <EscalationIcon />
              Escalations
            </Link>
          </nav>
        </div>
      </div>
    </div>
  );
}
