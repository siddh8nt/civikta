import Link from "next/link";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge, StatusBadge, VerifiedBadge } from "./ui/badges";
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
    <Link href={link} className="block overflow-hidden rounded-xl border border-slate-200 bg-white">
      {issue.cover_media_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={issue.cover_media_url} alt="" className="h-40 w-full object-cover" />
      )}
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <StatusBadge status={issue.status} />
          <SeverityBadge severity={issue.severity} />
          <VerifiedBadge count={issue.corroboration_count} />
        </div>
        <h3 className="line-clamp-2 text-sm font-semibold leading-snug">{issue.title}</h3>
        <p className="text-xs text-slate-500">
          {issue.locality_name ?? "Delhi"}
          {issue.distance_m != null && ` · ${Math.round(issue.distance_m)} m away`}
          {" · "}
          {timeAgo(issue.created_at)}
        </p>
        <div className="text-xs text-slate-500">
          <span>{issue.primary_authority_slug ? authorityLabel(issue.primary_authority_slug) : "routing…"}</span>
        </div>
      </div>
    </Link>
  );
}
