"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import type { AnalyzeResult } from "@/lib/types";
import { LocationStep } from "@/components/LocationStep";

const CATEGORIES = [
  "Roads & Streets",
  "Water / Sewer / Drainage",
  "Garbage & Sanitation",
  "Lights / Electrical",
  "Public Safety Hazard",
  "Parks / Public Space",
  "Animals / Other",
];

type Step = "evidence" | "location" | "category" | "analyzing" | "review" | "verify" | "done";

export default function RaisePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("evidence");
  const [description, setDescription] = useState("");
  const [mediaUrls, setMediaUrls] = useState<string[]>([]);
  const [loc, setLoc] = useState({ lat: 28.5677, lng: 77.2433 });
  const [, setCategory] = useState<string | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);

  // Firebase Storage upload goes here; for the demo we attach a sample image URL.
  const addPhoto = () =>
    setMediaUrls((m) => [...m, `https://picsum.photos/seed/u${Date.now()}/800/600`]);

  async function runAnalysis() {
    setBusy(true);
    setStep("analyzing");
    try {
      const draft = await api.createDraft({
        raw_description: description,
        latitude: loc.lat,
        longitude: loc.lng,
        media_urls: mediaUrls,
      });
      setReportId(draft.report_id);
      const res = await api.analyze(draft.report_id);
      setResult(res);
      setStep(res.duplicates.has_candidate ? "verify" : "review");
    } catch {
      alert("Analysis failed — is the backend running on :8000?");
      setStep("category");
    } finally {
      setBusy(false);
    }
  }

  async function finalize(corroborate: boolean) {
    if (!reportId) return;
    setBusy(true);
    try {
      const res = await api.submit(reportId, {
        corroborate,
        target_issue_id: corroborate ? result?.duplicates.best_candidate?.issue_id : undefined,
      });
      router.push(`/issues/${res.issue_id}`);
    } catch {
      alert("Submit failed.");
      setBusy(false);
    }
  }

  return (
    <main className="p-4 pb-24">
      <h1 className="mb-4 text-lg font-bold text-brand">Raise an Issue</h1>

      {step === "evidence" && (
        <section className="space-y-4">
          <p className="text-sm text-slate-500">Step 1 · Capture evidence</p>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            placeholder="Describe the issue (e.g. sewer overflowing in the lane for 3 days)…"
            className="w-full rounded-lg border border-slate-300 p-3 text-sm"
          />
          <div className="flex flex-wrap gap-2">
            {mediaUrls.map((u) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={u} src={u} alt="" className="h-16 w-16 rounded-lg object-cover" />
            ))}
            <button
              onClick={addPhoto}
              className="h-16 w-16 rounded-lg border-2 border-dashed border-slate-300 text-2xl text-slate-400"
            >
              +
            </button>
          </div>
          <button
            disabled={!description}
            onClick={() => setStep("location")}
            className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white disabled:opacity-40"
          >
            Next
          </button>
        </section>
      )}

      {step === "location" && (
        <section className="space-y-4">
          <p className="text-sm text-slate-500">Step 2 · Confirm location</p>
          <LocationStep value={loc} onChange={setLoc} />
          <button
            onClick={() => setStep("category")}
            className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white"
          >
            Confirm location
          </button>
        </section>
      )}

      {step === "category" && (
        <section className="space-y-4">
          <p className="text-sm text-slate-500">Step 3 · What kind of issue?</p>
          <div className="grid grid-cols-2 gap-2">
            {CATEGORIES.map((c) => (
              <button
                key={c}
                onClick={() => {
                  setCategory(c);
                  runAnalysis();
                }}
                className="rounded-lg border border-slate-200 p-3 text-left text-sm hover:border-brand"
              >
                {c}
              </button>
            ))}
          </div>
        </section>
      )}

      {step === "analyzing" && (
        <p className="py-16 text-center text-sm text-slate-400">🤖 Analysing your complaint…</p>
      )}

      {step === "review" && result && (
        <section className="space-y-4">
          <p className="text-sm text-slate-500">Step 4 · AI suggestion</p>
          <div className="space-y-2 rounded-xl border border-slate-200 p-4 text-sm">
            <Row k="Title" v={result.analysis.title} />
            <Row k="Issue type" v={result.analysis.issue_type} />
            <Row k="Severity" v={result.analysis.severity} />
            <Row k="Locality" v={result.geo.locality_name ?? "—"} />
            <Row k="Local body" v={result.geo.local_body_type ?? "—"} />
            <Row k="AI confidence" v={`${Math.round(result.analysis.confidence * 100)}%`} />
          </div>
          <button
            disabled={busy}
            onClick={() => finalize(false)}
            className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white disabled:opacity-40"
          >
            Submit as a new issue
          </button>
        </section>
      )}

      {step === "verify" && result?.duplicates.best_candidate && (
        <section className="space-y-4">
          <div className="rounded-xl border border-amber-300 bg-amber-50 p-4">
            <h2 className="font-semibold text-amber-900">Possible existing issue found nearby</h2>
            <p className="mt-1 text-sm text-amber-800">
              An issue near this location appears to match your complaint.
            </p>
            <div className="mt-3 rounded-lg bg-white p-3 text-sm">
              <p className="font-medium">{result.duplicates.best_candidate.title}</p>
              <p className="mt-1 text-xs text-slate-500">
                {Math.round(result.duplicates.best_candidate.distance_m)} m away ·{" "}
                {result.duplicates.best_candidate.corroboration_count} corroborations · status{" "}
                {result.duplicates.best_candidate.status} · match{" "}
                {Math.round(result.duplicates.best_candidate.score * 100)}%
              </p>
            </div>
          </div>
          <button
            disabled={busy}
            onClick={() => finalize(true)}
            className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white disabled:opacity-40"
          >
            Yes, this is the same issue — corroborate
          </button>
          <button
            disabled={busy}
            onClick={() => finalize(false)}
            className="w-full rounded-lg border border-slate-300 p-3 text-sm font-semibold text-slate-600"
          >
            No, report as a new issue
          </button>
        </section>
      )}
    </main>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-slate-400">{k}</span>
      <span className="text-right font-medium capitalize">{v.replace(/_/g, " ")}</span>
    </div>
  );
}
