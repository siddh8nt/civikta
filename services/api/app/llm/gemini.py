"""Real Gemini LLM client — uses the `google-genai` SDK (v2+).

Enable:
  pip install google-genai
  CIVIKTA_LLM=gemini
  GEMINI_API_KEY=<from Google AI Studio>

Prompt was developed and iterated in Google AI Studio before wiring here.
All network calls are async (client.aio) to keep the uvicorn event loop free.
"""

from __future__ import annotations

import json
import logging

import httpx

from app.core.config import Settings
from app.llm.base import EMBEDDING_DIM
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import Severity

log = logging.getLogger(__name__)

_SYSTEM = """\
You are CIVIKTA's civic complaint classifier for Delhi, India.

Your job: analyze citizen complaints about civic issues and produce a precise \
structured classification.

Issue categories (use one of these exact slugs):
roads_streets | water_sewer_drainage | garbage_sanitation | lights_electrical \
| parks_public_space | public_safety_hazard | other

Issue types (most specific match):
  roads_streets        → pothole_local_road, pothole_major_road, road_obstruction, \
broken_footpath, footpath_encroachment
  water_sewer_drainage → sewer_overflow, no_water_supply, contaminated_water, \
waterlogging, clogged_local_drain
  garbage_sanitation   → garbage_not_collected, illegal_dumping, dead_animal
  lights_electrical    → streetlight_not_working
  parks_public_space   → park_maintenance_issue, tree_hazard
  public_safety_hazard → stray_dog_issue, road_obstruction
  other                → other

Road class (road issues only): local_lane | collector_road | arterial | highway
Drain type (drainage issues only): sewer | roadside_storm_drain | local_open_drain | trunk_drain
Asset types: sewer_line, water_pipeline, local_lane, arterial_road, community_bin, \
garbage_blackspot, park, tree, footpath, road_row
Land owner hints (who is responsible in Delhi):
  mcd | ndmc | djb | pwd | ifcd | dda | railways | central_govt

Severity rules:
  critical — immediate threat to life (raw sewage flooding road, live wire, collapse)
  high     — health hazard or serious obstruction (sewer overflow, no water for days)
  medium   — significant inconvenience (garbage not collected 2+ days, pothole)
  low      — cosmetic or minor issue

Return ONLY valid JSON. Be concise and specific."""

_PROMPT_TEMPLATE = """\
Classify this Delhi civic complaint:

TEXT: {text}
LOCATION: {location}
USER_CATEGORY_HINT: {category}
ATTACHED_IMAGES: {media_count}

Return a JSON object with exactly these fields:
{{
  "title": "<5-8 word headline — e.g. 'Sewer overflow blocking Lajpat Nagar lane'>",
  "summary": "<1-2 sentence description>",
  "issue_category": "<category slug>",
  "issue_type": "<type slug>",
  "asset_type": "<asset slug or null>",
  "severity": "low|medium|high|critical",
  "obstruction_flag": true/false,
  "health_hazard_flag": true/false,
  "public_safety_flag": true/false,
  "road_class": "<road class or null>",
  "drain_type": "<drain type or null>",
  "land_owner_hint": "<authority slug or null>",
  "confidence": 0.0-1.0,
  "needs_manual_review": true/false
}}"""

_VALID_SEVERITIES = {"low", "medium", "high", "critical"}


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("CIVIKTA_LLM=gemini requires GEMINI_API_KEY.")

        from google import genai
        from google.genai import types as gtypes

        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._gtypes = gtypes
        self._model = settings.gemini_model
        self._embed_model = settings.vertex_embedding_model

    async def analyze_complaint(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
        parts: list = []

        # Attach up to 3 images inline
        if inp.media_urls:
            async with httpx.AsyncClient(timeout=10.0) as http:
                for url in inp.media_urls[:3]:
                    try:
                        r = await http.get(url)
                        r.raise_for_status()
                        mime = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
                        parts.append(
                            self._gtypes.Part.from_bytes(data=r.content, mime_type=mime)
                        )
                    except Exception as exc:
                        log.warning("Skip media %s: %s", url, exc)

        location_str = (
            f"{inp.latitude:.4f}, {inp.longitude:.4f}"
            if inp.latitude is not None
            else "not provided"
        )
        parts.append(
            self._gtypes.Part.from_text(
                _PROMPT_TEMPLATE.format(
                    text=inp.text or "(no description provided)",
                    location=location_str,
                    category=inp.category_hint or "not specified",
                    media_count=len(inp.media_urls),
                )
            )
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=parts,
                config=self._gtypes.GenerateContentConfig(
                    system_instruction=_SYSTEM,
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=512,
                ),
            )
            raw = response.text
        except Exception as exc:
            log.error("Gemini analyze_complaint call failed: %s", exc)
            return _fallback(inp)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            log.error("Gemini JSON parse error: %s — raw: %.300s", exc, raw)
            return _fallback(inp)

        try:
            sev_raw = str(data.get("severity", "medium")).lower()
            sev = sev_raw if sev_raw in _VALID_SEVERITIES else "medium"
            return ComplaintAnalysis(
                title=str(data.get("title", "Civic issue reported"))[:120],
                summary=str(data.get("summary", inp.text or ""))[:500],
                issue_category=str(data.get("issue_category") or "other"),
                issue_type=str(data.get("issue_type") or "garbage_not_collected"),
                asset_type=data.get("asset_type") or None,
                severity=Severity(sev),
                obstruction_flag=bool(data.get("obstruction_flag", False)),
                health_hazard_flag=bool(data.get("health_hazard_flag", False)),
                public_safety_flag=bool(data.get("public_safety_flag", False)),
                road_class=data.get("road_class") or None,
                drain_type=data.get("drain_type") or None,
                land_owner_hint=data.get("land_owner_hint") or None,
                confidence=float(data.get("confidence", 0.7)),
                needs_manual_review=bool(data.get("needs_manual_review", False)),
            )
        except (KeyError, ValueError, TypeError) as exc:
            log.error("ComplaintAnalysis construction failed: %s — data: %s", exc, data)
            return _fallback(inp)

    async def embed(self, text: str) -> list[float]:
        try:
            result = await self._client.aio.models.embed_content(
                model=self._embed_model,
                contents=[text],
            )
            vec: list[float] = list(result.embeddings[0].values)
        except Exception as exc:
            log.error("Gemini embed failed: %s", exc)
            vec = []

        if len(vec) < EMBEDDING_DIM:
            vec.extend([0.0] * (EMBEDDING_DIM - len(vec)))
        return vec[:EMBEDDING_DIM]

    async def summarize(self, prompt: str) -> str:
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=self._gtypes.GenerateContentConfig(
                    temperature=0.4, max_output_tokens=150
                ),
            )
            return response.text.strip()
        except Exception as exc:
            log.error("Gemini summarize failed: %s", exc)
            return prompt[:150]


def _fallback(inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
    text = inp.text or ""
    return ComplaintAnalysis(
        title=text[:80] if text else "Civic issue reported",
        summary=text,
        issue_category="other",
        issue_type="garbage_not_collected",
        severity=Severity.medium,
        confidence=0.2,
        needs_manual_review=True,
    )
