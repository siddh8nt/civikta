// Persists which authority portal the current user is operating in.
// Written when landing on the dashboard; read by all authority pages.

export interface AuthorityContext {
  authority: string;   // e.g. "mcd"
  zone: string | null; // e.g. "South West"
}

const KEY = "civikta_authority_ctx";

export function saveAuthorityContext(ctx: AuthorityContext): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(ctx));
}

export function getAuthorityContext(): AuthorityContext | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as AuthorityContext) : null;
  } catch { return null; }
}

// ── Authority display metadata ────────────────────────────────────────────────

export type AuthMeta = {
  name: string;
  full: string;
  headerBg: string;
  accent: string;
};

export const AUTHORITY_META: Record<string, AuthMeta> = {
  mcd:    { name: "MCD",             full: "Municipal Corporation of Delhi",        headerBg: "bg-blue-700",   accent: "text-blue-600" },
  ndmc:   { name: "NDMC",            full: "New Delhi Municipal Council",           headerBg: "bg-indigo-700", accent: "text-indigo-600" },
  dcb:    { name: "DCB",             full: "Delhi Cantonment Board",                headerBg: "bg-slate-700",  accent: "text-slate-600" },
  djb:    { name: "Delhi Jal Board", full: "Delhi Jal Board",                      headerBg: "bg-teal-700",   accent: "text-teal-600" },
  pwd:    { name: "PWD",             full: "Public Works Department",               headerBg: "bg-orange-600", accent: "text-orange-600" },
  ifcd:   { name: "IFCD",            full: "Irrigation & Flood Control Dept.",      headerBg: "bg-cyan-700",   accent: "text-cyan-600" },
  dda:    { name: "DDA",             full: "Delhi Development Authority",           headerBg: "bg-violet-700", accent: "text-violet-600" },
  police: { name: "Delhi Police",    full: "Delhi Police",                          headerBg: "bg-slate-900",  accent: "text-slate-700" },
  nhai:   { name: "NHAI",            full: "National Highways Auth. of India",      headerBg: "bg-amber-600",  accent: "text-amber-600" },
};

export const DEFAULT_META: AuthMeta = {
  name: "Authority", full: "Departmental Portal",
  headerBg: "bg-slate-800", accent: "text-slate-600",
};

export function getAuthorityMeta(slug: string): AuthMeta {
  return AUTHORITY_META[slug] ?? DEFAULT_META;
}
