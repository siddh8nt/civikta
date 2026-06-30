"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { IssueSummary } from "@/lib/types";
import { SeverityBadge } from "@/components/ui/badges";
import { authorityLabel } from "@/lib/authorities";
import { OversightBanner } from "@/components/OversightBanner";

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diff / 3600000);
  if (hrs < 1) return "< 1h ago";
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// Officials derived from delhi_wards.py ZONE_COMMISSIONERS
const ZONE_OFFICIALS: Record<string, { name: string; title: string; email: string }> = {
  "Narela":         { name: "Sachin Shinde",         title: "Additional Commissioner (Narela / West / Najafgarh), MCD", email: "sachin.shinde@mcd.delhi.gov.in" },
  "West":           { name: "Sachin Shinde",         title: "Additional Commissioner (Narela / West / Najafgarh), MCD", email: "sachin.shinde@mcd.delhi.gov.in" },
  "Najafgarh":      { name: "Sachin Shinde",         title: "Additional Commissioner (Narela / West / Najafgarh), MCD", email: "sachin.shinde@mcd.delhi.gov.in" },
  "South":          { name: "Jitender Yadav",        title: "Additional Commissioner (South / City / Centre), MCD",    email: "jitender.yadav@mcd.delhi.gov.in" },
  "City":           { name: "Jitender Yadav",        title: "Additional Commissioner (South / City / Centre), MCD",    email: "jitender.yadav@mcd.delhi.gov.in" },
  "Centre":         { name: "Jitender Yadav",        title: "Additional Commissioner (South / City / Centre), MCD",    email: "jitender.yadav@mcd.delhi.gov.in" },
  "Keshavpuram":    { name: "Nidhi Malik",           title: "Additional Commissioner (Keshavpuram / Rohini), MCD",     email: "nidhi.malik@mcd.delhi.gov.in" },
  "Rohini":         { name: "Nidhi Malik",           title: "Additional Commissioner (Keshavpuram / Rohini), MCD",     email: "nidhi.malik@mcd.delhi.gov.in" },
  "Civil Lines":    { name: "Dr. Tariq Thomas",      title: "Additional Commissioner (Civil Lines / Karol Bagh), MCD", email: "tariq.thomas@mcd.delhi.gov.in" },
  "Karol Bagh":     { name: "Dr. Tariq Thomas",      title: "Additional Commissioner (Civil Lines / Karol Bagh), MCD", email: "tariq.thomas@mcd.delhi.gov.in" },
  "Shahdara South": { name: "Pankaj Naresh Agrawal", title: "Additional Commissioner (Shahdara), MCD",                email: "pankaj.agrawal@mcd.delhi.gov.in" },
  "Shahdara North": { name: "Pankaj Naresh Agrawal", title: "Additional Commissioner (Shahdara), MCD",                email: "pankaj.agrawal@mcd.delhi.gov.in" },
  "SP-City":        { name: "Jitender Yadav",        title: "Additional Commissioner (South / City), MCD",             email: "jitender.yadav@mcd.delhi.gov.in" },
  "NDMC":           { name: "Keshav Chandra",        title: "Chairman, New Delhi Municipal Council",                   email: "chairman@ndmc.gov.in" },
  "DCB":            { name: "Kapil Goyal",            title: "CEO, Delhi Cantonment Board",                            email: "ceo@delhicantonment.gov.in" },
};

const AUTHORITY_OFFICIALS: Record<string, { name: string; title: string; email: string }> = {
  djb:          { name: "Commissioner, DJB",         title: "Delhi Jal Board",                       email: "ceo@delhijalboard.nic.in" },
  pwd:          { name: "Secretary, PWD Delhi",      title: "Public Works Department, GNCT Delhi",   email: "secy-pwd@nic.in" },
  ifcd:         { name: "Chief Engineer, IFCD",      title: "Irrigation & Flood Control Dept.",      email: "ce-ifcd@delhi.gov.in" },
  dda:          { name: "Vice Chairman, DDA",        title: "Delhi Development Authority",           email: "vc@dda.org.in" },
  delhi_police: { name: "Commissioner of Police",    title: "Delhi Police",                          email: "cp-delhi@nic.in" },
  nhai:         { name: "Regional Officer, NHAI",    title: "National Highways Authority of India",  email: "ro-delhi@nhai.org" },
};

function getOfficial(issue: IssueSummary) {
  if (issue.mcd_zone && ZONE_OFFICIALS[issue.mcd_zone]) return ZONE_OFFICIALS[issue.mcd_zone];
  const slug = issue.primary_authority_slug ?? "";
  const base = slug.split("_")[0];
  if (AUTHORITY_OFFICIALS[slug]) return AUTHORITY_OFFICIALS[slug];
  if (AUTHORITY_OFFICIALS[base]) return AUTHORITY_OFFICIALS[base];
  if (slug.startsWith("mcd")) return ZONE_OFFICIALS["South"]; // fallback MCD commissioner
  if (slug.startsWith("ndmc")) return ZONE_OFFICIALS["NDMC"];
  if (slug.startsWith("dcb")) return ZONE_OFFICIALS["DCB"];
  return null;
}

function buildEmailBody(issue: IssueSummary, tab: string) {
  const short = `CIV-${issue.id.slice(0, 8).toUpperCase()}`;
  const type = tab === "deadline" ? "Deadline Breach — No Authority Action" : "Disputed Resolution — Citizens Report Issue Unresolved";
  return `Subject: Escalation Notice — ${type} [${short}]

Dear Sir/Madam,

This is a formal escalation notice generated by the Civikta Civic Issue Management System on behalf of the NCT Delhi Oversight Authority.

Issue ID: ${short}
Title: ${issue.title ?? "Civic issue"}
Location: ${[issue.locality_name, issue.ward_name, issue.mcd_zone ? issue.mcd_zone + " Zone" : null].filter(Boolean).join(", ") || "Delhi"}
Assigned Authority: ${authorityLabel(issue.primary_authority_slug)}
Urgency Score: ${issue.urgency_score.toFixed(1)}
Reported: ${new Date(issue.created_at).toLocaleString("en-IN")}

Escalation Reason:
${tab === "deadline"
  ? "This issue has been in 'Submitted' status for over 1 hour with no action recorded by the assigned authority. This constitutes a breach of the mandated response SLA."
  : `This issue was marked as resolved by the assigned authority, but ${issue.corroboration_count} citizens have subsequently reported it as still unresolved — indicating a potential false resolution.`}

You are requested to:
1. Immediately review the status of this issue
2. Ensure the responsible field officer takes corrective action within 2 hours
3. Provide an explanation for the delay/false resolution to the oversight authority

This notice is being sent to you as the jurisdictionally responsible official based on the issue's geographic location. Non-response within 2 hours will result in escalation to the Chief Secretary, GNCT Delhi.

Reference: Civikta Oversight Portal — ${new Date().toLocaleString("en-IN")}

Regards,
Civikta Automated Oversight System
National Capital Territory of Delhi`;
}

type NotifyState = { issue: IssueSummary; tab: "deadline" | "false_resolved" } | null;

export default function OversightEscalationsPage() {
  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"deadline" | "false_resolved">("deadline");
  const [notify, setNotify] = useState<NotifyState>(null);
  const [sent, setSent] = useState<Set<string>>(new Set());

  useEffect(() => {
    api.authorityEscalations()
      .then(setIssues)
      .catch(() => setIssues([]))
      .finally(() => setLoading(false));
  }, []);

  const deadlineBreaches = issues.filter((i) => i.status === "submitted");
  const falseResolved = issues.filter((i) => i.status === "resolved");
  const shown = tab === "deadline" ? deadlineBreaches : falseResolved;

  function handleSend() {
    if (!notify) return;
    setSent((s) => new Set([...s, notify.issue.id]));
    setNotify(null);
  }

  return (
    <>
    <OversightBanner />
    <main className="dashboard-shell space-y-6 pt-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-800">Citizen Escalations</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Automated escalations via Vertex AI agent · Issues requiring oversight intervention
        </p>
      </div>

      {/* AI Agent notice */}
      <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4 flex items-start gap-3">
        <div className="shrink-0 mt-0.5 h-8 w-8 rounded-full bg-indigo-700 flex items-center justify-center text-white text-xs font-bold">AI</div>
        <div>
          <p className="text-sm font-semibold text-indigo-950">Vertex AI Escalation Agent</p>
          <p className="text-xs text-indigo-800 mt-0.5">
            Continuously monitors all active issues. Automatically flags to oversight when an authority has not acted within the set deadline, or a resolved issue is disputed by a significant number of citizens.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex rounded-xl border border-slate-200 bg-white p-1 w-fit gap-1">
        {(["deadline", "false_resolved"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
              tab === t
                ? t === "deadline" ? "bg-rose-700 text-white shadow-sm" : "bg-amber-700 text-white shadow-sm"
                : "text-slate-500 hover:bg-slate-50"
            }`}
          >
            {t === "deadline" ? "Deadline Breaches" : "Disputed Resolutions"}
            {!loading && (
              <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
                tab === t ? "bg-white/20 text-white" : t === "deadline" ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-800"
              }`}>
                {t === "deadline" ? deadlineBreaches.length : falseResolved.length}
              </span>
            )}
          </button>
        ))}
      </div>

      <p className="text-xs text-slate-400">
        {tab === "deadline"
          ? "Issues in 'submitted' status with no authority action for >1 hour."
          : "Issues marked resolved but disputed by ≥100 citizens via 'Still not resolved'."}
      </p>

      {/* Issue list */}
      {loading ? (
        <p className="py-10 text-center text-sm text-slate-400">Loading escalations…</p>
      ) : shown.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 py-12 text-center">
          <p className="text-sm font-medium text-slate-500">
            {tab === "deadline" ? "No deadline breaches — all authorities are on track." : "No disputed resolutions — citizens are satisfied."}
          </p>
          <p className="mt-1 text-xs text-slate-400">Vertex AI agent will alert here when escalations occur.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {shown.map((issue) => {
            const official = getOfficial(issue);
            const wasSent = sent.has(issue.id);
            return (
              <div
                key={issue.id}
                className={`rounded-xl border bg-white p-4 text-sm ${
                  tab === "deadline" ? "border-rose-200" : "border-amber-200"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <Link href={`/oversight/issues/${issue.id}`} className="min-w-0 flex-1 hover:underline">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${
                        tab === "deadline" ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-800"
                      }`}>
                        {tab === "deadline" ? "No action taken" : "Disputed resolution"}
                      </span>
                      <SeverityBadge severity={issue.severity} />
                    </div>
                    <p className="font-semibold text-slate-800 truncate">{issue.title ?? "Untitled issue"}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {issue.locality_name} · {authorityLabel(issue.primary_authority_slug)}
                      {issue.mcd_zone ? ` · ${issue.mcd_zone} Zone` : ""}
                    </p>
                    {tab === "false_resolved" && (
                      <p className="text-xs text-amber-700 mt-0.5 font-medium">
                        {issue.corroboration_count} citizens reported still unresolved
                      </p>
                    )}
                  </Link>
                  <div className="shrink-0 flex flex-col items-end gap-2">
                    <p className="text-xs text-slate-400">{timeAgo(issue.created_at)}</p>
                    <p className="text-xs font-semibold text-slate-600">{issue.urgency_score.toFixed(1)} urgency</p>
                    {official ? (
                      wasSent ? (
                        <span className="rounded-lg bg-green-100 px-2.5 py-1 text-[10px] font-bold text-green-700">
                          ✓ Notice sent
                        </span>
                      ) : (
                        <button
                          onClick={() => setNotify({ issue, tab })}
                          className="rounded-lg bg-slate-800 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-slate-700 transition"
                        >
                          Notify Official
                        </button>
                      )
                    ) : (
                      <span className="text-[10px] text-slate-400">No official mapped</span>
                    )}
                  </div>
                </div>
                {official && (
                  <div className="mt-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-[11px] text-slate-500 flex items-center gap-2">
                    <span className="font-semibold text-slate-700">{official.name}</span>
                    <span>·</span>
                    <span>{official.title}</span>
                    <span>·</span>
                    <span className="font-mono text-slate-400">{official.email}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Notify popup */}
      {notify && (() => {
        const official = getOfficial(notify.issue)!;
        const body = buildEmailBody(notify.issue, notify.tab);
        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setNotify(null)}>
            <div className="w-full max-w-2xl rounded-2xl bg-white shadow-2xl" onClick={(e) => e.stopPropagation()}>
              {/* Modal header */}
              <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-rose-700">Official Notice</p>
                  <h2 className="text-base font-bold text-slate-900">Report to Jurisdictional Official</h2>
                </div>
                <button onClick={() => setNotify(null)} className="text-slate-400 hover:text-slate-600 text-xl leading-none">×</button>
              </div>

              <div className="px-6 py-4 space-y-4">
                {/* To / official */}
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-1 text-sm">
                  <div className="flex gap-3">
                    <span className="w-10 text-xs font-bold uppercase tracking-wide text-slate-400">To</span>
                    <span className="font-semibold text-slate-800">{official.name}</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="w-10 text-xs font-bold uppercase tracking-wide text-slate-400">Role</span>
                    <span className="text-slate-600">{official.title}</span>
                  </div>
                  <div className="flex gap-3">
                    <span className="w-10 text-xs font-bold uppercase tracking-wide text-slate-400">Email</span>
                    <span className="font-mono text-slate-700">{official.email}</span>
                  </div>
                </div>

                {/* Email body preview */}
                <div>
                  <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Email content (auto-generated)</p>
                  <textarea
                    readOnly
                    value={body}
                    rows={12}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 font-mono text-[11px] text-slate-600 leading-relaxed resize-none focus:outline-none"
                  />
                </div>

                <p className="text-[11px] text-slate-400">
                  This is a mock interface — in production, this would trigger an official email via the GNCT Delhi government mail server.
                </p>
              </div>

              <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-4">
                <button onClick={() => setNotify(null)} className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">
                  Cancel
                </button>
                <button
                  onClick={handleSend}
                  className="rounded-xl bg-rose-700 px-5 py-2 text-sm font-bold text-white hover:bg-rose-800 transition"
                >
                  Send Notice →
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </main>
    </>
  );
}
