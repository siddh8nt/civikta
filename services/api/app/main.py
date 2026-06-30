"""CIVIKTA API entrypoint.

Runs end-to-end with zero external services (stub LLM + in-memory repo, seeded
with demo issues). Visit /docs for the interactive API, /api/config to confirm
which seams are active.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import analytics, authority, feed, geo, issues, meta, oversight, reports, users

settings = get_settings()

DESCRIPTION = """
## CIVIKTA — Delhi Civic Issue Transparency & Routing Platform

CIVIKTA is an AI-powered platform that lets Delhi citizens report civic problems (potholes, broken streetlights, sewage overflow, encroachments, etc.) and automatically routes them to the correct government authority using Google Gemini.

---

### 🏗️ How It Works

1. **Citizen reports an issue** — uploads photos, describes the problem, pins location on map
2. **Gemini AI analyses the report** — classifies severity, detects duplicates, extracts structured metadata
3. **Smart routing engine** — matches the issue to the responsible authority (MCD, NDMC, DJB, PWD, IFCD, DDA, Delhi Police, NHAI) based on jurisdiction, issue type, and location
4. **Authority dashboard** — officials see a prioritised queue scored by urgency, corroboration count, and SLA deadline
5. **Oversight layer** — city-level analytics, hotspot detection, and escalation management for administrators

---

### 🔑 Key Feature Groups

#### `/api/reports` — Citizen Issue Submission Pipeline
Multi-step submission flow: validate images → create draft → attach media → AI analysis → duplicate check → submit.
Gemini Vision scores image quality and extracts issue metadata before submission.

#### `/api/authority` — Authority Queue & Status Management
Department officials access their filtered issue queue sorted by urgency score (composite of severity, corroboration, and SLA deadline proximity).
Status transitions: `submitted → in_progress → resolved` or `rejected`. Citizens can escalate rejected/stale resolutions.

#### `/api/issues` — Issue Detail & Citizen Actions
Fetch full issue detail including AI analysis, media, ward/zone routing metadata.
Citizens can corroborate existing reports (upvote with evidence) and request escalation if SLA is breached.

#### `/api/feed` — Citizen Feed & Map
Geo-filtered feed of nearby issues within a configurable radius.
Map endpoint returns all active issues with coordinates for the citizen map view.

#### `/api/geo` — Jurisdiction Resolution
Resolves a GPS coordinate to the responsible authority slug, ward name, MCD zone, and locality — powers automatic routing at submission time.

#### `/api/analytics` — AI-Powered Insights (Gemini)
Natural-language query interface for oversight users. Ask questions like *"Which ward had the most waterlogging issues this monsoon?"* and get structured answers powered by Gemini.

#### `/api/oversight` — City-Level Dashboard
Summary stats, geographic hotspot clusters, and active SLA breach alerts for government oversight officers.

#### `/api/users` — Identity & Onboarding
Citizen sign-in and profile upsert. Stores ward/locality for personalised feed and pre-filled reports.

---

### 🤖 AI Stack
- **Google Gemini 2.5 Flash** — image analysis, severity classification, duplicate detection, natural-language analytics
- **Supabase Postgres** — persistent storage with PostGIS for geospatial jurisdiction queries
- **Cloud Run** — fully containerised, auto-scaling deployment on GCP

---

### 🏆 Built for Vibe2Ship Hackathon 2026 — PS2: Community Hero
"""

app = FastAPI(
    title="CIVIKTA API",
    version="1.0.0",
    description=DESCRIPTION,
    contact={"name": "Civikta", "url": "https://civikta-web-67594358509.us-central1.run.app"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "reports",   "description": "Citizen issue submission pipeline — draft, media, AI analysis, duplicate check, submit"},
        {"name": "authority", "description": "Authority issue queue, status updates, and escalation management"},
        {"name": "issues",    "description": "Issue detail fetch and citizen actions (corroborate, escalate)"},
        {"name": "feed",      "description": "Geo-filtered citizen feed and map data"},
        {"name": "geo",       "description": "GPS coordinate → jurisdiction & ward resolution"},
        {"name": "analytics", "description": "Natural-language AI analytics powered by Gemini"},
        {"name": "oversight", "description": "City-level summary stats, hotspots, and SLA alerts"},
        {"name": "users",     "description": "Citizen identity, sign-in, and profile management"},
        {"name": "meta",      "description": "Health check and runtime configuration"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (meta.router, reports.router, issues.router, feed.router,
          authority.router, oversight.router, geo.router, users.router, analytics.router):
    app.include_router(r)


@app.get("/")
async def root() -> dict:
    return {"name": "CIVIKTA API", "docs": "/docs", "config": "/api/config"}
