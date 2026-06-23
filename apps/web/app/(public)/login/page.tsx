import Link from "next/link";

// Stub auth screen. Wire Firebase Authentication here (CIVIKTA_AUTH=firebase).
export default function LoginPage() {
  return (
    <main className="app-shell flex flex-col justify-center gap-5 p-6">
      <h1 className="text-2xl font-bold text-brand">Sign in to CIVIKTA</h1>
      <p className="text-sm text-slate-500">
        Demo mode — no real auth yet. Firebase Authentication (OTP / Google sign-in)
        slots in here.
      </p>
      <div className="space-y-3">
        <input
          className="w-full rounded-lg border border-slate-300 p-3 text-sm"
          placeholder="Phone or email"
        />
        <button className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white">
          Send OTP (stub)
        </button>
      </div>
      <Link href="/my-locality" className="text-center text-sm font-medium text-brand">
        Continue as demo citizen →
      </Link>
    </main>
  );
}
