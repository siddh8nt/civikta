import Link from "next/link";

const ENTRIES = [
  { href: "/my-locality", title: "Citizen App", desc: "Report, browse & verify issues near you", emoji: "📍" },
  { href: "/authority/dashboard", title: "Authority Dashboard", desc: "Operator queue & status workflow", emoji: "🏛️" },
  { href: "/oversight/dashboard", title: "Oversight Cockpit", desc: "Hotspots, performance & AI alerts", emoji: "📊" },
];

export default function Home() {
  return (
    <main className="app-shell flex flex-col justify-center gap-6 p-6">
      <div>
        <h1 className="text-3xl font-bold text-brand">CIVIKTA</h1>
        <p className="mt-1 text-sm text-slate-500">
          Delhi civic issue transparency & routing. Sunlight is the best disinfectant.
        </p>
      </div>
      <div className="space-y-3">
        {ENTRIES.map((e) => (
          <Link
            key={e.href}
            href={e.href}
            className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 transition hover:border-brand"
          >
            <span className="text-2xl">{e.emoji}</span>
            <span>
              <span className="block font-semibold">{e.title}</span>
              <span className="block text-xs text-slate-500">{e.desc}</span>
            </span>
          </Link>
        ))}
      </div>
      <p className="text-center text-xs text-slate-400">
        Demo build · stub auth · in-memory data
      </p>
    </main>
  );
}
