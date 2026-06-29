# CIVIKTA
### Every civic issue. Right authority. Full transparency.

AI-powered civic grievance routing across Delhi's 9 authorities and 272 wards using Google Gemini 2.5 Flash.

**Live:** [civikta-web-67594358509.us-central1.run.app](https://civikta-web-67594358509.us-central1.run.app)  
**API:** [civikta-api-67594358509.us-central1.run.app/docs](https://civikta-api-67594358509.us-central1.run.app/docs)  
**Built for:** Vibe2Ship Hackathon 2026 — PS2: Community Hero

---

## What it does

Citizens in Delhi report a civic issue (pothole, sewage overflow, broken streetlight, encroachment, etc.) by uploading photos and pinning a location. Gemini AI analyses the report, classifies its severity, and routes it to the exact government authority responsible for that location — MCD, NDMC, DJB, PWD, IFCD, DDA, Delhi Police, or NHAI.

Authority officers see a live, urgency-scored queue and update issue status. Citizens can track progress, corroborate existing reports, and escalate if deadlines are breached. Oversight officers get city-wide analytics and proactive AI anomaly alerts.

---

## Key features

**Citizen flow**
- Photo quality validation via Gemini Vision before submission
- GPS-to-ward resolution across all 272 Delhi wards and MCD zones
- AI triage: issue type classification, severity scoring, authority routing
- Duplicate detection — corroborate existing reports instead of filing noise
- Real-time status tracking and SLA-breach escalation

**Authority portals**
- Separate dashboards for MCD (12 zones), NDMC, DCB, DJB, PWD, IFCD, DDA, Delhi Police, NHAI
- Issues sorted by urgency score (severity × corroboration × deadline proximity)
- Status updates: submitted → in_progress → resolved / rejected
- Escalation queue for SLA breaches and citizen disputes

**Oversight dashboard**
- City-wide issue stats and SLA compliance by authority
- Geographic hotspot clustering
- Proactive anomaly alerts powered by Gemini

**AI analytics**
- Natural-language chatbot for oversight officers
- Ask plain-English questions; Gemini function-calls the live database and synthesises answers

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (standalone, App Router) |
| Backend | FastAPI + Python 3.12 |
| AI | Google Gemini 2.5 Flash (vision, triage, analytics, anomaly detection) |
| Database | Supabase Postgres + PostGIS (geospatial jurisdiction queries) |
| Deployment | Google Cloud Run (both frontend and backend) |
| Maps | Google Maps Platform |

---

## Monorepo layout

```
civikta/
  apps/
    web/              Next.js frontend (citizen + authority + oversight)
  services/
    api/              FastAPI backend (18 endpoints across 8 route groups)
  packages/
    shared-types/     TypeScript types mirroring backend contracts
  infra/
    sql/              Postgres schema, seeds, PostGIS + routing rules
```

---

## API overview

18 endpoints across 8 groups. Full interactive docs at `/docs`.

| Group | Endpoints | Description |
|---|---|---|
| `reports` | 7 | Submission pipeline: validate → draft → media → AI analyze → dedup → submit |
| `authority` | 4 | Prioritised queue, issue detail, status updates, escalations |
| `issues` | 3 | Public issue detail, corroboration, escalation requests |
| `feed` | 2 | Nearby issues feed, map viewport |
| `geo` | 1 | GPS → ward + authority + MCD zone resolution |
| `analytics` | 1 | Gemini natural-language analytics chatbot |
| `oversight` | 3 | City stats, hotspots, AI anomaly alerts |
| `users` | 3 | Sign-in, profile upsert, profile fetch |

---

## Local development

### Backend
```bash
cd services/api
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# -> http://localhost:8000/docs
```

### Frontend
```bash
cd apps/web
npm install
npm run dev
# -> http://localhost:3000
```

Copy `.env.example` to `.env` / `.env.local` and fill in your keys. The backend runs with stub defaults (no external services needed) if keys are omitted.

---

## Deployment

Both services are containerised and deployed to Google Cloud Run via `deploy.ps1`.

```powershell
cd civikta
.\deploy.ps1
```
