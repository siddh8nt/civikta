"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { IssueDetail } from "@/lib/types";
import { SeverityBadge, StatusBadge, VerifiedBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { eventLabel } from "@/lib/labels";

type Screen = "detail" | "escalation";

function payloadString(payload: Record<string, unknown>, key: string): string | null {
  const value = payload[key];
  return typeof value === "string" && value.length > 0 ? value : null;
}

function isPastIsoDate(value: string | null): boolean {
  if (!value) return false;
  const time = new Date(value).getTime();
  return Number.isFinite(time) && time < Date.now();
}

export default function IssueDetailPage({ params }: { params: { id: string } }) {
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [err, setErr] = useState(false);
  const [busy, setBusy] = useState(false);
  const [screen, setScreen] = useState<Screen>("detail");
  const [escalationNote, setEscalationNote] = useState("");
  const [escalationSent, setEscalationSent] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setCurrentUserId(data.user?.id ?? null));
  }, []);

  const load = () => api.issue(params.id).then(setIssue).catch(() => setErr(true));
  useEffect(() => { load(); }, [params.id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function corroborate(body: { still_unresolved?: boolean; affected_too?: boolean }) {
    setBusy(true);
    try {
      await api.corroborate(params.id, body);
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function disputeResolution() {
    setBusy(true);
    try {
      await api.requestEscalation(params.id);
      if (escalationNote.trim()) {
        await api.corroborate(params.id, { still_unresolved: true, note: escalationNote } as Parameters<typeof api.corroborate>[1]);
      }
      setEscalationSent(true);
      await load();
    } finally {
      setBusy(false);
    }
  }

  if (err) return <main className="p-6 text-sm text-rose-500">Issue not found.</main>;
  if (!issue) return <main className="p-6 text-sm text-slate-400">Loading…</main>;

  const status = issue.status;
  const isResolved = status === "resolved";
  const isReopened = status === "reopened";
  const isClosed = (status as string) === "closed";
  const isRejected = status === "rejected";

  // â”€â”€ Escalation screen â”€â”€
  if (screen === "escalation") {
    const slaEstimateDays = 7;
    const filedDaysAgo = Math.floor(
      (Date.now() - new Date(issue.created_at).getTime()) / (1000 * 60 * 60 * 24)
    );
    const slaBreach = filedDaysAgo > slaEstimateDays;

    return (
      <main className="pb-32 p-4 space-y-4">
        <button onClick={() => setScreen("detail")} className="text-sm text-slate-500">← Back</button>

        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4">
          <p className="text-xs font-bold uppercase tracking-widest text-rose-600 mb-1">Escalation Notice</p>
          <h2 className="text-base font-bold text-slate-900">{issue.title}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{issue.locality_name} · Ward {issue.ward_no}</p>
        </div>

        {escalationSent ? (
          <div className="rounded-xl border border-green-200 bg-green-50 p-5 text-center space-y-2">
            <div className="text-3xl">✓</div>
            <p className="font-semibold text-green-800">Escalation submitted</p>
            <p className="text-sm text-green-700">
              Your request has been recorded on the issue timeline. The Vertex AI escalation agent
              will automatically notify the oversight authority if the department misses its deadline.
            </p>
            <button
              onClick={() => setScreen("detail")}
              className="mt-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Back to issue
            </button>
          </div>
        ) : (
          <>
            <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3 text-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Escalation summary</p>
              <EscRow label="Filed" value={`${filedDaysAgo} day${filedDaysAgo !== 1 ? "s" : ""} ago`} />
              <EscRow
                label="SLA status"
                value={slaBreach ? `Breached by ${filedDaysAgo - slaEstimateDays}d` : "Within SLA"}
                highlight={slaBreach ? "red" : "green"}
              />
              <EscRow label="Corroborations" value={String(issue.corroboration_count)} />
              <EscRow label="Urgency score" value={issue.urgency_score.toFixed(1)} />
              <EscRow label="Assigned to" value={authorityLabel(issue.primary_authority_slug)} />
              <EscRow label="Current status" value={status} />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-600">
                Additional details (optional)
              </label>
              <textarea
                value={escalationNote}
                onChange={(e) => setEscalationNote(e.target.value)}
                rows={3}
                placeholder="Describe what is still wrong, or add any update…"
                className="w-full rounded-xl border border-slate-200 p-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-rose-400"
              />
            </div>

            <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[480px] border-t border-slate-200 bg-white p-3 space-y-2">
              <button
                disabled={busy}
                onClick={disputeResolution}
                className="w-full rounded-xl bg-rose-600 py-3 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-40"
              >
                {busy ? "Submitting…" : "Submit escalation to supervisor"}
              </button>
              <button
                onClick={() => setScreen("detail")}
                className="w-full rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-600"
              >
                Cancel
              </button>
            </div>
          </>
        )}
      </main>
    );
  }

  // ── Main detail screen ──
  return (
    <main className="pb-28">
      {issue.media_urls.length > 0 && (
        <ImageCarousel urls={issue.media_urls} />
      )}

      <div className="space-y-5 p-4">
        <div>
          <IssueIdChip id={issue.id} />
          <div className="mb-2 flex flex-wrap gap-1.5">
            <StatusBadge status={issue.status} />
            <SeverityBadge severity={issue.severity} />
            <VerifiedBadge count={issue.corroboration_count} />
          </div>
          <h1 className="text-lg font-bold leading-snug">{issue.title}</h1>
          <p className="mt-1 text-xs text-slate-500">
            {issue.locality_name ?? "Delhi"} · Ward {issue.ward_no ?? "—"} ·{" "}
            {new Date(issue.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Status context banner */}
        {isResolved && (
          <div className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-900">
            <p className="font-semibold">Authority has marked this resolved</p>
            <p className="text-xs mt-0.5 text-green-700">Please confirm if the issue is actually fixed.</p>
          </div>
        )}
        {isReopened && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
            <p className="font-semibold">Issue reopened â€” escalation in progress</p>
            <p className="text-xs mt-0.5 text-rose-700">Supervisor and oversight have been notified.</p>
          </div>
        )}
        {isClosed && (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
            <p className="font-semibold">Issue closed</p>
          </div>
        )}
        {isRejected && (
          <div className="rounded-xl border border-orange-200 bg-orange-50 p-3 text-sm text-orange-900">
            <p className="font-semibold">Issue was rejected by the authority</p>
            {issue.status_reason != null && <p className="text-xs mt-0.5">Reason: {issue.status_reason}</p>}
          </div>
        )}

        {issue.latitude != null && issue.longitude != null && (
          <Section title="Location">
            <div className="overflow-hidden rounded-xl border border-slate-200">
              <iframe
                title="Issue location"
                width="100%"
                height="180"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                src={`https://maps.google.com/maps?q=${issue.latitude},${issue.longitude}&z=17&output=embed`}
                className="block w-full border-0"
              />
            </div>
          </Section>
        )}

        <Section title="Summary">
          <p className="text-sm text-slate-600">{issue.ai_summary ?? issue.public_summary}</p>
        </Section>

        <Section title="Jurisdiction">
          <div className="rounded-lg bg-slate-50 p-3 text-sm">
            {issue.local_body_type && (
              <>
                <Row k="Local body" v={issue.local_body_type} />
                {issue.mcd_zone && (
                  <Row k="Zone" v={issue.mcd_zone} />
                )}
              </>
            )}
            <Row k="Portal" v={issue.primary_authority_slug ? authorityLabel(issue.primary_authority_slug) : "Pending assignment"} />
            {issue.routing_confidence != null && (
              <Row k="Confidence" v={`${(issue.routing_confidence * 100).toFixed(0)}%`} />
            )}
          </div>
        </Section>

        <Section title="Assigned Authority">
          <div className="rounded-lg bg-slate-50 p-3 text-sm">
            <Row k="Responsible body" v={authorityLabel(issue.primary_authority_slug)} />
            {issue.secondary_authority_slug && (
              <Row k="Supporting body" v={authorityLabel(issue.secondary_authority_slug)} />
            )}
          </div>
        </Section>

        <Section title="Community">
          <div className="rounded-lg border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900">
            <p className="font-medium">✓ Reported by {issue.total_report_count} resident{issue.total_report_count !== 1 ? "s" : ""}</p>
            {issue.last_corroborated_at && (
              <p className="text-xs mt-0.5 text-teal-700">
                Last activity {new Date(issue.last_corroborated_at).toLocaleDateString()}
              </p>
            )}
          </div>
        </Section>

        {/* Escalation â€” only for the original reporter after no acknowledgement or a missed deadline */}
        {(() => {
          const isReporter = currentUserId && issue.reporter_id === currentUserId;
          const authorityAcknowledged = issue.timeline.some(
            (e) => e.event_type === "authority_acknowledged"
          );
          const twelveHoursAfterReport =
            Date.now() - new Date(issue.created_at).getTime() >= 12 * 60 * 60 * 1000;
          const missedAuthorityDeadline = issue.timeline.some(
            (e) => e.event_type === "deadline_set" && isPastIsoDate(payloadString(e.payload, "deadline"))
          );
          const canEscalate =
            isReporter &&
            !["resolved", "rejected", "closed"].includes(status) &&
            ((!authorityAcknowledged && twelveHoursAfterReport) || missedAuthorityDeadline);
          if (!canEscalate) return null;
          return (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm">
              <p className="font-semibold text-amber-900">Authority not responding?</p>
              <p className="text-xs text-amber-700 mt-0.5">
                {missedAuthorityDeadline
                  ? "The authority has missed its committed deadline. You can flag this for oversight review."
                  : "No acknowledgement has been made on your report within 12 hours. You can flag this for oversight review."}
              </p>
              <button
                onClick={() => setScreen("escalation")}
                className="mt-2 inline-block rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700"
              >
                Request Oversight Review →
              </button>
            </div>
          );
        })()}

        <Section title="Track Issue Progress">
          <ol className="space-y-2 border-l-2 border-slate-200 pl-4 text-sm">
            {issue.timeline.filter(e => [
                "created","assigned","authority_acknowledged","authority_rejected",
                "field_visit_scheduled","field_visit_completed","repair_scheduled",
                "resolved","reopened","still_unresolved_confirmed",
              ].includes(e.event_type)).map((e, i) => (
              <li key={i} className="relative">
                <span className={`absolute -left-[21px] top-1 h-2 w-2 rounded-full ${
                  e.event_type === "resolved" ? "bg-green-500" :
                  e.event_type === "deadline_set" ? "bg-amber-400" :
                  e.event_type === "escalated_to_oversight" ? "bg-red-500" :
                  e.event_type === "in_progress_update" ? "bg-blue-400" :
                  "bg-slate-400"
                }`} />
                <span className="font-medium text-slate-800">{eventLabel(e.event_type)}</span>
                <span className="ml-2 text-xs text-slate-400">
                  {new Date(e.created_at).toLocaleString()}
                </span>
                {/* Deadline shown to citizens */}
                {e.event_type === "deadline_set" && payloadString(e.payload, "deadline") && (
                  <p className="mt-0.5 text-xs text-amber-700 font-medium">
                    Authority committed to update by: {new Date(String(payloadString(e.payload, "deadline"))).toLocaleString()}
                  </p>
                )}
                {/* In-progress update */}
                {e.event_type === "in_progress_update" && (
                  <div className="mt-1 rounded-lg bg-blue-50 border border-blue-100 p-2 space-y-0.5">
                    {payloadString(e.payload, "title") && <p className="text-xs font-semibold text-blue-800">{payloadString(e.payload, "title")}</p>}
                    {payloadString(e.payload, "description") && <p className="text-xs text-blue-700">{payloadString(e.payload, "description")}</p>}
                    {payloadString(e.payload, "image_data") && (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={`data:image/jpeg;base64,${payloadString(e.payload, "image_data")}`}
                        alt="Authority update photo"
                        className="mt-1 max-h-40 rounded object-cover"
                      />
                    )}
                  </div>
                )}
                {/* Resolution proof photo */}
                {e.event_type === "resolved" && payloadString(e.payload, "proof_image_data") && (
                  <div className="mt-1 space-y-1">
                    <p className="text-xs text-green-700 font-medium">Resolution photo from authority:</p>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`data:image/jpeg;base64,${payloadString(e.payload, "proof_image_data")}`}
                      alt="Resolution proof"
                      className="max-h-40 w-full rounded-lg object-cover"
                    />
                  </div>
                )}
                {e.payload?.status_reason != null && (
                  <p className="mt-0.5 text-xs text-slate-500 italic">"{String(e.payload.status_reason)}"</p>
                )}
              </li>
            ))}
          </ol>
        </Section>
      </div>

      {/* â”€â”€ Bottom action bar â€” changes per status â”€â”€ */}
      <div className="fixed bottom-16 left-1/2 z-20 flex w-full max-w-[480px] -translate-x-1/2 gap-2 border-t border-slate-200 bg-white p-3">

        {/* RESOLVED: confirm or dispute */}
        {isResolved && (
          <>
            <button
              disabled={busy}
              onClick={() => corroborate({ still_unresolved: false })}
              className="flex-1 rounded-xl border border-green-500 py-2.5 text-sm font-semibold text-green-700 hover:bg-green-50 disabled:opacity-40"
            >
              ✓ Issue is fixed
            </button>
            <button
              disabled={busy}
              onClick={() => setScreen("escalation")}
              className="flex-1 rounded-xl bg-rose-600 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-40"
            >
              Still not resolved
            </button>
          </>
        )}

        {/* ACTIVE: corroborate */}
        {["submitted", "assigned", "in_progress", "pending_verification", "manual_review"].includes(status) && (
          <>
            <button
              disabled={busy}
              onClick={() => corroborate({ affected_too: true })}
              className="flex-1 rounded-xl border border-brand py-2.5 text-sm font-semibold text-brand disabled:opacity-40"
            >
              I&apos;m affected too
            </button>
            <button
              disabled={busy}
              onClick={() => corroborate({ still_unresolved: true })}
              className="flex-1 rounded-xl bg-brand py-2.5 text-sm font-semibold text-white disabled:opacity-40"
            >
              Still unresolved
            </button>
          </>
        )}

        {/* REOPENED */}
        {isReopened && (
          <button
            disabled={busy}
            onClick={() => corroborate({ still_unresolved: true })}
            className="flex-1 rounded-xl bg-rose-600 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
          >
            Add more evidence
          </button>
        )}

        {/* CLOSED / REJECTED: no actions */}
        {(isClosed || isRejected) && (
          <div className="flex-1 rounded-xl border border-slate-200 py-2.5 text-center text-sm text-slate-400">
            {isClosed ? "Issue closed" : "Issue rejected"}
          </div>
        )}

      </div>
    </main>
  );
}

function ImageCarousel({ urls }: { urls: string[] }) {
  const [active, setActive] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  function onScroll() {
    if (!ref.current) return;
    const idx = Math.round(ref.current.scrollLeft / ref.current.offsetWidth);
    setActive(idx);
  }

  function goTo(i: number) {
    if (!ref.current) return;
    ref.current.scrollTo({ left: i * ref.current.offsetWidth, behavior: "smooth" });
  }

  return (
    <div className="relative h-52 bg-black">
      <div
        ref={ref}
        onScroll={onScroll}
        className="flex h-full overflow-x-auto snap-x snap-mandatory scrollbar-none"
        style={{ scrollbarWidth: "none" }}
      >
        {urls.map((url, i) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img key={i} src={url} alt="" className="h-full w-full flex-shrink-0 snap-start object-cover" />
        ))}
      </div>
      {urls.length > 1 && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
          {urls.map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i)}
              className={`h-1.5 rounded-full transition-all duration-200 ${i === active ? "w-4 bg-white" : "w-1.5 bg-white/50"}`}
            />
          ))}
        </div>
      )}
      {urls.length > 1 && (
        <div className="absolute top-2 right-2 rounded-full bg-black/40 px-2 py-0.5 text-[10px] font-medium text-white">
          {active + 1}/{urls.length}
        </div>
      )}
    </div>
  );
}

function IssueIdChip({ id }: { id: string }) {
  const short = id.slice(0, 8).toUpperCase();
  return (
    <div className="mb-2 inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-slate-50 px-2 py-1">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">Issue ID</span>
      <span className="font-mono text-xs font-bold text-slate-700">CIV-{short}</span>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</h2>
      {children}
    </section>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3 py-0.5 text-sm">
      <span className="text-slate-400">{k}</span>
      <span className="text-right font-medium">{v}</span>
    </div>
  );
}

function EscRow({ label, value, highlight }: { label: string; value: string; highlight?: "red" | "green" }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-slate-400">{label}</span>
      <span className={`font-medium ${highlight === "red" ? "text-rose-600" : highlight === "green" ? "text-green-600" : "text-slate-700"}`}>
        {value}
      </span>
    </div>
  );
}

