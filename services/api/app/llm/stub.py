"""Offline LLM stub. Keyword-heuristic classifier so the whole intake flow works
with no API key. Deterministic, fast, good enough to demo the pipeline shape.

Swap for GeminiClient (CIVIKTA_LLM=gemini) for real multimodal understanding.
"""

from __future__ import annotations

import hashlib
import re

from app.llm.base import EMBEDDING_DIM
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import Severity
from app.seeds.issue_types import category_for_type

# ordered keyword -> (issue_type, asset_type, severity, health, safety, road_class, drain_type)
_RULES: list[tuple[list[str], dict]] = [
    (["sewer", "sewage", "gutter overflow", "manhole"],
     dict(t="sewer_overflow", a="sewer_line", sev=Severity.high, health=True, drain="sewer")),
    (["no water", "water supply", "no supply", "dry tap"],
     dict(t="no_water_supply", a="water_pipeline", sev=Severity.high)),
    (["dirty water", "contaminat", "muddy water", "smelly water"],
     dict(t="contaminated_water", a="water_pipeline", sev=Severity.high, health=True)),
    (["waterlog", "flood", "knee deep", "water logging"],
     dict(t="waterlogging", a="roadside_storm_drain", sev=Severity.high, road="arterial")),
    (["drain", "nala", "nallah", "choked drain"],
     dict(t="clogged_local_drain", a="local_open_drain", sev=Severity.medium)),
    (["pothole", "broken road", "road broken"],
     dict(t="pothole_local_road", a="local_lane", sev=Severity.medium, safety=True)),
    (["footpath", "pavement"],
     dict(t="broken_footpath", a="footpath", sev=Severity.low)),
    (["garbage", "trash", "kachra", "waste not", "bin overflow"],
     dict(t="garbage_not_collected", a="community_bin", sev=Severity.medium)),
    (["dump", "dumping", "malba", "debris"],
     dict(t="illegal_dumping", a="garbage_blackspot", sev=Severity.medium)),
    (["streetlight", "street light", "light not", "dark street"],
     dict(t="streetlight_not_working", a=None, sev=Severity.low, safety=True)),
    (["tree fell", "tree fallen", "branch", "tree hazard"],
     dict(t="tree_hazard", a="tree", sev=Severity.medium, safety=True)),
    (["park", "playground", "garden"],
     dict(t="park_maintenance_issue", a="park", sev=Severity.low)),
    (["encroach", "illegal shop", "vendor blocking"],
     dict(t="footpath_encroachment", a="footpath", sev=Severity.medium)),
    (["obstruction", "blocking road", "road blocked"],
     dict(t="road_obstruction", a="road_row", sev=Severity.medium, safety=True)),
    (["stray dog", "dog bite", "monkey"],
     dict(t="stray_dog_issue", a=None, sev=Severity.medium, health=True)),
    (["dead animal", "carcass", "dead dog", "dead cow"],
     dict(t="dead_animal", a=None, sev=Severity.medium, health=True)),
]


def _match(text: str) -> dict:
    low = text.lower()
    for keywords, meta in _RULES:
        if any(k in low for k in keywords):
            return meta
    return dict(t="garbage_not_collected", a=None, sev=Severity.low)


def _title(text: str, issue_type: str) -> str:
    snippet = re.sub(r"\s+", " ", text).strip()[:60]
    return snippet or issue_type.replace("_", " ").title()


class StubLLMClient:
    async def analyze_complaint(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
        text = inp.text or inp.category_hint or ""
        m = _match(text)
        issue_type = m["t"]
        # arterial heuristic: bump local pothole -> major if text says ring road / highway
        if issue_type == "pothole_local_road" and re.search(
            r"ring road|highway|flyover|nh-?\d|arterial|main road", text.lower()
        ):
            issue_type, m = "pothole_major_road", {**m, "road": "arterial", "a": "arterial_road"}

        return ComplaintAnalysis(
            title=_title(text, issue_type),
            summary=f"Citizen-reported {issue_type.replace('_', ' ')}." + (f" {text[:140]}" if text else ""),
            issue_category=category_for_type(issue_type) or "garbage_sanitation",
            issue_type=issue_type,
            asset_type=m.get("a"),
            severity=m.get("sev", Severity.medium),
            health_hazard_flag=bool(m.get("health")),
            public_safety_flag=bool(m.get("safety")),
            obstruction_flag="obstruct" in text.lower() or "blocking" in text.lower(),
            road_class=m.get("road"),
            drain_type=m.get("drain"),
            confidence=0.6 if text else 0.3,
            needs_manual_review=not bool(text),
        )

    async def embed(self, text: str) -> list[float]:
        """Deterministic pseudo-embedding from a hash — same text -> same vector.
        Good enough for the duplicate-scoring seam to function offline."""
        out: list[float] = []
        seed = text.lower().encode("utf-8")
        i = 0
        while len(out) < EMBEDDING_DIM:
            h = hashlib.sha256(seed + str(i).encode()).digest()
            out.extend((b - 128) / 128.0 for b in h)
            i += 1
        return out[:EMBEDDING_DIM]

    async def summarize(self, prompt: str) -> str:
        return f"[stub-summary] {prompt[:200]}"
