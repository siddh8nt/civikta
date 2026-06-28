#!/usr/bin/env python3
"""
Geo resolution verification script — tests known locations against the API.

Usage:
    python verify_geo.py [--base-url http://localhost:8000]

Exits with code 1 if any assertion fails.
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.parse

BASE_URL = "http://localhost:8000"
if "--base-url" in sys.argv:
    idx = sys.argv.index("--base-url")
    BASE_URL = sys.argv[idx + 1]

# ── Known test cases ──────────────────────────────────────────────────────────
# Format: (label, lat, lng, expected_jurisdiction, expected_zone_contains)
#   expected_zone_contains: substring that must appear in zone, or None to skip
TEST_CASES = [
    # ── NDMC area (must NOT return MCD) ──────────────────────────────────────
    ("Connaught Place",             28.6315, 77.2167, "NDMC", "NDMC"),
    ("India Gate",                  28.6120, 77.2295, "NDMC", "NDMC"),
    ("Rashtrapati Bhavan",          28.6143, 77.1990, "NDMC", "NDMC"),
    ("Lodhi Estate",                28.5936, 77.2270, "NDMC", "NDMC"),
    ("Chanakyapuri (diplo enclave)",28.5982, 77.1860, "NDMC", "NDMC"),
    ("Janpath",                     28.6260, 77.2195, "NDMC", "NDMC"),
    ("Khan Market",                 28.5997, 77.2268, "NDMC", "NDMC"),
    # ── DCB area (must NOT return MCD or NDMC) ────────────────────────────────
    ("Brar Square (DCB)",           28.5900, 77.0930, "DCB",  "DCB"),
    ("Shankar Vihar",               28.5950, 77.0920, "DCB",  "DCB"),
    # ── MCD areas (must NOT return NDMC or DCB) ──────────────────────────────
    ("Rohini Sector 17",            28.7220, 77.1350, "MCD",  "Rohini"),
    ("Lajpat Nagar",                28.5676, 77.2373, "MCD",  None),
    ("Dwarka Sector 12",            28.5954, 77.0370, "MCD",  None),
    ("Narela",                      28.8550, 77.0940, "MCD",  "Narela"),
    ("Shahdara",                    28.6714, 77.2943, "MCD",  "Shahdara"),
    ("Saket",                       28.5237, 77.2090, "MCD",  "South"),
]


def resolve(lat: float, lng: float) -> dict:
    url = f"{BASE_URL}/api/geo/resolve?lat={lat}&lng={lng}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main() -> None:
    passed = 0
    failed = 0
    errors = 0

    print(f"Verifying geo resolution against {BASE_URL}\n")
    print(f"{'Label':<35} {'Expected juris':<8} {'Got juris':<8} {'Zone':<20} {'Method':<25} {'OK?'}")
    print("-" * 110)

    for label, lat, lng, exp_jurisdiction, exp_zone_contains in TEST_CASES:
        try:
            r = resolve(lat, lng)
        except Exception as exc:
            print(f"{label:<35} {'':8} ERROR: {exc}")
            errors += 1
            continue

        got_jurisdiction = r.get("local_body_type") or ""
        got_zone         = r.get("zone") or ""
        ward_method      = r.get("debug", {}).get("ward_method", "?")
        juris_method     = r.get("debug", {}).get("jurisdiction_method", "?")
        method_str       = f"ward={ward_method} / juris={juris_method}"

        ok = got_jurisdiction == exp_jurisdiction
        if exp_zone_contains and exp_zone_contains not in (got_zone or ""):
            ok = False

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(
            f"{label:<35} {exp_jurisdiction:<8} {got_jurisdiction:<8} "
            f"{got_zone:<20} {method_str:<35} {status}"
        )
        if not ok:
            print(f"  -> ward={r.get('ward_name')} zone={got_zone!r} conf={r.get('confidence')}")

    print("-" * 110)
    print(f"\nResults: {passed} passed / {failed} failed / {errors} errors")

    if failed or errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
