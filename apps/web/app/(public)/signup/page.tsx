import Link from "next/link";

export default function SignupPage() {
  return (
    <main className="app-shell flex flex-col justify-center gap-5 p-6">
      <h1 className="text-2xl font-bold text-brand">Create your CIVIKTA account</h1>
      <p className="text-sm text-slate-500">Demo mode — Firebase Auth wires in here.</p>
      <div className="space-y-3">
        <input className="w-full rounded-lg border border-slate-300 p-3 text-sm" placeholder="Name" />
        <input className="w-full rounded-lg border border-slate-300 p-3 text-sm" placeholder="Phone or email" />
        <input className="w-full rounded-lg border border-slate-300 p-3 text-sm" placeholder="Home locality (optional)" />
        <button className="w-full rounded-lg bg-brand p-3 text-sm font-semibold text-white">
          Create account (stub)
        </button>
      </div>
      <Link href="/login" className="text-center text-sm font-medium text-brand">
        Already have an account? Sign in
      </Link>
    </main>
  );
}
