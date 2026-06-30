import Link from "next/link";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge, StatusBadge } from "./ui/badges";
import { authorityLabel } from "@/lib/authorities";

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3.6e6);
  if (h < 1) return "just now";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function IssueCard({ issue, href }: { issue: IssueSummary; href?: string }) {
  const link = href ?? `/issues/${issue.id}`;
  return (
    <Link href={link} className="flex gap-2.5 overflow-hidden rounded-xl border border-slate-200 bg-paper p-2">
      {issue.cover_media_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={issue.cover_media_url} alt="" loading="lazy" className="h-16 w-16 shrink-0 rounded-lg object-cover" />
      ) : (
        <div className="h-16 w-16 shrink-0 rounded-lg bg-slate-100" />
      )}
      <div className="min-w-0 flex-1 space-y-1 py-0.5">
        <div className="flex flex-wrap items-center gap-1">
          <StatusBadge status={issue.status} />
          <SeverityBadge severity={issue.severity} />
        </div>
        <h3 className="line-clamp-1 text-sm font-semibold leading-snug">{issue.title}</h3>
        <p className="truncate text-xs text-slate-500">
          {issue.locality_name ?? "Delhi"}
          {issue.distance_m != null && ` · ${Math.round(issue.distance_m)}m`}
          {" · "}
          {timeAgo(issue.created_at)}
          {issue.corroboration_count > 0 && ` · ✓${issue.corroboration_count}`}
        </p>
        <p className="truncate text-xs text-slate-500">
          {issue.primary_authority_slug ? authorityLabel(issue.primary_authority_slug) : "routing…"}
        </p>
      </div>
    </Link>
  );
}
