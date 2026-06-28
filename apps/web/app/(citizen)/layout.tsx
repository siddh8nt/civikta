"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { TopBar } from "@/components/TopBar";
import { hasCompletedOnboarding } from "@/lib/user";

const NAV = [
  { href: "/my-locality", label: "Locality", icon: "🗺️" },
  { href: "/raise", label: "Raise", icon: "➕" },
  { href: "/my-reports", label: "Reports", icon: "📋" },
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
      <nav className="fixed bottom-0 left-1/2 z-20 flex w-full max-w-[480px] -translate-x-1/2 border-t border-slate-200 bg-white">
        {NAV.map((n) => {
          const active = path === n.href || path.startsWith(n.href + "/");
          const cls = `flex flex-1 flex-col items-center gap-0.5 py-2 text-xs ${active ? "text-brand" : "text-slate-400"}`;
          // All nav tabs use hard navigation so the phone always loads the latest JS
          return (
            <a key={n.href} href={n.href} className={cls}>
              <span className="text-lg">{n.icon}</span>
              {n.label}
            </a>
          );
        })}
      </nav>
    </div>
  );
}
