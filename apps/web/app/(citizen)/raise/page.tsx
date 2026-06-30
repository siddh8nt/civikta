"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { LocationStep } from "@/components/LocationStep";
import { api } from "@/lib/api";
import { getUserLocation } from "@/lib/user";
import type { DuplicateCandidate } from "@/lib/types";

// ── Types ─────────────────────────────────────────────────────────────────────

type Step = "location" | "camera" | "describe" | "confirm" | "submitting";
type SubmitStage = "creating" | "analyzing" | "filing";
type LatLng = { lat: number; lng: number };
type WardInfo = {
  ward_no: number | null;
  ward_name: string | null;
  zone: string | null;
  local_body_type: string | null;
  locality_name: string | null;
  in_delhi: boolean;
};
type Photo = { id: string; dataUrl: string };

// ── Helpers ───────────────────────────────────────────────────────────────────

function compressImage(dataUrl: string, maxPx = 1280, q = 0.78): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxPx / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * scale);
      c.height = Math.round(img.height * scale);
      c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
      resolve(c.toDataURL("image/jpeg", q));
    };
    img.src = dataUrl;
  });
}

// ── Voice hook (hold-to-speak) ────────────────────────────────────────────────

type RecordState = "idle" | "recording" | "unsupported";

function useVoice(onTranscript: (t: string) => void) {
  const [state, setState] = useState<RecordState>("idle");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recRef   = useRef<any>(null);
  const holdRef  = useRef(false);   // true while the button is physically held
  const cbRef    = useRef(onTranscript);
  const [interim, setInterim] = useState("");

  // Audio blob capture (runs alongside SpeechRecognition during the hold)
  const [audioData, setAudioData] = useState<string | null>(null);
  const mrRef     = useRef<MediaRecorder | null>(null);
  const mrChunks  = useRef<Blob[]>([]);

  // keep callback ref fresh so closures never go stale
  useEffect(() => { cbRef.current = onTranscript; }, [onTranscript]);

  const supported = useCallback((): boolean => {
    if (typeof window === "undefined") return false;
    // Speech API is blocked on HTTP (non-secure context) on Android Chrome — same as getUserMedia
    if (!window.isSecureContext) return false;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    return !!(w.SpeechRecognition || w.webkitSpeechRecognition);
  }, []);

  const startAudioCapture = useCallback(async () => {
    if (mrRef.current) return; // already capturing
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      mrChunks.current = [];
      mr.ondataavailable = (e) => { if (e.data.size > 0) mrChunks.current.push(e.data); };
      mr.onstop = () => {
        const blob = new Blob(mrChunks.current, { type: mr.mimeType || "audio/webm" });
        if (blob.size > 0) {
          const reader = new FileReader();
          reader.onloadend = () => setAudioData(reader.result as string);
          reader.readAsDataURL(blob);
        }
        stream.getTracks().forEach((t) => t.stop());
        mrRef.current = null;
      };
      mr.start();
      mrRef.current = mr;
    } catch {
      // permission denied or MediaRecorder unavailable — transcript still works
    }
  }, []);

  const stopAudioCapture = useCallback(() => {
    if (mrRef.current && mrRef.current.state !== "inactive") {
      mrRef.current.stop();
    }
  }, []);

  const lastInterimRef = useRef(""); // best text seen in current session
  const gotFinalRef   = useRef(false);

  const launchRec = useCallback(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = typeof window !== "undefined" ? (window as any) : null;
    const SR = w?.SpeechRecognition || w?.webkitSpeechRecognition || null;
    if (!SR || recRef.current) return;

    lastInterimRef.current = "";
    gotFinalRef.current    = false;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const rec: any = new SR();
    rec.lang = "hi-IN";
    rec.continuous = false;
    rec.interimResults = true;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    rec.onresult = (e: any) => {
      let inter = "";
      for (let i = 0; i < e.results.length; i++) {
        if (e.results[i].isFinal) {
          const t = e.results[i][0].transcript.trim();
          if (t) { cbRef.current(t); gotFinalRef.current = true; }
        } else {
          inter += e.results[i][0].transcript;
        }
      }
      // keep the best interim so onend can fall back to it
      if (inter) lastInterimRef.current = inter;
      setInterim(inter);
    };

    rec.onerror = () => {
      recRef.current = null;
      setInterim("");
      if (holdRef.current) setTimeout(launchRec, 150);
      else setState("idle");
    };

    rec.onend = () => {
      recRef.current = null;
      // Android Chrome often never sets isFinal — use last interim as fallback
      if (!gotFinalRef.current && lastInterimRef.current.trim()) {
        cbRef.current(lastInterimRef.current.trim());
      }
      lastInterimRef.current = "";
      setInterim("");
      if (holdRef.current) {
        setTimeout(launchRec, 80);
      } else {
        setState("idle");
      }
    };

    try {
      rec.start();
      recRef.current = rec;
      setState("recording");
    } catch {
      // already started — ignore
    }
  }, []); // stable: reads all mutable state through refs

  const startSession = useCallback(() => {
    holdRef.current = true;
    launchRec();
    startAudioCapture();
  }, [launchRec, startAudioCapture]);

  const stopSession = useCallback(() => {
    holdRef.current = false;
    if (recRef.current) { recRef.current.stop(); recRef.current = null; }
    setState("idle");
    setInterim("");
    stopAudioCapture();
  }, [stopAudioCapture]);

  return { state, interim, supported, startSession, stopSession, audioData };
}

// ── Follow-up questions ───────────────────────────────────────────────────────

function getFollowUps(text: string): Array<{ q: string; answers: string[] }> {
  const t = text.toLowerCase();
  if (/water|sewer|sewage|drain|flood|overflow|पानी|naali|नाली|baarish/.test(t))
    return [
      { q: "How long has this been happening?", answers: ["Today", "2-3 days", "A week+", "Months"] },
      { q: "Is there a health risk?", answers: ["Yes", "Possibly", "Not sure"] },
    ];
  if (/garbage|trash|kachra|कचरा|dump|waste|sanitation/.test(t))
    return [
      { q: "When was garbage last collected?", answers: ["Yesterday", "2-3 days ago", "A week+"] },
      { q: "How many households affected?", answers: ["Just my building", "Entire lane", "Multiple lanes"] },
    ];
  if (/pothole|road|sadak|सड़क|footpath|gutter/.test(t))
    return [
      { q: "Has any accident happened because of this?", answers: ["Yes", "No", "Near misses"] },
      { q: "Is traffic movement affected?", answers: ["Completely blocked", "Slowed down", "No"] },
    ];
  if (/light|lamp|bijli|बिजली|electric|wire|dark/.test(t))
    return [
      { q: "How many lights are not working?", answers: ["1-2", "3-5", "Entire stretch"] },
      { q: "Is this a safety concern at night?", answers: ["Yes, women's safety", "Yes, accident risk", "General inconvenience"] },
    ];
  if (/tree|park|garden|branch/.test(t))
    return [
      { q: "Is it blocking the road or footpath?", answers: ["Yes, completely", "Partially", "No"] },
      { q: "Is there immediate danger?", answers: ["Yes, about to fall", "Possibly", "No"] },
    ];
  if (/dog|stray|cat|animal|bite/.test(t))
    return [
      { q: "Have there been any bites or attacks?", answers: ["Yes", "No", "Near misses"] },
      { q: "Where are they concentrated?", answers: ["Near my building", "On main road", "In park"] },
    ];
  return [
    { q: "How long has this issue been here?", answers: ["Today", "A few days", "A week+", "Months"] },
    { q: "How urgently does it need fixing?", answers: ["Emergency", "Within a day", "This week"] },
  ];
}

// ── Progress dots ─────────────────────────────────────────────────────────────

const STEP_ORDER: Step[] = ["location", "camera", "describe", "confirm"];

function ProgressDots({ step }: { step: Step }) {
  const idx = STEP_ORDER.indexOf(step as Step);
  return (
    <div className="flex items-center gap-1.5">
      {STEP_ORDER.map((_, i) => (
        <div
          key={i}
          className={`rounded-full transition-all duration-300 ${
            i === idx
              ? "h-2 w-5 bg-brand"
              : i < idx
              ? "h-2 w-2 bg-brand/40"
              : "h-2 w-2 bg-slate-200"
          }`}
        />
      ))}
    </div>
  );
}

// ── Step shell ────────────────────────────────────────────────────────────────

function StepShell({
  step,
  title,
  subtitle,
  onBack,
  children,
}: {
  step: Step;
  title: string;
  subtitle?: string;
  onBack: () => void;
  children: React.ReactNode;
}) {
  // Fade + rise in once on first arrival at /raise, matching the My Locality
  // page transition. StepShell is the same component instance across step
  // switches, so this only fires on initial mount, not every step change.
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <div
      className={`flex flex-col overflow-hidden bg-paper transition-all duration-300 ease-out ${
        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
      }`}
      style={{ maxWidth: 480, margin: "0 auto", height: "calc(100dvh - 104px)" }}
    >
      <div className="flex items-center gap-3 border-b border-slate-100 px-4 py-3">
        <button
          onClick={onBack}
          className="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 active:bg-slate-100"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
            <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-slate-900 truncate">{title}</h1>
          {subtitle && <p className="text-[11px] text-slate-400">{subtitle}</p>}
        </div>
        <ProgressDots step={step} />
      </div>
      {children}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────────────────────────────────────

export default function RaisePage() {
  const router = useRouter();

  const fileRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [step, setStep] = useState<Step>("location");

  // true when running on HTTP (LAN dev) — getUserMedia is blocked, use native file capture
  const [useNativeCamera] = useState<boolean>(
    () => typeof window !== "undefined" && !window.isSecureContext
  );

  // Location — fixed SSR default; updated from localStorage after hydration
  const [loc, setLoc] = useState<LatLng>({ lat: 28.6139, lng: 77.209 });
  useEffect(() => {
    const saved = getUserLocation();
    if (saved?.lat && saved?.lng) setLoc({ lat: saved.lat, lng: saved.lng });
  }, []);
  const [wardInfo, setWardInfo] = useState<WardInfo | null>(null);
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState<string | null>(null);
  const [showLocConfirm, setShowLocConfirm] = useState(false);

  // Camera
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [viewingPhoto, setViewingPhoto] = useState<Photo | null>(null);

  // Describe
  const [transcript, setTranscript] = useState("");
  const [description, setDescription] = useState("");
  const [followUps, setFollowUps] = useState<Array<{ q: string; answers: string[] }>>([]);
  const [answeredFollowUps, setAnsweredFollowUps] = useState<Record<string, string>>({});

  // Submit
  const [busy, setBusy] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitStage, setSubmitStage] = useState<SubmitStage>("creating");
  const [analyzeMsgIdx, setAnalyzeMsgIdx] = useState(0);
  const [cvCandidate, setCvCandidate] = useState<DuplicateCandidate | null>(null);
  const [pendingReportId, setPendingReportId] = useState<string | null>(null);

  // ── Voice ──────────────────────────────────────────────────────────────────

  const handleTranscript = useCallback((t: string) => {
    setTranscript((prev) => {
      const next = prev ? prev + " " + t : t;
      setFollowUps(getFollowUps(next));
      return next;
    });
  }, []);

  const voice = useVoice(handleTranscript);

  // ── Camera lifecycle ───────────────────────────────────────────────────────

  useEffect(() => {
    // Native camera mode (HTTP / insecure context): no getUserMedia needed
    if (useNativeCamera) return;

    if (step !== "camera") {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
      return;
    }
    startStream(facingMode);
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step, facingMode, useNativeCamera]);

  async function startStream(facing: "environment" | "user") {
    setCameraError(null);
    try {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: facing, width: { ideal: 1280 }, height: { ideal: 1280 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch {
      setCameraError("Camera access denied — please allow camera or use gallery below.");
    }
  }

  function capturePhoto() {
    if (photos.length >= 3) return;
    const video = videoRef.current;
    if (!video) return;
    const size = Math.min(video.videoWidth, video.videoHeight);
    if (!size) return;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d")!;
    ctx.drawImage(
      video,
      (video.videoWidth - size) / 2,
      (video.videoHeight - size) / 2,
      size, size, 0, 0, size, size,
    );
    const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
    const id = `${Date.now()}-${Math.random()}`;
    setPhotos((p) => [...p, { id, dataUrl }]);
  }

  async function handleFiles(files: FileList | null) {
    if (!files) return;
    const allowed = 3 - photos.length;
    for (const file of Array.from(files).slice(0, allowed)) {
      if (!file.type.startsWith("image/")) continue;
      const dataUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target!.result as string);
        reader.readAsDataURL(file);
      });
      const compressed = await compressImage(dataUrl);
      const id = `${Date.now()}-${Math.random()}`;
      setPhotos((p) => (p.length < 3 ? [...p, { id, dataUrl: compressed }] : p));
    }
    // reset so the same file can be re-picked after retake
    if (cameraRef.current) cameraRef.current.value = "";
    if (fileRef.current) fileRef.current.value = "";
  }

  // ── Location ───────────────────────────────────────────────────────────────

  async function handleConfirmPin() {
    setResolving(true);
    setResolveError(null);
    try {
      const res = await api.geoResolve(loc.lat, loc.lng);
      setWardInfo(res);
      setShowLocConfirm(true);
    } catch {
      setResolveError("Couldn't identify location — check your connection.");
    } finally {
      setResolving(false);
    }
  }

  // ── Submit ─────────────────────────────────────────────────────────────────

  const ANALYZE_MSGS = [
    "Reading your description…",
    "Examining photos for evidence…",
    "Identifying the issue type…",
    "Checking ward & jurisdiction…",
    "Determining responsible authority…",
    "Building your report…",
  ];

  async function handleSubmit() {
    const combinedText = [
      transcript,
      Object.entries(answeredFollowUps)
        .map(([q, a]) => `${q}: ${a}`)
        .join(". "),
      description,
    ]
      .filter(Boolean)
      .join("\n")
      .trim();

    setBusy(true);
    setSubmitError(null);
    setSubmitStage("creating");
    setAnalyzeMsgIdx(0);
    setStep("submitting");

    let msgTimer: ReturnType<typeof setInterval> | null = null;
    try {
      const draft = await api.createDraft({
        raw_description: combinedText || undefined,
        latitude: loc.lat,
        longitude: loc.lng,
        image_data: photos.map((p) => p.dataUrl),
        audio_data: voice.audioData ?? undefined,
      });

      setSubmitStage("analyzing");
      setAnalyzeMsgIdx(0);
      msgTimer = setInterval(() => {
        setAnalyzeMsgIdx((i) => (i + 1) % ANALYZE_MSGS.length);
      }, 2200);

      const analyzeResult = await api.analyze(draft.report_id);
      clearInterval(msgTimer);
      msgTimer = null;

      // If a nearby duplicate was found, pause and ask the citizen
      if (analyzeResult.duplicates.has_candidate && analyzeResult.duplicates.best_candidate) {
        setPendingReportId(draft.report_id);
        setCvCandidate(analyzeResult.duplicates.best_candidate);
        return; // wait for handleCvDecision
      }

      setSubmitStage("filing");
      const res = await api.submit(draft.report_id, { corroborate: false });
      router.push(`/issues/${res.issue_id}`);
    } catch (err) {
      if (msgTimer) clearInterval(msgTimer);
      const msg = err instanceof Error ? err.message : "Unknown error";
      setSubmitError(`Submission failed — ${msg}. Please try again.`);
      setStep("confirm");
      setBusy(false);
    }
  }

  async function handleCvDecision(corroborate: boolean) {
    if (!pendingReportId) return;
    // Capture before clearing state so the value is definitely available in the async call below
    const targetIssueId = cvCandidate?.issue_id;
    setCvCandidate(null);
    setSubmitStage("filing");
    try {
      const res = await api.submit(pendingReportId, {
        corroborate,
        target_issue_id: corroborate ? targetIssueId : undefined,
      });
      router.push(`/issues/${res.issue_id}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setSubmitError(`Submission failed — ${msg}. Please try again.`);
      setStep("confirm");
      setBusy(false);
    }
  }

  // ── Back nav ───────────────────────────────────────────────────────────────

  function handleBack() {
    if (step === "location") router.push("/my-locality");
    else if (step === "camera") setStep("location");
    else if (step === "describe") setStep("camera");
    else if (step === "confirm") setStep("describe");
  }

  const hasEvidence =
    transcript.trim().length > 0 || description.trim().length > 0;

  const fullDescription = [
    transcript,
    Object.entries(answeredFollowUps)
      .map(([q, a]) => `${q}: ${a}`)
      .join(". "),
    description,
  ]
    .filter(Boolean)
    .join("\n")
    .trim();

  // ─────────────────────────────────────────────────────────────────────────
  // SUBMITTING
  // ─────────────────────────────────────────────────────────────────────────

  if (step === "submitting") {
    const stageOrder: SubmitStage[] = ["creating", "analyzing", "filing"];
    const stageIdx = stageOrder.indexOf(submitStage);

    const stages = [
      {
        key: "creating" as SubmitStage,
        icon: (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
        ),
        label: "Creating report",
        activeMsg: "Uploading your photos and description…",
        doneMsg: "Report created",
      },
      {
        key: "analyzing" as SubmitStage,
        icon: (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
          </svg>
        ),
        label: "AI analysis",
        activeMsg: ANALYZE_MSGS[analyzeMsgIdx],
        doneMsg: "Issue classified & authority identified",
      },
      {
        key: "filing" as SubmitStage,
        icon: (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
          </svg>
        ),
        label: "Filing with authority",
        activeMsg: "Sending to the correct department…",
        doneMsg: "Filed successfully",
      },
    ];

    return (
      <div
        className="flex min-h-screen flex-col bg-paper"
        style={{ maxWidth: 480, margin: "0 auto" }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-slate-100 px-4 py-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand/10">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
            </svg>
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900">Processing your report</p>
            <p className="text-[11px] text-slate-400">Please don't close this screen</p>
          </div>
        </div>

        {/* Body */}
        <div className="flex flex-1 flex-col px-6 pt-10 pb-8">

          {/* AI brain graphic */}
          <div className="mb-10 flex justify-center">
            <div className="relative flex h-24 w-24 items-center justify-center">
              <span className="absolute inset-0 animate-ping rounded-full bg-brand/10" style={{ animationDuration: "2s" }} />
              <span className="absolute inset-3 animate-pulse rounded-full bg-brand/10" style={{ animationDuration: "1.5s" }} />
              <span className="relative flex h-14 w-14 items-center justify-center rounded-full bg-brand/15">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-4.16z"/>
                  <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-4.16z"/>
                </svg>
              </span>
            </div>
          </div>

          {/* Stage list */}
          <div className="space-y-0">
            {stages.map((stage, i) => {
              const idx = stageOrder.indexOf(stage.key);
              const isDone = idx < stageIdx;
              const isActive = idx === stageIdx;

              return (
                <div key={stage.key} className="flex gap-4">
                  {/* Timeline column */}
                  <div className="flex flex-col items-center" style={{ width: 36 }}>
                    <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all duration-500 ${
                      isDone
                        ? "bg-brand text-white shadow-md shadow-brand/30"
                        : isActive
                        ? "border-2 border-brand bg-brand/10 text-brand"
                        : "border-2 border-slate-200 bg-cream text-slate-300"
                    }`}>
                      {isDone ? (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      ) : isActive ? (
                        <span className="flex h-2.5 w-2.5 rounded-full bg-brand animate-pulse" />
                      ) : (
                        stage.icon
                      )}
                    </div>
                    {i < stages.length - 1 && (
                      <div className={`mt-1 w-0.5 flex-1 rounded-full transition-all duration-700 ${isDone ? "bg-brand/30 min-h-[2rem]" : "bg-slate-100 min-h-[2rem]"}`} />
                    )}
                  </div>

                  {/* Content */}
                  <div className={`pb-7 pt-1.5 flex-1 min-w-0 ${i === stages.length - 1 ? "pb-0" : ""}`}>
                    <p className={`text-sm font-semibold transition-colors duration-300 ${
                      isDone ? "text-brand" : isActive ? "text-slate-900" : "text-slate-300"
                    }`}>
                      {stage.label}
                    </p>
                    {isActive && (
                      <p key={stage.activeMsg} className="mt-0.5 text-xs text-slate-500 transition-all duration-300">
                        {stage.activeMsg}
                      </p>
                    )}
                    {isDone && (
                      <p className="mt-0.5 text-xs text-brand/70">{stage.doneMsg}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Community Verification card — shown when AI finds a nearby duplicate */}
          {cvCandidate && (
            <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 overflow-hidden">
              <div className="px-4 pt-4 pb-3">
                <div className="flex items-center gap-2 mb-2">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#d97706" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  <p className="text-xs font-bold text-amber-700 uppercase tracking-wide">Similar issue nearby</p>
                </div>
                <p className="text-sm font-semibold text-slate-900 leading-snug mb-1">
                  {cvCandidate.title ?? "Existing civic issue"}
                </p>
                <p className="text-xs text-slate-500">
                  {Math.round(cvCandidate.distance_m)}m away
                  {cvCandidate.corroboration_count > 0
                    ? ` · ${cvCandidate.corroboration_count} other${cvCandidate.corroboration_count !== 1 ? "s" : ""} reported this`
                    : ""}
                </p>
              </div>
              <div className="border-t border-amber-100 px-4 py-3 space-y-2">
                <p className="text-[11px] text-slate-500 mb-1">Is this the same issue you're reporting?</p>
                <button
                  onClick={() => handleCvDecision(true)}
                  className="w-full rounded-xl bg-brand py-3 text-sm font-bold text-white active:scale-95 transition-transform"
                >
                  Yes — add my report to this issue
                </button>
                <button
                  onClick={() => handleCvDecision(false)}
                  className="w-full rounded-xl border border-slate-200 bg-paper py-3 text-sm font-semibold text-slate-600 active:scale-95 transition-transform"
                >
                  No — it's a different issue
                </button>
              </div>
            </div>
          )}

          {/* Footer note */}
          {!cvCandidate && (
            <div className="mt-auto pt-10 text-center">
              <p className="text-[11px] text-slate-300">
                {submitStage === "analyzing"
                  ? "AI is thinking — this usually takes 10–15 seconds"
                  : submitStage === "creating"
                  ? "Uploading your evidence…"
                  : "Almost done…"}
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // STEP 1 — LOCATION
  // ─────────────────────────────────────────────────────────────────────────

  if (step === "location") {
    return (
      <StepShell
        step="location"
        title="Where is the issue?"
        subtitle="Drag the map to place the pin exactly"
        onBack={handleBack}
      >
        <div className="flex-1 overflow-y-auto px-3 pt-2 pb-1">
          <LocationStep value={loc} onChange={setLoc} />
        </div>

        <div className="border-t border-slate-100 px-4 pb-5 pt-2 space-y-2">
          {resolveError && (
            <p className="text-center text-xs text-rose-500">{resolveError}</p>
          )}
          <button
            onClick={handleConfirmPin}
            disabled={resolving}
            className="w-full rounded-2xl bg-slate-900 py-4 text-sm font-bold text-white transition active:scale-95 disabled:opacity-50"
          >
            {resolving ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Identifying location…
              </span>
            ) : (
              "Confirm pin location →"
            )}
          </button>
        </div>

        {/* Location confirm sheet */}
        {showLocConfirm && wardInfo && (
          <div
            className="fixed inset-0 z-50 flex flex-col justify-end"
            style={{ maxWidth: 480, margin: "0 auto" }}
          >
            <div
              className="absolute inset-0 bg-black/40 backdrop-blur-sm"
              onClick={() => setShowLocConfirm(false)}
            />
            <div
              className="relative rounded-t-3xl bg-paper px-6 pb-10 pt-5 shadow-2xl"
              style={{ animation: "slide-up 0.3s cubic-bezier(.4,0,.2,1) forwards" }}
            >
              <style>{`@keyframes slide-up{from{transform:translateY(100%)}to{transform:translateY(0)}}`}</style>
              <div className="mx-auto mb-5 h-1 w-10 rounded-full bg-slate-200" />
              <p className="mb-4 text-sm font-bold text-slate-900">Issue location identified</p>
              <div className="mb-5 rounded-2xl bg-cream p-4 space-y-2.5">
                {wardInfo.locality_name && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Area</span>
                    <span className="text-sm font-semibold text-slate-900">{wardInfo.locality_name}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Ward</span>
                  <span className="text-sm font-medium text-slate-700">
                    {wardInfo.ward_name ?? "—"}
                    {wardInfo.ward_no ? ` (#${wardInfo.ward_no})` : ""}
                  </span>
                </div>
                {wardInfo.zone && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Zone</span>
                    <span className="text-sm font-medium text-slate-700">{wardInfo.zone}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Authority</span>
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                    wardInfo.local_body_type === "NDMC"
                      ? "bg-blue-50 text-blue-700"
                      : wardInfo.local_body_type === "DCB"
                      ? "bg-amber-50 text-amber-700"
                      : "bg-emerald-50 text-emerald-700"
                  }`}>
                    {wardInfo.local_body_type ?? "—"}
                  </span>
                </div>
                <div className="flex items-center justify-between border-t border-slate-100 pt-2.5">
                  <span className="text-xs text-slate-400">Coordinates</span>
                  <span className="text-[11px] text-slate-500 tabular-nums">
                    {loc.lat.toFixed(4)}, {loc.lng.toFixed(4)}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <button
                  onClick={() => { setShowLocConfirm(false); setStep("camera"); }}
                  className="w-full rounded-2xl bg-brand py-4 text-sm font-bold text-white active:scale-95"
                >
                  Looks correct — Next →
                </button>
                <button
                  onClick={() => setShowLocConfirm(false)}
                  className="w-full rounded-2xl border border-slate-200 py-3.5 text-sm font-semibold text-slate-600"
                >
                  Change location
                </button>
              </div>
            </div>
          </div>
        )}
      </StepShell>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // STEP 2 — CAMERA
  // ─────────────────────────────────────────────────────────────────────────

  if (step === "camera") {
    return (
      <StepShell
        step="camera"
        title="Photo evidence"
        subtitle={photos.length === 0 ? "Take up to 3 photos of the issue" : `${photos.length}/3 taken — tap a photo to retake`}
        onBack={handleBack}
      >
        {/* Hidden file inputs */}
        {/* Native camera capture (used on HTTP/insecure context) */}
        <input
          ref={cameraRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {/* Gallery picker */}
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />

        <div className="flex flex-1 flex-col items-center overflow-y-auto px-4 pt-4 pb-4 gap-4">

          {useNativeCamera ? (
            /* ── Native camera mode (HTTP LAN) ── */
            <div
              className="relative w-full overflow-hidden rounded-2xl bg-slate-900 flex flex-col items-center justify-center gap-5"
              style={{ aspectRatio: "1 / 1" }}
            >
              {photos.length < 3 ? (
                <>
                  <div className="flex h-20 w-20 items-center justify-center rounded-full border-4 border-white/20">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity=".7">
                      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                  </div>
                  <button
                    onClick={() => cameraRef.current?.click()}
                    className="rounded-2xl bg-white px-8 py-3.5 text-sm font-bold text-slate-900 active:scale-95 transition-transform shadow-lg"
                  >
                    Open camera
                  </button>
                  <p className="text-[11px] text-white/40 -mt-2">
                    {photos.length > 0 ? `${photos.length}/3 taken` : "Tap to take a photo"}
                  </p>
                </>
              ) : (
                <p className="text-sm font-medium text-white/60">3 photos taken</p>
              )}
            </div>
          ) : (
            /* ── In-browser getUserMedia viewfinder (HTTPS) ── */
            <div
              className="relative w-full overflow-hidden rounded-2xl bg-slate-900"
              style={{ aspectRatio: "1 / 1" }}
            >
              {cameraError ? (
                <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" opacity=".5">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  <p className="text-xs text-white/60">{cameraError}</p>
                  <button
                    onClick={() => startStream(facingMode)}
                    className="rounded-xl bg-white/20 px-4 py-2 text-sm font-medium text-white"
                  >
                    Try again
                  </button>
                </div>
              ) : (
                // eslint-disable-next-line jsx-a11y/media-has-caption
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="absolute inset-0 h-full w-full object-cover"
                />
              )}

              {/* Switch camera */}
              {!cameraError && (
                <button
                  onClick={() =>
                    setFacingMode((f) => (f === "environment" ? "user" : "environment"))
                  }
                  className="absolute right-3 top-3 flex h-10 w-10 items-center justify-center rounded-full bg-black/50 text-white"
                  aria-label="Switch camera"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 4v6h6M23 20v-6h-6"/>
                    <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4-4.64 4.36A9 9 0 0 1 3.51 15"/>
                  </svg>
                </button>
              )}

              {/* Shutter */}
              {!cameraError && photos.length < 3 && (
                <button
                  onClick={capturePhoto}
                  className="absolute bottom-5 left-1/2 -translate-x-1/2 flex h-16 w-16 items-center justify-center rounded-full border-4 border-white/80 bg-white/20 backdrop-blur active:scale-90 transition-transform"
                  aria-label="Take photo"
                >
                  <div className="h-11 w-11 rounded-full bg-white shadow-inner" />
                </button>
              )}

              {photos.length >= 3 && (
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full bg-black/60 px-4 py-2 text-xs font-medium text-white">
                  3 photos taken
                </div>
              )}
            </div>
          )}

          {/* Thumbnails */}
          <div className="flex w-full items-center gap-3">
            {photos.map((ph) => (
              <button
                key={ph.id}
                onClick={() => setViewingPhoto(ph)}
                className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl border-2 border-brand active:scale-95 transition-transform"
                aria-label="View photo"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={ph.dataUrl} alt="" className="h-full w-full object-cover" />
              </button>
            ))}
            {Array.from({ length: 3 - photos.length }).map((_, i) => (
              <div
                key={i}
                className="h-20 w-20 shrink-0 rounded-xl border-2 border-dashed border-slate-200 bg-cream"
              />
            ))}
          </div>

          {/* Gallery / add more */}
          <button
            onClick={() => fileRef.current?.click()}
            disabled={photos.length >= 3}
            className="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-600 disabled:opacity-40"
          >
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" aria-hidden>
              <rect x="2" y="2" width="16" height="16" rx="3" stroke="currentColor" strokeWidth="1.5"/>
              <circle cx="7" cy="7" r="1.5" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M2 13l5-5 4 4 2-2 5 5" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
            </svg>
            {useNativeCamera && photos.length > 0 ? "Add from gallery" : "Choose from gallery"}
          </button>
        </div>

        <div className="border-t border-slate-100 px-4 pb-8 pt-3">
          <button
            onClick={() => setStep("describe")}
            disabled={photos.length === 0}
            className="w-full rounded-2xl bg-slate-900 py-4 text-sm font-bold text-white transition active:scale-95 disabled:opacity-40"
          >
            {photos.length === 0 ? "Take at least 1 photo to continue" : "Next — Describe the issue →"}
          </button>
        </div>

        {/* Photo full-view overlay */}
        {viewingPhoto && (
          <div
            className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/95 px-6"
            style={{ maxWidth: 480, margin: "0 auto" }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={viewingPhoto.dataUrl}
              alt=""
              className="max-h-[70vh] w-full rounded-xl object-contain"
            />
            <div className="mt-8 flex gap-3 w-full">
              <button
                onClick={() => {
                  setPhotos((p) => p.filter((x) => x.id !== viewingPhoto.id));
                  setViewingPhoto(null);
                  // on native mode, re-open camera so they can retake immediately
                  if (useNativeCamera) setTimeout(() => cameraRef.current?.click(), 100);
                }}
                className="flex-1 rounded-2xl border border-white/30 py-3.5 text-sm font-semibold text-white"
              >
                Retake
              </button>
              <button
                onClick={() => setViewingPhoto(null)}
                className="flex-1 rounded-2xl bg-white/20 py-3.5 text-sm font-semibold text-white"
              >
                Keep
              </button>
            </div>
          </div>
        )}
      </StepShell>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // STEP 3 — DESCRIBE
  // ─────────────────────────────────────────────────────────────────────────

  if (step === "describe") {
    return (
      <StepShell
        step="describe"
        title="Describe the issue"
        subtitle="Voice, text, or both"
        onBack={handleBack}
      >
        <div className="flex-1 overflow-y-auto px-4 pt-4 pb-4 space-y-4">

          {/* Context strip: location + photos */}
          <div className="flex gap-2 overflow-x-auto pb-1">
            <div className="h-20 w-20 shrink-0 overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
              <iframe
                title="Issue pin"
                src={`https://maps.google.com/maps?q=${loc.lat},${loc.lng}&z=17&output=embed`}
                className="block border-0 pointer-events-none"
                style={{ width: 80, height: 80, marginLeft: -1, marginTop: -1 }}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
            {photos.map((ph) => (
              <div
                key={ph.id}
                className="h-20 w-20 shrink-0 overflow-hidden rounded-xl border border-slate-200"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={ph.dataUrl} alt="" className="h-full w-full object-cover" />
              </div>
            ))}
          </div>

          {/* Voice recorder — hold to speak */}
          {voice.supported() ? (
            <div className="rounded-2xl border border-slate-100 bg-cream p-5">
              {/* Instruction */}
              <p className="text-center text-xs font-semibold text-slate-500 mb-4">
                {voice.state === "recording"
                  ? (<span className="text-rose-500 font-bold">🔴 Listening — release when done</span>)
                  : transcript
                  ? "Hold to add more"
                  : "Hold the button and speak"}
              </p>

              {/* Big hold button */}
              <div className="flex justify-center mb-4">
                <button
                  onPointerDown={(e) => { (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId); voice.startSession(); }}
                  onPointerUp={() => voice.stopSession()}
                  onPointerLeave={() => voice.stopSession()}
                  onPointerCancel={() => voice.stopSession()}
                  className={`select-none touch-none flex h-24 w-24 flex-col items-center justify-center rounded-full transition-all duration-150 ${
                    voice.state === "recording"
                      ? "scale-110 bg-rose-500 text-white shadow-xl shadow-rose-200"
                      : "bg-paper border-2 border-slate-200 text-slate-600 active:scale-105 active:border-brand active:text-brand shadow-md"
                  }`}
                  aria-label="Hold to record"
                >
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                  </svg>
                  <span className="mt-1 text-[10px] font-semibold tracking-wide">
                    {voice.state === "recording" ? "RELEASE" : "HOLD"}
                  </span>
                </button>
              </div>

              <p className="text-center text-[11px] text-slate-400 mb-3">
                Hindi · English · Hinglish · You can hold multiple times
              </p>

              {/* Live + saved transcript */}
              {(transcript || voice.interim) && (
                <div className="rounded-xl bg-paper border border-slate-200 px-3 py-2.5 text-sm text-slate-700 leading-relaxed">
                  {transcript}
                  {voice.interim && (
                    <span className="text-slate-400"> {voice.interim}…</span>
                  )}
                </div>
              )}
              {transcript && (
                <button
                  onClick={() => { setTranscript(""); setFollowUps([]); setAnsweredFollowUps({}); }}
                  className="mt-2 text-[10px] text-slate-400 underline"
                >
                  Clear
                </button>
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-amber-200 bg-amber-50 px-4 py-4 text-center space-y-1">
              <p className="text-sm font-semibold text-amber-800">Voice requires HTTPS</p>
              <p className="text-xs text-amber-600">Running on local network — type your description in the box below. Voice works on the deployed app.</p>
            </div>
          )}

            {/* Follow-up chips */}
            {transcript && followUps.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-200 space-y-3">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
                  Quick questions — tap to answer (optional)
                </p>
                {followUps.map(({ q, answers }) => (
                  <div key={q}>
                    <p className="text-xs font-medium text-slate-600 mb-1.5">{q}</p>
                    {answeredFollowUps[q] ? (
                      <div className="flex items-center justify-between rounded-lg bg-brand/10 px-3 py-1.5">
                        <span className="text-xs font-semibold text-brand">{answeredFollowUps[q]}</span>
                        <button
                          onClick={() =>
                            setAnsweredFollowUps((a) => {
                              const n = { ...a };
                              delete n[q];
                              return n;
                            })
                          }
                          className="text-[11px] text-slate-400 ml-2"
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {answers.map((a) => (
                          <button
                            key={a}
                            onClick={() =>
                              setAnsweredFollowUps((prev) => ({ ...prev, [q]: a }))
                            }
                            className="rounded-full border border-slate-200 bg-paper px-3 py-1 text-xs text-slate-700 active:bg-brand active:text-white active:border-brand transition-colors"
                          >
                            {a}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

          {/* Text field */}
          <div>
            <p className="mb-1.5 text-xs font-semibold text-slate-400">
              {voice.supported() ? "Additional details" : "Describe the issue"}{" "}
              <span className="font-normal text-slate-300">
                {hasEvidence ? "(optional)" : "(required)"}
              </span>
            </p>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="How long has it been there? Any landmark? Who is affected?…"
              className="w-full rounded-xl border border-slate-200 bg-cream p-3 text-sm text-slate-700 placeholder-slate-400 focus:border-brand focus:outline-none"
            />
          </div>

          {!hasEvidence && (
            <p className="text-center text-xs text-rose-500">
              Please add a voice note or description before continuing.
            </p>
          )}
        </div>

        <div className="border-t border-slate-100 px-4 pb-8 pt-3">
          <button
            disabled={!hasEvidence}
            onClick={() => setStep("confirm")}
            className="w-full rounded-2xl bg-slate-900 py-4 text-sm font-bold text-white transition active:scale-95 disabled:opacity-40"
          >
            Review before posting →
          </button>
        </div>
      </StepShell>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // STEP 4 — CONFIRM
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <StepShell
      step="confirm"
      title="Review your report"
      subtitle="Everything looks good? Post it."
      onBack={handleBack}
    >
      <div className="flex-1 overflow-y-auto px-4 pt-4 pb-4 space-y-4">

        {/* Location */}
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Location</p>
          <div className="overflow-hidden rounded-2xl border border-slate-200">
            <div className="overflow-hidden" style={{ height: 140 }}>
              <iframe
                title="Issue location"
                width="100%"
                height="140"
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                src={`https://maps.google.com/maps?q=${loc.lat},${loc.lng}&z=17&output=embed`}
                className="block w-full border-0 pointer-events-none"
              />
            </div>
            <div className="flex items-center justify-between bg-paper px-3 py-2">
              <span className="text-xs font-medium text-slate-700">
                {wardInfo?.locality_name ?? wardInfo?.ward_name ?? "Location confirmed"}
                {wardInfo?.ward_no ? ` — Ward #${wardInfo.ward_no}` : ""}
              </span>
              <span className="text-[10px] tabular-nums text-slate-400">
                {loc.lat.toFixed(4)}, {loc.lng.toFixed(4)}
              </span>
            </div>
          </div>
        </div>

        {/* Photos */}
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Photos ({photos.length})
          </p>
          <div className="flex gap-2">
            {photos.map((ph) => (
              <div
                key={ph.id}
                className="h-24 w-24 overflow-hidden rounded-xl border border-slate-200"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={ph.dataUrl} alt="" className="h-full w-full object-cover" />
              </div>
            ))}
          </div>
        </div>

        {/* Description */}
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Your description
          </p>
          <div className="rounded-2xl border border-slate-100 bg-cream p-4">
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
              {fullDescription || "(no description provided)"}
            </p>
          </div>
        </div>

        <div className="rounded-xl bg-brand/5 border border-brand/20 px-4 py-3">
          <p className="text-[11px] text-brand/80 leading-relaxed">
            AI will analyse your photos, voice note, and description to classify the issue and automatically route it to the correct Delhi authority.
          </p>
        </div>

        {submitError && (
          <p className="rounded-xl bg-rose-50 px-3 py-2 text-xs text-rose-600">
            {submitError}
          </p>
        )}
      </div>

      <div className="border-t border-slate-100 px-4 pb-8 pt-3">
        <button
          disabled={busy}
          onClick={handleSubmit}
          className="w-full rounded-2xl bg-brand py-4 text-sm font-bold text-white transition active:scale-95 disabled:opacity-50"
        >
          {busy ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Posting…
            </span>
          ) : (
            "Post this issue →"
          )}
        </button>
      </div>
    </StepShell>
  );
}
