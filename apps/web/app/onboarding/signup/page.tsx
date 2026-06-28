"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { saveProfile, markOnboardingComplete, setUserId, getUserLocation, saveUserLocation } from "@/lib/user";
import { supabase } from "@/lib/supabase";
import { api } from "@/lib/api";

// Hidden from user — phone is the only identifier shown
function toEmail(phone: string) {
  return `u${phone}@gmail.com`;
}

export default function SignupPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"signup" | "signin">("signup");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<{ name?: string; phone?: string; password?: string; confirm?: string }>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  function validate() {
    const e: typeof errors = {};
    if (mode === "signup") {
      if (!name.trim() || name.trim().length < 2) e.name = "Enter your full name";
      const digits = phone.replace(/\D/g, "");
      if (digits.length !== 10) e.phone = "Enter a valid 10-digit mobile number";
      if (password.length < 6) e.password = "Password must be at least 6 characters";
      if (password !== confirmPassword) e.confirm = "Passwords do not match";
    } else {
      const digits = phone.replace(/\D/g, "");
      if (digits.length !== 10) e.phone = "Enter a valid 10-digit mobile number";
      if (!password) e.password = "Enter your password";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleNext() {
    if (!validate()) return;
    setLoading(true);
    setServerError(null);
    const digits = phone.replace(/\D/g, "");
    const email = toEmail(digits);

    if (mode === "signup") {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) {
        setServerError(error.message);
        setLoading(false);
        return;
      }
      const uid = data.user?.id;
      if (uid) setUserId(uid);
      saveProfile({ name: name.trim(), phone: digits });
      try { await api.upsertMe({ name: name.trim(), phone: digits }); } catch { /* non-fatal */ }
      window.location.href = "/onboarding/kyc";
    } else {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setServerError("Incorrect phone number or password.");
        setLoading(false);
        return;
      }
      const uid = data.user?.id;
      if (uid) setUserId(uid);

      // 1. localStorage has location from previous onboarding on this device
      const saved = getUserLocation();
      if (saved) {
        markOnboardingComplete();
        window.location.href = "/my-locality";
        return;
      }

      // 2. No local data - hydrate the signed-in phone account from the backend.
      // /me may point at the current demo/auth identity, so use the phone lookup.
      try {
        const u = await api.signin({ phone: digits, password_hash: password });
        saveProfile({ name: u.name ?? "", phone: u.phone ?? digits });
        if (u.id) setUserId(u.id);
        if (u.home_lat != null && u.home_lng != null) {
          saveUserLocation({
            lat: u.home_lat,
            lng: u.home_lng,
            ward_no: u.ward_no ?? null,
            ward_name: u.ward_name ?? null,
            zone: u.zone ?? null,
            local_body_type: u.local_body_type ?? null,
          });
          markOnboardingComplete();
          window.location.href = "/my-locality";
          return;
        }
      } catch { /* fall through */ }

      window.location.href = "/onboarding/location";
    }
  }

  return (
    <div className="flex h-dvh flex-col bg-slate-950 overflow-hidden" style={{ maxWidth: 480, margin: "0 auto" }}>
      <div className="shrink-0 px-6 pt-6">
        <button onClick={() => router.back()} className="text-slate-500 text-sm">← Back</button>
      </div>

      <div className="shrink-0 px-6 pt-6 pb-4">
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
          <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-emerald-400" stroke="currentColor" strokeWidth={1.8}>
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" strokeLinecap="round" />
          </svg>
        </div>
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          {mode === "signup" ? "Create your account" : "Welcome back"}
        </h1>
        <p className="mt-1.5 text-sm text-slate-400">
          {mode === "signup" ? "Set up your Civikta identity in seconds." : "Sign in with your phone and password."}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 space-y-4">
        {mode === "signup" && (
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-slate-500">Full Name</label>
            <input
              type="text" value={name}
              onChange={(e) => { setName(e.target.value); setErrors((v) => ({ ...v, name: undefined })); }}
              placeholder="Your name" autoComplete="name"
              className={`w-full rounded-2xl border bg-slate-900 px-4 py-3.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-2 ${errors.name ? "border-rose-500 focus:ring-rose-500/30" : "border-slate-800 focus:border-emerald-500 focus:ring-emerald-500/20"}`}
            />
            {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name}</p>}
          </div>
        )}

        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-slate-500">Mobile Number</label>
          <div className="flex items-center">
            <div className="flex items-center rounded-l-2xl border border-r-0 border-slate-800 bg-slate-900 px-3 py-3.5">
              <span className="text-sm font-medium text-slate-400">🇮🇳 +91</span>
            </div>
            <input
              type="tel" inputMode="numeric" value={phone}
              onChange={(e) => { setPhone(e.target.value); setErrors((v) => ({ ...v, phone: undefined })); }}
              placeholder="98765 43210" maxLength={10}
              className={`flex-1 rounded-r-2xl border bg-slate-900 px-4 py-3.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-2 ${errors.phone ? "border-rose-500 focus:ring-rose-500/30" : "border-slate-800 focus:border-emerald-500 focus:ring-emerald-500/20"}`}
            />
          </div>
          {errors.phone && <p className="mt-1 text-xs text-rose-400">{errors.phone}</p>}
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-slate-500">Password</label>
          <input
            type="password" value={password}
            onChange={(e) => { setPassword(e.target.value); setErrors((v) => ({ ...v, password: undefined })); }}
            placeholder={mode === "signup" ? "At least 6 characters" : "Your password"}
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            className={`w-full rounded-2xl border bg-slate-900 px-4 py-3.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-2 ${errors.password ? "border-rose-500 focus:ring-rose-500/30" : "border-slate-800 focus:border-emerald-500 focus:ring-emerald-500/20"}`}
          />
          {errors.password && <p className="mt-1 text-xs text-rose-400">{errors.password}</p>}
        </div>

        {mode === "signup" && (
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-widest text-slate-500">Confirm Password</label>
            <input
              type="password" value={confirmPassword}
              onChange={(e) => { setConfirmPassword(e.target.value); setErrors((v) => ({ ...v, confirm: undefined })); }}
              placeholder="Re-enter password" autoComplete="new-password"
              className={`w-full rounded-2xl border bg-slate-900 px-4 py-3.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-2 ${errors.confirm ? "border-rose-500 focus:ring-rose-500/30" : "border-slate-800 focus:border-emerald-500 focus:ring-emerald-500/20"}`}
            />
            {errors.confirm && <p className="mt-1 text-xs text-rose-400">{errors.confirm}</p>}
          </div>
        )}

        {serverError && (
          <p className="rounded-xl bg-rose-500/10 border border-rose-500/20 px-4 py-3 text-sm text-rose-400">{serverError}</p>
        )}
      </div>

      <div className="shrink-0 px-6 pb-8 pt-4 space-y-3">
        <button
          onClick={handleNext} disabled={loading}
          className="w-full rounded-2xl bg-emerald-500 py-4 text-sm font-bold text-white tracking-wide transition hover:bg-emerald-400 active:scale-95 disabled:opacity-60"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              {mode === "signup" ? "Creating account…" : "Signing in…"}
            </span>
          ) : (
            mode === "signup" ? "Continue →" : "Sign in →"
          )}
        </button>

        <button
          onClick={() => { setMode(mode === "signup" ? "signin" : "signup"); setServerError(null); setErrors({}); }}
          className="w-full text-center text-sm text-slate-500"
        >
          {mode === "signup"
            ? <>Already have an account? <span className="text-emerald-400 font-medium">Sign in</span></>
            : <>New user? <span className="text-emerald-400 font-medium">Create account</span></>}
        </button>
      </div>
    </div>
  );
}
