// Silent user identity — no login UI, UUID auto-generated on first visit.
// Stored in localStorage so it persists across sessions.

const KEY = "civikta_user_id";

export function setUserId(id: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, id);
}

function makeUUID(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Fallback for HTTP (non-secure) contexts — crypto.randomUUID requires HTTPS
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function getUserId(): string {
  if (typeof window === "undefined") return "ssr-placeholder";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = makeUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}

export function hasCompletedOnboarding(): boolean {
  if (typeof window === "undefined") return true;
  return localStorage.getItem("civikta_onboarded") === "1";
}

export function markOnboardingComplete(): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("civikta_onboarded", "1");
}

// Called on sign-out. Clears every piece of per-account local state — not
// just the onboarding flag — so a different account signing in on the same
// browser never inherits a stale cached location/profile from this one.
export function resetOnboarding(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("civikta_onboarded");
  localStorage.removeItem("civikta_location");
  localStorage.removeItem("civikta_profile");
  localStorage.removeItem("civikta_user_id");
}

// ── Profile ────────────────────────────────────────────────────────────────

export interface UserProfile {
  name: string;
  phone: string;
}

export interface UserLocation {
  lat: number;
  lng: number;
  ward_no: number | null;
  ward_name: string | null;
  zone: string | null;
  local_body_type: string | null;
}

export function saveProfile(p: UserProfile): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("civikta_profile", JSON.stringify(p));
}

export function getProfile(): UserProfile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("civikta_profile");
    return raw ? (JSON.parse(raw) as UserProfile) : null;
  } catch { return null; }
}

export function saveUserLocation(l: UserLocation): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("civikta_location", JSON.stringify(l));
}

export function getUserLocation(): UserLocation | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("civikta_location");
    return raw ? (JSON.parse(raw) as UserLocation) : null;
  } catch { return null; }
}
