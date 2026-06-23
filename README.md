# CIVIKTA

Delhi Civic Issue Transparency & Routing Platform.

See [`../CIVIKTA_PRD_UNIFIED.md`](../CIVIKTA_PRD_UNIFIED.md) for the full product + technical spec.

## Monorepo layout

```
civikta/
  apps/
    web/              Next.js frontend (citizen app + authority + oversight dashboards)
  services/
    api/              FastAPI backend (intake, geo, routing, duplicate detection, feed)
  packages/
    shared-types/     TS types mirroring the backend contracts
  infra/
    sql/              Postgres schema + seeds (PostGIS + pgvector)
    docs/             Routing rules + authority master reference
```

## The big idea: it runs today, the real services slot in later

The backend is built around **four config-driven seams**. Each one ships with a
zero-dependency default so the whole app runs end-to-end with **no API keys and no
database**. When you're ready, you write one new file and flip one env flag — no
caller code changes.

| Seam | Default (now) | Production (later) | Flip with |
|------|---------------|--------------------|-----------|
| **Pipeline** (orchestration) | `DeterministicPipeline` — calls services in a fixed order | `AgenticPipeline` — Gemini + ADK tool loop | `CIVIKTA_PIPELINE` |
| **LLM** (model provider) | `StubLLMClient` — offline keyword heuristics | `GeminiClient` — Gemini via AI Studio key | `CIVIKTA_LLM` |
| **Repository** (data) | `MemoryRepository` — in-process dict store | `SupabaseRepository` — Postgres + PostGIS | `CIVIKTA_REPO` |
| **Auth** | `StubAuth` — trusts a demo header | `FirebaseAuth` — verifies Firebase ID tokens | `CIVIKTA_AUTH` |

> The future **agentic orchestration layer** is just a new `ComplaintPipeline`
> implementation. The deterministic services (`geo`, `routing`, `duplicate
> detection`, `urgency`) are already exposed as agent-ready **tools** in
> `app/agents/tools.py`. Building the agent = wiring those existing tools into an
> ADK loop. Nothing downstream has to change.

## Quick start

### Backend
```bash
cd services/api
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# -> http://localhost:8000/docs  (interactive API, works with zero external services)
```
> Python 3.12 recommended. Newer versions may lack prebuilt wheels for some deps.

### Frontend
```bash
cd apps/web
npm install
npm run dev
# -> http://localhost:3000
```

Copy `.env.example` files to `.env` / `.env.local` and fill in only what you need —
the defaults run without any of it.
