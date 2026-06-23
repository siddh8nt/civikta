# Extending CIVIKTA

The scaffold is built so each real service drops in without touching callers.
Every recipe below is: **write one file, flip one env flag.** The app keeps
running the whole time on the stub/in-memory defaults.

---

## 1. Add the agentic orchestration layer (the big one)

The complaint intake is a swappable `ComplaintPipeline` (`app/pipeline/base.py`).
The default is `DeterministicPipeline` (fixed-order service calls). The agent is
just a second implementation.

**The work is mostly done already:**
- The agent's tools exist and are tested: `app/agents/tools.py` exposes
  `analyze_complaint`, `resolve_delhi_geography`, `lookup_routing_candidates`,
  `duplicate_issue_search`, `embed_and_score_similarity`. Each has a
  `to_function_schema()` for one-line registration with Gemini/ADK.
- The output contract exists: `app/schemas/ai.py::ComplaintAnalysis`.
- The agent shell exists: `app/agents/complaint_triage_agent.py` (system
  instruction + loop skeleton).

**To wire it:**
1. `pip install google-adk` (and a Gemini key from Google AI Studio).
2. Implement the ADK tool-calling loop in `ComplaintTriageAgent.run()`.
3. Implement `AgenticPipeline.analyze()` (`app/pipeline/agentic.py`) to call the
   agent. `submit()` already delegates to deterministic routing — leave it.
4. Set `CIVIKTA_PIPELINE=agentic`.

Routers, services, schemas, and the frontend **do not change.** Routing stays
deterministic in every pipeline by design (PRD §22).

---

## 2. Swap the stub classifier for real Gemini  ✅ DONE

`GeminiClient` is fully implemented in `app/llm/gemini.py`. To activate:

1. `pip install google-genai` (already in `requirements.txt`).
2. Get an API key from [Google AI Studio](https://aistudio.google.com/).
3. `.env`: `CIVIKTA_LLM=gemini`, `GEMINI_API_KEY=<your key>`

The client uses the `google-genai` SDK (v2+, the successor to `google-generativeai`):
- `analyze_complaint` → multimodal Gemini 2.0 Flash call, JSON mode, returns `ComplaintAnalysis`
- `embed` → `text-embedding-004` via `client.aio.models.embed_content` (768-dim)
- `summarize` → oversight headlines + case briefs

Prompt was developed in Google AI Studio. Graceful fallback: if Gemini call fails,
the issue is flagged `needs_manual_review=True` rather than crashing the flow.

---

## 3. Move from in-memory to Supabase (Postgres + PostGIS + pgvector)

1. Create a Supabase project, run `infra/sql/schema.sql`, then the seeds in
   `infra/sql/seeds/`.
2. `pip install supabase`.
3. Implement `SupabaseRepository` in `app/repositories/supabase.py` against the
   `Repository` protocol (`app/repositories/base.py`). The spatial methods become
   PostGIS (`ST_DWithin`, bbox `&&`); semantic duplicate scoring uses the
   `summary_embedding` pgvector column.
4. `.env`: `CIVIKTA_REPO=supabase`, `SUPABASE_URL=...`, `SUPABASE_SERVICE_KEY=...`

Every service already speaks only the `Repository` protocol, so nothing else
changes.

---

## 4. Real auth (Firebase)

1. `pip install firebase-admin`, create a Firebase project + service account.
2. Implement `FirebaseAuth.authenticate()` in `app/core/auth.py` (verify the
   Bearer ID token, map UID → user).
3. `.env`: `CIVIKTA_AUTH=firebase`, `FIREBASE_PROJECT_ID=...`,
   `GOOGLE_APPLICATION_CREDENTIALS=...`
4. Frontend: send `Authorization: Bearer <idToken>` instead of the demo headers
   (`apps/web/lib/api.ts`).

---

## 5. Real Google Maps + Firebase Storage (frontend)

- **Maps / Places:** replace `components/MapPlaceholder.tsx` and the search box in
  `components/LocationStep.tsx` with the Maps JS SDK + Places Autocomplete
  (restrict to country `in`, bias to Delhi). Set `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`.
- **Storage:** in `app/(citizen)/raise/page.tsx`, replace the sample-image
  `addPhoto` with a Firebase Storage upload; pass the returned URL into
  `media_urls`. Set the `NEXT_PUBLIC_FIREBASE_*` vars.

---

## Where things live

| You want to change… | Go to |
|---|---|
| What the AI returns | `app/schemas/ai.py`, `app/llm/` |
| How issues are routed | `app/services/routing_service.py`, `app/seeds/routing_rules.py` |
| Duplicate scoring weights | `app/services/duplicate_detection_service.py` |
| Urgency formula | `app/services/urgency_score_service.py` |
| Oversight anomaly logic | `app/services/oversight_service.py` |
| API surface | `app/routers/` |
| The intake orchestration order | `app/pipeline/deterministic.py` |
| Demo data | `app/seeds/demo_issues.py` |
| Frontend screens | `apps/web/app/` (route groups: public / citizen / authority / oversight) |
