const AUTHORITY_LABELS: Record<string, string> = {
  mcd_sanitation:    "Municipal Corporation of Delhi — Sanitation",
  mcd_engineering:   "Municipal Corporation of Delhi — Engineering",
  mcd_horticulture:  "Municipal Corporation of Delhi — Horticulture & Parks",
  mcd_public_health: "Municipal Corporation of Delhi — Public Health",
  ndmc_sanitation:   "New Delhi Municipal Council — Sanitation",
  ndmc_civil:        "New Delhi Municipal Council — Civil Works",
  ndmc_horticulture: "New Delhi Municipal Council — Horticulture",
  dcb_civic:         "Delhi Cantonment Board",
  djb:               "Delhi Jal Board",
  pwd:               "Public Works Department",
  ifcd:              "Irrigation & Flood Control Department",
  dda:               "Delhi Development Authority",
  delhi_police:      "Delhi Police",
  nhai:              "National Highways Authority of India",
};

export function authorityLabel(slug: string | null | undefined): string {
  if (!slug) return "—";
  return AUTHORITY_LABELS[slug] ?? slug.replace(/_/g, " ");
}
