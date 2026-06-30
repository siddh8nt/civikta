// Persistent dark backdrop behind every /onboarding/* page. Next.js App
// Router keeps this layout mounted across navigation between sibling routes
// (welcome → signup → kyc → location), so the page's own dark background
// never has to "catch up" mid-transition — eliminating the flash of the
// light page body background during client-side route swaps.
export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return <div className="min-h-dvh bg-slate-950">{children}</div>;
}
