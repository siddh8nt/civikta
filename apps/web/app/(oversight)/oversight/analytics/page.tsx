"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

type ToolCall = {
  name: string;
  args: Record<string, unknown>;
  result: unknown;
};

type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; text: string; tool_calls: ToolCall[]; suggested_questions: string[]; loading?: false }
  | { role: "assistant"; loading: true };

const TOOL_LABELS: Record<string, string> = {
  get_issue_stats:          "Aggregate issue statistics",
  get_issue_detail:         "Issue detail lookup",
  search_issues:            "Advanced issue search",
  get_authority_scorecard:  "Authority scorecard",
  get_authority_comparison: "Multi-authority comparison",
  get_category_breakdown:   "Category breakdown",
  get_ward_health_scores:   "Ward health scores",
  get_zone_comparison:      "Zone comparison",
  get_sla_analysis:         "SLA compliance analysis",
  get_escalation_analysis:  "Escalation & false closure",
  get_stalled_issues:       "Stalled issues audit",
  get_chronic_hotspots:     "Chronic hotspot analysis",
  get_rejection_analysis:   "Rejection analysis",
  get_safety_hazard_report: "Safety hazard report",
  get_unrouted_issues:      "Routing gap analysis",
  get_citizen_engagement:          "Citizen engagement metrics",
  get_trend_analysis:              "Trend analysis",
  get_commissioner_accountability: "Commissioner accountability audit",
};

const SUGGESTED_QUERIES = [
  "Which authority has the worst SLA compliance?",
  "Audit MCD Engineering's performance",
  "Generate a ward health report for South Zone",
  "What are the most critical open issues in Delhi?",
  "Which wards have the highest false closure rate?",
  "Identify systemic waterlogging issues and recommend interventions",
  "Compare MCD Sanitation vs NDMC Sanitation performance",
  "Generate a state-wide civic audit report",
  "Which MCD commissioner has the worst SLA record?",
  "Audit Pankaj Agrawal's zones for false closures",
];

export default function AnalyticsChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    if (!question.trim() || busy) return;
    const q = question.trim();
    setInput("");
    setBusy(true);

    // Capture history before adding the new messages (last 3 exchanges = 6 turns)
    setMessages((prev) => {
      type FullMsg = { role: "user"; text: string } | { role: "assistant"; text: string; tool_calls: ToolCall[]; suggested_questions: string[] };
      const history = (prev.filter((m): m is FullMsg =>
        m.role === "user" || (m.role === "assistant" && !("loading" in m) && "text" in m)
      ) as FullMsg[])
        .slice(-6)
        .map((m) => ({ role: m.role as "user" | "assistant", text: m.text }));

      api.analyticsQuery(q, {}, history)
        .then((result) => {
          setMessages((m) => [
            ...m.slice(0, -1),
            { role: "assistant", text: result.answer, tool_calls: result.tool_calls, suggested_questions: result.suggested_questions ?? [] },
          ]);
        })
        .catch((err: unknown) => {
          const msg = err instanceof Error ? err.message : String(err);
          setMessages((m) => [
            ...m.slice(0, -1),
            { role: "assistant", text: `Error: ${msg}`, tool_calls: [], suggested_questions: [] },
          ]);
        })
        .finally(() => setBusy(false));

      return [...prev, { role: "user" as const, text: q }, { role: "assistant" as const, loading: true as const }];
    });
  }

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-screen flex-col bg-slate-50">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-6 py-3 flex items-center justify-between shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-slate-900">CIVIKTA Analytics</span>
            <span className="rounded bg-violet-100 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-violet-700">
              Gemini Agent
            </span>
          </div>
          <p className="text-[10px] text-slate-400">State-wide civic intelligence · Policy & audit analysis</p>
        </div>
        <Link href="/oversight/dashboard" className="text-xs text-slate-500 hover:text-slate-700">
          ← Dashboard
        </Link>
      </header>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {!hasMessages && (
          <div className="mx-auto max-w-2xl">
            <div className="mb-8 text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100">
                <svg className="h-7 w-7 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z" />
                </svg>
              </div>
              <h2 className="text-lg font-bold text-slate-900">Oversight Intelligence Agent</h2>
              <p className="mt-1 text-sm text-slate-500 max-w-md mx-auto">
                Ask any governance question. The agent queries live issue data across all 14 authorities,
                250 wards, and 12 MCD zones — then synthesizes findings with policy recommendations.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {SUGGESTED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-700 hover:border-violet-300 hover:bg-violet-50 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "user" ? (
              <div className="max-w-xl rounded-2xl bg-violet-600 px-4 py-3 text-sm text-white">
                {msg.text}
              </div>
            ) : msg.loading ? (
              <AssistantLoading />
            ) : (
              <AssistantMessage
                text={msg.text}
                tool_calls={msg.tool_calls}
                suggested_questions={msg.suggested_questions}
                question={(() => { const prev = messages[i - 1]; return prev?.role === "user" ? prev.text : undefined; })()}
                onSuggest={send}
              />
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-slate-200 bg-white px-4 py-3 shrink-0">
        <div className="mx-auto flex max-w-3xl gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
            disabled={busy}
            placeholder="Ask about any authority, ward, zone, or issue type…"
            className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-violet-400 focus:outline-none focus:ring-1 focus:ring-violet-400 disabled:opacity-50"
          />
          <button
            disabled={busy || !input.trim()}
            onClick={() => send(input)}
            className="rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-40 transition"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}

function AssistantLoading() {
  return (
    <div className="max-w-2xl rounded-2xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <div className="flex gap-1">
          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:0ms]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:150ms]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:300ms]" />
        </div>
        <span>Querying live data…</span>
      </div>
    </div>
  );
}

function openReport(question: string, text: string, tool_calls: ToolCall[]) {
  const timestamp = new Date().toLocaleString("en-IN", { dateStyle: "long", timeStyle: "short" });
  const uniqueTools = [...new Set(tool_calls.map(t => TOOL_LABELS[t.name] ?? t.name))];
  const toolsSummary = tool_calls.length > 0
    ? `<p style="margin:0 0 4px 0;font-size:11px;color:#6d28d9;font-weight:600;">Data sources queried (${tool_calls.length})</p>
       <p style="margin:0;font-size:11px;color:#7c3aed;">${uniqueTools.join(" · ")}</p>`
    : "";

  const bodyHtml = parseBlocks(text).map(b => {
    if (b.kind === "table") {
      const thead = `<thead><tr>${b.headers.map(h => `<th>${inlineHtml(h)}</th>`).join("")}</tr></thead>`;
      const tbody = `<tbody>${b.rows.map((row, ri) =>
        `<tr class="${ri % 2 === 0 ? "tr-even" : "tr-odd"}">${row.map(cell => `<td>${inlineHtml(cell)}</td>`).join("")}</tr>`
      ).join("")}</tbody>`;
      return `<div class="tbl-wrap"><table class="data-table">${thead}${tbody}</table></div>`;
    }
    if (b.kind === "h1")    return `<h1>${inlineHtml(b.text)}</h1>`;
    if (b.kind === "h2")    return `<h2>${inlineHtml(b.text)}</h2>`;
    if (b.kind === "h3")    return `<h3>${inlineHtml(b.text)}</h3>`;
    if (b.kind === "li")    return `<li>${inlineHtml(b.text)}</li>`;
    if (b.kind === "empty") return `<br>`;
    return `<p>${inlineHtml(b.text)}</p>`;
  }).join("\n");

  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CIVIKTA Report — ${esc(question.slice(0, 60))}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; background: #f8fafc; font-size: 13px; line-height: 1.7; }

  /* ── Top nav bar ─────────────────────────────── */
  .topbar {
    position: sticky; top: 0; z-index: 100;
    background: #fff; border-bottom: 1px solid #e2e8f0;
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 32px; gap: 12px;
  }
  .topbar-left { display: flex; align-items: center; gap: 10px; }
  .back-btn {
    display: flex; align-items: center; gap-6px; gap: 6px;
    padding: 6px 12px; border-radius: 8px; border: 1px solid #e2e8f0;
    background: #f8fafc; color: #475569; font-size: 12px; font-weight: 500;
    cursor: pointer; text-decoration: none; transition: all .15s;
  }
  .back-btn:hover { border-color: #c4b5fd; background: #f5f3ff; color: #7c3aed; }
  .topbar-title { font-size: 13px; font-weight: 600; color: #64748b; }
  .pdf-btn {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 8px; border: none;
    background: #7c3aed; color: #fff; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: background .15s;
  }
  .pdf-btn:hover { background: #6d28d9; }

  /* ── Report content ──────────────────────────── */
  .page { max-width: 820px; margin: 32px auto; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 40px 48px; }
  .report-header { display: flex; align-items: flex-start; justify-content: space-between; border-bottom: 2px solid #7c3aed; padding-bottom: 16px; margin-bottom: 24px; }
  .brand { font-size: 20px; font-weight: 800; color: #7c3aed; letter-spacing: -0.5px; }
  .brand span { color: #1e293b; }
  .meta { text-align: right; font-size: 11px; color: #64748b; line-height: 1.6; }
  .question-box { background: #f5f3ff; border-left: 3px solid #7c3aed; padding: 10px 14px; margin-bottom: 20px; border-radius: 0 6px 6px 0; }
  .question-label { font-size: 10px; font-weight: 700; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; }
  .question-text { font-size: 13px; font-weight: 600; color: #1e293b; }
  .tools-box { background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 6px; padding: 10px 14px; margin-bottom: 20px; }
  .body h1 { font-size: 16px; font-weight: 700; color: #0f172a; margin: 20px 0 8px; }
  .body h2 { font-size: 14px; font-weight: 700; color: #1e293b; margin: 16px 0 6px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
  .body h3 { font-size: 13px; font-weight: 700; color: #334155; margin: 14px 0 4px; }
  .body p { margin: 4px 0; color: #334155; }
  .body li { margin: 3px 0 3px 18px; color: #334155; }
  .body strong { font-weight: 700; color: #0f172a; }
  .body br { display: block; margin: 4px 0; }
  .tbl-wrap { overflow-x: auto; margin: 14px 0; border-radius: 6px; border: 1px solid #e2e8f0; }
  .data-table { width: 100%; border-collapse: collapse; font-size: 11.5px; }
  .data-table thead tr { background: #f5f3ff; }
  .data-table th { padding: 8px 12px; text-align: left; font-weight: 700; color: #6d28d9; border-bottom: 2px solid #ddd6fe; white-space: nowrap; }
  .data-table td { padding: 6px 12px; color: #334155; border-bottom: 1px solid #f1f5f9; }
  .data-table .tr-even { background: #fff; }
  .data-table .tr-odd  { background: #f8fafc; }
  .report-footer { margin-top: 32px; padding-top: 12px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; }

  @media print {
    .topbar { display: none; }
    body { background: #fff; }
    .page { margin: 0; border: none; border-radius: 0; padding: 24px 32px; box-shadow: none; }
    @page { margin: 1.5cm 1.8cm; size: A4; }
    h2, h3 { page-break-after: avoid; }
    .question-box, .tools-box, .tbl-wrap { page-break-inside: avoid; }
    .data-table th { background: #f5f3ff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .data-table .tr-odd { background: #f8fafc !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head><body>

<div class="topbar">
  <div class="topbar-left">
    <a class="back-btn" onclick="window.opener ? window.close() : window.history.back(); return false;" href="#">
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"/></svg>
      Back to Chat
    </a>
    <span class="topbar-title">Oversight Intelligence Report</span>
  </div>
  <button class="pdf-btn" onclick="window.print()">
    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
    Export PDF
  </button>
</div>

<div class="page">
  <div class="report-header">
    <div>
      <div class="brand">CIVIKTA<span> Analytics</span></div>
      <div style="font-size:11px;color:#7c3aed;margin-top:2px;">Oversight Intelligence Report</div>
    </div>
    <div class="meta">Generated: ${timestamp}<br>NCT Delhi · Civic Issue Platform<br>Powered by Gemini on Vertex AI</div>
  </div>
  <div class="question-box">
    <div class="question-label">Query</div>
    <div class="question-text">${esc(question)}</div>
  </div>
  ${toolsSummary ? `<div class="tools-box">${toolsSummary}</div>` : ""}
  <div class="body">${bodyHtml}</div>
  <div class="report-footer">
    <span>CIVIKTA · Citizen Civic Transparency Platform</span>
    <span>Confidential — Oversight Use Only</span>
  </div>
</div>
</body></html>`;

  const w = window.open("", "_blank");
  if (w) { w.document.write(html); w.document.close(); }
}

function esc(s: string) {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function inlineHtml(text: string) {
  return esc(text).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function AssistantMessage({ text, tool_calls, suggested_questions, question, onSuggest }: {
  text: string;
  tool_calls: ToolCall[];
  suggested_questions: string[];
  question?: string;
  onSuggest: (q: string) => void;
}) {
  const [showTools, setShowTools] = useState(false);

  return (
    <div className="max-w-2xl w-full space-y-2">
      {/* Tool calls summary — always visible when present */}
      {tool_calls.length > 0 && (
        <div className="rounded-xl border border-violet-100 bg-violet-50 px-3 py-2">
          <button
            onClick={() => setShowTools((v) => !v)}
            className="flex w-full items-center justify-between text-xs font-semibold text-violet-700"
          >
            <span className="flex items-center gap-1.5">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
              </svg>
              {tool_calls.length} tool{tool_calls.length !== 1 ? "s" : ""} called
            </span>
            <span>{showTools ? "▲ Hide" : "▼ Show"}</span>
          </button>

          {showTools && (
            <div className="mt-2 space-y-2">
              {tool_calls.map((tc, i) => (
                <div key={i} className="rounded-lg border border-violet-200 bg-white p-2.5 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-violet-800">
                      {TOOL_LABELS[tc.name] ?? tc.name}
                    </span>
                    <span className="rounded bg-violet-100 px-1.5 py-0.5 text-[10px] font-mono text-violet-600">
                      {tc.name}
                    </span>
                  </div>
                  {Object.keys(tc.args).length > 0 && (
                    <div className="mb-1 text-slate-500">
                      Args: {Object.entries(tc.args)
                        .filter(([, v]) => v != null && v !== "")
                        .map(([k, v]) => `${k}=${String(v)}`)
                        .join(", ") || "none"}
                    </div>
                  )}
                  <details className="text-slate-400">
                    <summary className="cursor-pointer hover:text-slate-600">View result</summary>
                    <pre className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap break-all text-[10px] text-slate-500">
                      {JSON.stringify(tc.result, null, 2)}
                    </pre>
                  </details>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main answer */}
      <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4">
        <MarkdownText text={text} />
        {text && !text.startsWith("Error:") && (
          <div className="mt-4 flex justify-end border-t border-slate-100 pt-3">
            <button
              onClick={() => openReport(question ?? "Oversight Report", text, tool_calls)}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-violet-300 hover:bg-violet-50 hover:text-violet-700 transition"
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
              </svg>
              Expand
            </button>
          </div>
        )}
      </div>

      {/* Suggested follow-up pills */}
      {suggested_questions.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1 pl-1">
          {suggested_questions.map((q, i) => (
            <button
              key={i}
              onClick={() => onSuggest(q)}
              className="flex items-center gap-1.5 rounded-full border border-violet-200 bg-white px-3 py-1.5 text-xs text-violet-700 shadow-sm hover:border-violet-400 hover:bg-violet-50 hover:shadow transition-all"
            >
              <svg className="h-3 w-3 shrink-0 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
              </svg>
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Markdown block parser ─────────────────────────────────────────────────────
type MdBlock =
  | { kind: "h1" | "h2" | "h3" | "li" | "p" | "empty"; text: string }
  | { kind: "table"; headers: string[]; rows: string[][] };

function isTableSep(line: string) {
  return /^\|[\s|:\-]+\|$/.test(line.trim());
}
function parseTableRow(line: string): string[] {
  return line.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim());
}
function parseBlocks(text: string): MdBlock[] {
  const lines = text.split("\n");
  const blocks: MdBlock[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const tr = line.trim();
    if (tr.startsWith("|") && tr.endsWith("|") && i + 1 < lines.length && isTableSep(lines[i + 1])) {
      const headers = parseTableRow(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) {
        rows.push(parseTableRow(lines[i]));
        i++;
      }
      blocks.push({ kind: "table", headers, rows });
      continue;
    }
    if (line.startsWith("### "))                         blocks.push({ kind: "h3",    text: line.slice(4) });
    else if (line.startsWith("## "))                     blocks.push({ kind: "h2",    text: line.slice(3) });
    else if (line.startsWith("# "))                      blocks.push({ kind: "h1",    text: line.slice(2) });
    else if (line.startsWith("- ") || line.startsWith("* ")) blocks.push({ kind: "li", text: line.slice(2) });
    else if (tr === "")                                  blocks.push({ kind: "empty", text: "" });
    else                                                 blocks.push({ kind: "p",     text: line });
    i++;
  }
  return blocks;
}

function renderInline(text: string): React.ReactNode {
  return text.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith("**") && p.endsWith("**")
      ? <strong key={i} className="font-semibold text-slate-900">{p.slice(2, -2)}</strong>
      : p
  );
}

function MarkdownText({ text }: { text: string }) {
  const blocks = parseBlocks(text);
  return (
    <div className="space-y-1 text-sm text-slate-800">
      {blocks.map((b, i) => {
        if (b.kind === "table") return (
          <div key={i} className="my-3 overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full border-collapse text-xs">
              <thead>
                <tr className="bg-violet-50">
                  {b.headers.map((h, j) => (
                    <th key={j} className="border-b border-slate-200 px-3 py-2 text-left font-semibold text-violet-800 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {b.rows.map((row, j) => (
                  <tr key={j} className={j % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                    {row.map((cell, k) => (
                      <td key={k} className="border-b border-slate-100 px-3 py-1.5 text-slate-700">
                        {renderInline(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        if (b.kind === "h1") return <h1 key={i} className="mt-4 text-lg font-bold text-slate-900">{renderInline(b.text)}</h1>;
        if (b.kind === "h2") return <h2 key={i} className="mt-4 text-base font-bold text-slate-900">{renderInline(b.text)}</h2>;
        if (b.kind === "h3") return <h3 key={i} className="mt-3 font-bold text-slate-900">{renderInline(b.text)}</h3>;
        if (b.kind === "li") return (
          <div key={i} className="flex gap-2">
            <span className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
            <span>{renderInline(b.text)}</span>
          </div>
        );
        if (b.kind === "empty") return <div key={i} className="h-2" />;
        return <p key={i}>{renderInline(b.text)}</p>;
      })}
    </div>
  );
}
