"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

/** Compact issue-ID search bar for authority and oversight portals.
 *  urlPrefix: "/authority/issues" or "/oversight/issues"
 */
export function IssueSearchBar({ urlPrefix }: { urlPrefix: string }) {
  const [query, setQuery] = useState("");
  const router = useRouter();

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = query.trim().replace(/^CIV-/i, "");
    if (!trimmed) return;
    // Accept full UUID or short prefix (first 8 chars)
    router.push(`${urlPrefix}/${trimmed}`);
    setQuery("");
  }

  return (
    <form onSubmit={handleSearch} className="flex items-center gap-2">
      <div className="relative flex-1">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by Issue ID…"
          className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none"
        />
      </div>
      <button
        type="submit"
        className="rounded-lg bg-slate-800 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700 transition"
      >
        Go
      </button>
    </form>
  );
}
