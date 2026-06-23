"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/my-locality", label: "Locality", icon: "🗺️" },
  { href: "/raise", label: "Raise", icon: "➕" },
  { href: "/my-reports", label: "Reports", icon: "📋" },
];

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="app-shell pb-16">
      {children}
      <nav className="fixed bottom-0 left-1/2 z-20 flex w-full max-w-[480px] -translate-x-1/2 border-t border-slate-200 bg-white">
        {NAV.map((n) => {
          const active = path === n.href || path.startsWith(n.href + "/");
          return (
            <Link
              key={n.href}
              href={n.href}
              className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-xs ${
                active ? "text-brand" : "text-slate-400"
              }`}
            >
              <span className="text-lg">{n.icon}</span>
              {n.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
