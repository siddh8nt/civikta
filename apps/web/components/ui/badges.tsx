import type { IssueStatus, Severity } from "@/lib/types";

const STATUS_STYLES: Record<string, string> = {
  submitted: "bg-slate-100 text-slate-700",
  pending_verification: "bg-amber-100 text-amber-800",
  assigned: "bg-blue-100 text-blue-800",
  in_progress: "bg-indigo-100 text-indigo-800",
  resolved: "bg-emerald-100 text-emerald-800",
  reopened: "bg-rose-100 text-rose-800",
  rejected: "bg-slate-200 text-slate-600",
  manual_review: "bg-purple-100 text-purple-800",
};

const SEVERITY_STYLES: Record<Severity, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

function chip(text: string, cls: string) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {text}
    </span>
  );
}

export function StatusBadge({ status }: { status: IssueStatus | string }) {
  const label = String(status).replace(/_/g, " ");
  return chip(label, STATUS_STYLES[status] || "bg-slate-100 text-slate-700");
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  return chip(severity, SEVERITY_STYLES[severity] || SEVERITY_STYLES.medium);
}

export function VerifiedBadge({ count }: { count: number }) {
  if (count <= 0) return null;
  return chip(`✓ ${count} corroborated`, "bg-teal-100 text-teal-800");
}
