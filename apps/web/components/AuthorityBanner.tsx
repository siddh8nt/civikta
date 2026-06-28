"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAuthorityContext, getAuthorityMeta } from "@/lib/authority-context";
import { IssueSearchBar } from "@/components/IssueSearchBar";

export function AuthorityBanner() {
  const [ctx, setCtx] = useState<{ authority: string; zone: string | null } | null>(null);

  useEffect(() => {
    setCtx(getAuthorityContext());
  }, []);

  if (!ctx) return null;

  const meta = getAuthorityMeta(ctx.authority);
  // Always pass authority+zone so the dashboard never loses context
  const dashParams = new URLSearchParams({ authority: ctx.authority });
  if (ctx.zone) dashParams.set("zone", ctx.zone);
  const dashHref = `/authority/dashboard?${dashParams.toString()}`;

  return (
    <div className={`${meta.headerBg} text-white`}>
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
        {/* Left: identity */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/20 text-[10px] font-bold">
            CV
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs font-bold tracking-wider">CIVIKTA</span>
              <span className="rounded bg-white/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest">
                {meta.name}
              </span>
              {ctx.zone && (
                <span className="rounded bg-white/15 px-2 py-0.5 text-[10px] font-medium">
                  {ctx.zone} Zone
                </span>
              )}
            </div>
            <p className="text-[10px] text-white/60 tracking-wide truncate">
              {meta.full}{ctx.zone ? ` · ${ctx.zone} Zone` : ""} · Authority Portal
            </p>
          </div>
        </div>

        {/* Right: search + nav */}
        <div className="flex shrink-0 items-center gap-2">
          <div className="w-52">
            <IssueSearchBar urlPrefix="/authority/issues" />
          </div>
          <Link
            href={dashHref}
            className="rounded border border-white/20 bg-white/10 px-2.5 py-1.5 text-[11px] font-medium text-white/80 hover:bg-white/20 transition"
          >
            Dashboard
          </Link>
          <Link
            href="/authority/issues"
            className="rounded border border-white/20 bg-white/10 px-2.5 py-1.5 text-[11px] font-medium text-white/80 hover:bg-white/20 transition"
          >
            Queue
          </Link>
          <Link
            href="/authority/portal"
            className="rounded border border-white/20 bg-white/10 px-2.5 py-1.5 text-[11px] font-medium text-white/80 hover:bg-white/20 transition"
          >
            Change Portal
          </Link>
        </div>
      </div>
    </div>
  );
}
