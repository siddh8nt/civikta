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
    <form
      onSubmit={handleSearch}
      className="flex w-full max-w-[220px] items-center gap-1.5 rounded-full border border-slate-200 bg-white py-1 pl-3.5 pr-1 shadow-sm transition-all focus-within:border-slate-300 focus-within:shadow-md"
    >
      <svg
        className="h-3.5 w-3.5 shrink-0 text-slate-400"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
      </svg>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by Issue ID…"
        className="min-w-0 flex-1 border-0 bg-transparent text-[13px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
      />
      <button
        type="submit"
        disabled={!query.trim()}
        aria-label="Search"
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 disabled:opacity-0"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </button>
    </form>
  );
}
