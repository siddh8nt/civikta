"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { TopBar } from "@/components/TopBar";
import { hasCompletedOnboarding } from "@/lib/user";

function IconLocality({ active }: { active: boolean }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8}>
      <path d="M12 21s7-7.5 7-12a7 7 0 10-14 0c0 4.5 7 12 7 12z" strokeLinejoin="round" />
      <circle cx="12" cy="9" r="2.4" fill={active ? "currentColor" : "none"} />
    </svg>
  );
}

function IconRaise({ active }: { active: boolean }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v8M8 12h8" strokeLinecap="round" />
    </svg>
  );
}

function IconReports({ active }: { active: boolean }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth={active ? 2.2 : 1.8}>
      <rect x="5" y="3" width="14" height="18" rx="2.2" />
      <path d="M9 8h6M9 12h6M9 16h3.5" strokeLinecap="round" />
    </svg>
  );
}

const NAV = [
  { href: "/my-locality", label: "Locality", Icon: IconLocality },
  { href: "/raise", label: "Raise", Icon: IconRaise },
  { href: "/my-reports", label: "Reports", Icon: IconReports },
];

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!hasCompletedOnboarding()) {
      router.replace("/onboarding");
    }
  }, [router]);

  return (
    <div className="app-shell pt-10 pb-16">
      <TopBar />
      {children}
      <nav className="fixed bottom-0 left-1/2 z-20 flex w-full max-w-[480px] -translate-x-1/2 border-t border-slate-200 bg-paper">
        {NAV.map((n) => {
          const active = path === n.href || path.startsWith(n.href + "/");
          // All nav tabs use hard navigation so the phone always loads the latest JS
          return (
            <a
              key={n.href}
              href={n.href}
              className="flex flex-1 flex-col items-center gap-1 py-2.5 transition-transform active:scale-90"
            >
              <span
                className={`flex h-8 w-8 items-center justify-center rounded-full transition-colors duration-200 ${
                  active ? "bg-brand/10 text-brand" : "text-slate-400"
                }`}
              >
                <n.Icon active={active} />
              </span>
              <span
                className={`text-[11px] transition-colors duration-200 ${
                  active ? "font-bold text-brand" : "font-medium text-slate-400"
                }`}
              >
                {n.label}
              </span>
            </a>
          );
        })}
      </nav>
    </div>
  );
}
