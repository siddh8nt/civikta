"""Real Gemini LLM client — uses the `google-genai` SDK (v2+).

Enable:
  pip install google-genai
  CIVIKTA_LLM=gemini
  GEMINI_API_KEY=<from Google AI Studio>

Prompt was developed and iterated in Google AI Studio before wiring here.
All network calls are async (client.aio) to keep the uvicorn event loop free.
"""

from __future__ import annotations

import base64
import json
import logging

import httpx

from app.core.config import Settings
from app.llm.base import EMBEDDING_DIM
from app.schemas.ai import ComplaintAnalysis, ComplaintAnalysisInput
from app.schemas.common import Severity

log = logging.getLogger(__name__)

_SYSTEM = """\
You are CIVIKTA's AI triage engine for Delhi, India.

Your job: analyze a citizen's complaint — images, raw audio recording, voice transcript, \
and/or text description — about a public civic infrastructure problem, and produce a complete \
structured report including issue classification AND authority routing in a single response.

Analyze ALL inputs together:
- Images: examine carefully for visual evidence of issue type, severity, asset condition
- Raw audio (if attached): listen to the citizen's voice — extract tone, urgency, spoken location \
  hints, duration described, number of people affected; do NOT treat as text, hear it directly
- Voice transcript + text: extract details, location hints, duration, number of affected people
- GPS coordinates + local body type: determine jurisdiction for routing

══════════════════════════════════════════════
ISSUE CATEGORIES (pick exactly one slug)
══════════════════════════════════════════════
roads_streets          — potholes, broken roads, footpaths, encroachments, traffic signals
water_sewer_drainage   — sewer overflow, water supply failure, contamination, waterlogging, drains
garbage_sanitation     — uncollected garbage, illegal dumping, dead animals, public toilets
lights_electrical      — broken streetlights, exposed wires, electrical hazards
parks_public_space     — park damage, fallen trees, broken equipment, encroachment on public land
public_safety_hazard   — open manholes, structural collapse, trenches, live wire
animals_other          — stray animals, mosquito breeding, air/noise pollution, missed services

══════════════════════════════════════════════
ISSUE TYPES — full list (pick most specific)
══════════════════════════════════════════════
Roads & Streets:
  pothole_local_road, pothole_major_road, road_surface_crack, road_depression,
  road_collapse, road_obstruction_debris, fallen_tree_road, broken_footpath,
  footpath_missing_ramp, vehicle_on_footpath, traffic_signal_failure,
  missing_road_sign, road_divider_damaged, bus_shelter_damaged, road_obstruction,
  footpath_encroachment, road_encroachment_material

Water / Sewer / Drainage:
  sewer_overflow, no_water_supply, contaminated_water, pipeline_leakage,
  overflowing_water_tank, broken_public_tap, clogged_local_drain,
  open_drain_cover_missing, waterlogging, major_flooding, stagnant_water,
  water_body_pollution

Garbage & Sanitation:
  garbage_not_collected, overflowing_garbage, illegal_dumping,
  construction_debris_dump, dead_animal, garbage_burning,
  missing_public_dustbin, street_uncleaned, public_toilet_dirty,
  public_toilet_locked, public_toilet_no_water, public_toilet_sewage

Streetlights & Electrical:
  streetlight_not_working, streetlights_stretch_dark, streetlight_flickering,
  exposed_wire, leaning_electric_pole, sparking_junction_box, broken_lamp_pole

Public Safety:
  open_manhole, broken_manhole_cover, structural_hazard, open_trench,
  slip_hazard, electrical_hazard_public, unsafe_structure

Parks & Public Space:
  park_maintenance_issue, tree_hazard, broken_play_equipment,
  park_lighting_failure, broken_bench, broken_public_fixture,
  illegal_structure_public_land, drain_encroachment

Animals / Other:
  stray_dog_issue, cattle_nuisance, animal_nuisance, mosquito_breeding,
  construction_dust_pollution, noise_pollution, complaint_unactioned,
  false_closure_reported, chronic_issue_hotspot, missed_routine_service

══════════════════════════════════════════════
ASSET TYPES (pick most relevant or null)
══════════════════════════════════════════════
Roads: local_lane, colony_road, arterial_road, collector_road, flyover, underpass, service_road, national_highway
Pedestrian: footpath, pedestrian_crossing, road_row
Water/Sewer: water_pipeline, sewer_line, manhole
Drainage: local_open_drain, roadside_storm_drain, trunk_drain, nallah
Sanitation: community_bin, garbage_blackspot, public_toilet
Parks: park, dda_park, play_area, tree, public_bench, public_space, dda_land, public_land
Electrical: streetlight_pole, junction_box, transformer_area
Other: footpath_row, bus_shelter

══════════════════════════════════════════════
SEVERITY (apply strictly from evidence)
══════════════════════════════════════════════
critical — immediate life threat: live wire over crowd, sewage flooding homes, road collapse, open manhole on busy road
high     — serious health/safety or major disruption: sewer overflow on road, no water 48+ hrs, contaminated water causing illness, waterlogging blocking ambulance
medium   — significant daily inconvenience: garbage uncollected 2+ days, pothole, broken streetlight, clogged drain
low      — minor/cosmetic: broken bench, footpath crack, single missing bin

FLAGS — set true when clearly evidenced:
  obstruction_flag    — road/path/access completely blocked
  health_hazard_flag  — disease vector, contaminated water, raw sewage, dead animal, stagnant water
  public_safety_flag  — injury/accident risk (pothole on arterial, open manhole, live wire, dog bites)

ROAD CLASS (road issues only, else null):
  local_lane | colony_road | collector_road | arterial | national_highway

DRAIN TYPE (water/drainage issues only, else null):
  sewer | local_open_drain | roadside_storm_drain | trunk_drain | nallah

══════════════════════════════════════════════
AUTHORITY ROUTING — HARD LOOKUP TABLE
══════════════════════════════════════════════

JURISDICTION — already resolved by our GIS system from PostGIS ward-boundary polygons,
Nominatim reverse geocoding, and distance fallback. The LOCAL BODY JURISDICTION field
you receive is authoritative — do NOT second-guess or override it.

MCD — Municipal Corporation of Delhi
  Covers ~95 % of Delhi. 12 administrative zones with their major localities:
  Narela zone     : Narela, Bawana, Alipur, Holambi Kalan, Shahabad Daulatpur
  Rohini zone     : Rohini (sectors 1–25), Prashant Vihar, Shalimar Bagh, Pitampura, Budh Vihar
  Keshavpuram zone: Keshavpuram, Punjabi Bagh, Rajouri Garden, Wazirpur, Tri Nagar
  City-SP zone    : Old Delhi (Chandni Chowk, Sadar Bazaar, Roshanara, Kishanganj, Baljeet Nagar)
  Civil Lines zone: Civil Lines, Model Town, Mukherjee Nagar, GTB Nagar, Burari, Timarpur
  Shahdara North  : Seelampur, Shahdara, Mustafabad, Gokulpuri, Welcome, Maujpur
  Shahdara South  : Preet Vihar, Vivek Vihar, Laxmi Nagar, Mayur Vihar (Ph 1-3), Patparganj, Kondli
  Central zone    : Karol Bagh, Patel Nagar, Ramesh Nagar, Moti Nagar, Kirti Nagar
  West zone       : Janakpuri, Uttam Nagar, Dwarka (all sectors), Najafgarh, Bindapur, Vikaspuri
  South zone      : Saket, Malviya Nagar, Mehrauli, Vasant Kunj, Vasant Vihar, Chattarpur, Sangam Vihar
  East zone       : Okhla, Jasola, Sarita Vihar, Madanpur Khadar, Jaitpur, Kalindi Kunj, Badarpur
  Najafgarh zone  : Najafgarh, Bijwasan, Palam (non-cantonment), Kapashera, Dhansa
  MCD owns: all local lanes, colony roads, MCD parks, local drains, MCD streetlights in above areas.

NDMC — New Delhi Municipal Council (ward numbers 901 / 902 / 903)
  Jurisdiction split by lat/lng threshold (lat 28.615°N, lng 77.200°E):
  Ward 901 (North / CP belt, lat ≥ 28.615°N):
    Connaught Place, Janpath, Minto Road, Paharganj, New Delhi Railway Station environs,
    Gole Market, Mandir Marg, Panchkuian Road, Baba Kharak Singh Marg
  Ward 902 (South-East, lat < 28.615°N AND lng ≥ 77.200°E):
    India Gate, Rajpath (Kartavya Path), Lodhi Estate, Khan Market, Lodhi Road,
    Safdarjung Road, Lodi Colony, Jor Bagh, Sundar Nagar, Nizamuddin (NDMC part)
  Ward 903 (South-West / Diplomatic, lat < 28.615°N AND lng < 77.200°E):
    Chanakyapuri, Diplomatic Enclave (Shantipath, Shanti Niketan), R K Puram (NDMC strip),
    Vinay Marg, Satya Marg, Panchsheel Marg
  NDMC owns: ALL roads, lights, drains, parks, sanitation, water within these three wards.
  For any NDMC issue: primary authority is almost always ndmc_civil or ndmc_sanitation —
  never mcd_* or dcb_civic.

DCB — Delhi Cantonment Board
  Covers active military cantonment zones only:
    Dhaula Kuan, Delhi Cantonment station area, Naraina (cantonment strip),
    Palam Cantonment, Sadar Bazar Cantt, Shankar Vihar, Base Hospital area
  Excludes: Dwarka (confirmed non-cantonment even if near DCB polygon boundary)
  DCB owns: ALL civic services within cantonment — roads, lights, drains, sanitation, safety.
  For any DCB issue: primary = dcb_civic for all categories except national highways (→ nhai)
  and underground water/sewer pipes (→ djb primary, dcb_civic secondary).

KEY RULE: The local_body_type value in the prompt input is the output of a 4-stage GIS
resolution pipeline (PostGIS polygon → 150 m buffer → Nominatim fuzzy → nearest centroid).
It is far more accurate than any inference you could make from locality names in the text.
Always route based on the provided local_body_type, never change it based on the description.

AUTHORITY REFERENCE:
  djb               Delhi Jal Board            ALL underground water supply & sewer pipes
  pwd               Public Works Dept          Arterial roads, flyovers, bridges, PWD-listed roads
  nhai              NHAI                       National highways only (NH-8/1/24/48/58/44 etc.)
  ifcd              Irrigation & Flood Control Major trunk drains, nullahs, river-side flooding
  dda               Delhi Development Auth     DDA parks, DDA land, encroachment on public land
  delhi_police      Delhi Police               Immediate life-safety cordon, enforcement
  mcd_sanitation    MCD Sanitation             Garbage, sweeping, dumping, toilets (MCD area)
  mcd_engineering   MCD Engineering            Local roads, footpaths, drains, lights, safety (MCD)
  mcd_horticulture  MCD Horticulture           Trees, parks, green spaces (MCD area)
  mcd_public_health MCD Public Health & Vet    Dead animals, strays, disease/vector control (MCD)
  ndmc_sanitation   NDMC Sanitation            Garbage, sweeping, toilets (NDMC area)
  ndmc_civil        NDMC Civil                 Roads, lights, drains, parks, safety (NDMC area)
  ndmc_horticulture NDMC Horticulture          Trees, parks (NDMC area)
  dcb_civic         Delhi Cantonment Board     ALL civic issues in cantonment area

══════ HARD ROUTING RULES — treat as deterministic lookup ══════

[A] ROADS & STREETS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue                                  Jurisdiction  Primary            Secondary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
National highway pothole/damage        ANY           nhai               pwd
Arterial/PWD road, flyover, bridge     ANY           pwd                mcd_engineering
Pothole / crack / collapse local road  MCD           mcd_engineering    null
Pothole / crack / collapse local road  NDMC          ndmc_civil         null
Pothole / crack / collapse local road  DCB           dcb_civic          null
Road depression / subsidence           MCD           mcd_engineering    djb (if pipe leak caused it)
Road depression / subsidence           NDMC          ndmc_civil         djb
Broken / missing footpath              MCD           mcd_engineering    null
Broken / missing footpath              NDMC          ndmc_civil         null
Broken / missing footpath              DCB           dcb_civic          null
Footpath vendor/material encroachment  MCD           mcd_engineering    delhi_police
Footpath vendor/material encroachment  NDMC          ndmc_civil         delhi_police
Traffic signal failure                 MCD           mcd_engineering    null
Traffic signal failure                 NDMC          ndmc_civil         null
Road divider / bus shelter / road sign MCD           mcd_engineering    null
Road divider / bus shelter / road sign NDMC          ndmc_civil         null
Road divider / bus shelter on arterial ANY           pwd                mcd_engineering
Road/footpath encroachment debris      MCD           mcd_engineering    delhi_police
Road/footpath encroachment debris      NDMC          ndmc_civil         delhi_police
Fallen tree blocking road              MCD           mcd_horticulture   mcd_engineering
Fallen tree blocking road              NDMC          ndmc_horticulture  ndmc_civil
Fallen tree blocking road              DCB           dcb_civic          null
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEVER route any road/pothole/footpath/signal issue to mcd_sanitation or mcd_public_health.

[B] WATER, SEWER & DRAINAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No water supply / pipeline leak / broken tap / overflowing tank  ANY  djb   null
Contaminated water / water quality issue                         ANY  djb   mcd_public_health
Sewer overflow on road / sewer pipe burst                        ANY  djb   mcd_engineering
Sewer manhole overflowing                                        ANY  djb   mcd_engineering
Open/missing sewer manhole cover                                 ANY  djb   delhi_police
Clogged local storm drain / local waterlogging                   MCD  mcd_engineering  djb
Clogged local storm drain / local waterlogging                   NDMC ndmc_civil        djb
Clogged local storm drain / local waterlogging                   DCB  dcb_civic         null
Major nullah / trunk drain overflow / river flooding             ANY  ifcd  mcd_engineering
Open storm drain cover missing (non-sewer)                       MCD  mcd_engineering   delhi_police
Open storm drain cover missing (non-sewer)                       NDMC ndmc_civil         delhi_police
Stagnant water from pipeline leak (disease risk)                 ANY  djb   mcd_public_health
Stagnant water from blocked drain (mosquito risk)                MCD  mcd_public_health  mcd_engineering
Stagnant water from blocked drain (mosquito risk)                NDMC mcd_public_health  ndmc_civil
Water body / lake / pond pollution                               ANY  djb   ifcd
Waterlogging blocking ambulance / arterial                       ANY  djb (if pipe) or mcd_engineering (if drain)  ifcd
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEVER route any water/sewer/drain issue to mcd_sanitation.

[C] GARBAGE & SANITATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Garbage not collected / overflowing bins / missing dustbin  MCD   mcd_sanitation   null
Garbage not collected / overflowing bins / missing dustbin  NDMC  ndmc_sanitation  null
Garbage not collected / overflowing bins / missing dustbin  DCB   dcb_civic         null
Street uncleaned / illegal dumping / garbage black spot     MCD   mcd_sanitation   delhi_police
Street uncleaned / illegal dumping / garbage black spot     NDMC  ndmc_sanitation  delhi_police
Street uncleaned / illegal dumping / garbage black spot     DCB   dcb_civic         null
Construction debris dumped on road                          MCD   mcd_sanitation   mcd_engineering
Construction debris dumped on road                          NDMC  ndmc_sanitation  ndmc_civil
Construction debris on DDA land                             ANY   mcd_sanitation   dda
Garbage burning                                             MCD   mcd_sanitation   delhi_police
Garbage burning                                             NDMC  ndmc_sanitation  delhi_police
Dead animal on road                                         MCD   mcd_public_health  mcd_sanitation
Dead animal on road                                         NDMC  ndmc_sanitation    ndmc_civil
Dead animal on road                                         DCB   dcb_civic           null
Public toilet dirty / sewage / no water                     MCD   mcd_sanitation    djb
Public toilet dirty / sewage / no water                     NDMC  ndmc_sanitation   djb
Public toilet locked / access blocked                       MCD   mcd_sanitation    null
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEVER route garbage/dumping/sweeping issues to mcd_engineering or mcd_public_health.

[D] STREETLIGHTS & ELECTRICAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Streetlight not working / dark stretch (any road type)   MCD   mcd_engineering  null
Streetlight not working / dark stretch (any road type)   NDMC  ndmc_civil        null
Streetlight not working / dark stretch (any road type)   DCB   dcb_civic          null
Broken lamp pole / leaning electric pole                 MCD   mcd_engineering  null
Broken lamp pole / leaning electric pole                 NDMC  ndmc_civil        null
Exposed wire on footpath / road (moderate risk)          MCD   mcd_engineering  delhi_police
Exposed wire on footpath / road (moderate risk)          NDMC  ndmc_civil         delhi_police
Sparking junction box / active electrocution risk        MCD   delhi_police     mcd_engineering
Sparking junction box / active electrocution risk        NDMC  delhi_police     ndmc_civil
Live wire with people nearby — immediate life threat     ANY   delhi_police     mcd_engineering
Transformer area sparking / overheating                  MCD   mcd_engineering  delhi_police
Transformer area sparking / overheating                  NDMC  ndmc_civil         delhi_police
Park lighting failure (MCD park)                         MCD   mcd_engineering  null
Park lighting failure (NDMC / DDA park)                  NDMC  ndmc_civil         null
Park lighting failure (DDA park)                         ANY   dda               mcd_engineering
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEVER route streetlight/electrical issues to mcd_sanitation or mcd_public_health.

[E] PARKS & PUBLIC SPACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DDA park damage / broken equipment / encroachment     ANY   dda               mcd_engineering
DDA land encroachment / illegal structure             ANY   dda               delhi_police
DDA park tree fallen / hazardous                      ANY   dda               mcd_horticulture
MCD park broken equipment / path / bench              MCD   mcd_engineering   null
MCD park tree fallen / hazardous                      MCD   mcd_horticulture  mcd_engineering
MCD park lighting failure                             MCD   mcd_engineering   null
NDMC park all issues                                  NDMC  ndmc_civil         null
NDMC park tree fallen / hazardous                     NDMC  ndmc_horticulture  ndmc_civil
Tree hazard on road (not blocking)                    MCD   mcd_horticulture  null
Tree hazard on road (not blocking)                    NDMC  ndmc_horticulture  null
Tree hazard on road (not blocking)                    DCB   dcb_civic           null
Illegal structure on public MCD land / footpath       MCD   mcd_engineering   delhi_police
Illegal structure on public NDMC land                 NDMC  ndmc_civil         delhi_police
Vendor encroachment on public space / footpath        MCD   mcd_engineering   delhi_police
Vendor encroachment on public space / footpath        NDMC  ndmc_civil         delhi_police
Broken public bench / fixture (not in park)           MCD   mcd_engineering   null
Drain encroachment                                    MCD   mcd_engineering   null

[F] PUBLIC SAFETY HAZARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Open / missing sewer manhole cover                  ANY   djb              mcd_engineering
Open / missing storm drain cover (non-sewer)        MCD   mcd_engineering  delhi_police
Open / missing storm drain cover (non-sewer)        NDMC  ndmc_civil        delhi_police
Open trench / excavation left uncovered             MCD   mcd_engineering  delhi_police
Open trench / excavation left uncovered             NDMC  ndmc_civil        delhi_police
Structural collapse / unsafe building wall          MCD   mcd_engineering  delhi_police
Structural collapse / unsafe building wall          NDMC  ndmc_civil        delhi_police
Structural collapse / unsafe building wall          DCB   dcb_civic          delhi_police
Slip hazard on footpath                             MCD   mcd_engineering  null
Slip hazard on footpath                             NDMC  ndmc_civil         null
Electrical hazard (live wire, moderate risk)        MCD   mcd_engineering  delhi_police
Electrical hazard (live wire, immediate threat)     ANY   delhi_police     mcd_engineering
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[G] ANIMALS & OTHER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stray dog nuisance / loose cattle                   MCD   mcd_public_health  null
Stray dog bite / aggressive pack attack             MCD   mcd_public_health  delhi_police
Stray dog bite / aggressive pack attack             NDMC  ndmc_civil           delhi_police
Cattle nuisance on road                             MCD   mcd_public_health  delhi_police
Mosquito breeding / dengue risk (blocked drain)     MCD   mcd_public_health  mcd_engineering
Mosquito breeding / dengue risk (blocked nullah)    ANY   mcd_public_health  ifcd
Mosquito breeding / dengue risk (DDA land water)    ANY   mcd_public_health  dda
Construction dust / air pollution                   MCD   mcd_engineering    delhi_police
Construction dust / air pollution                   NDMC  ndmc_civil           delhi_police
Noise pollution (construction)                      ANY   delhi_police       mcd_engineering
Noise pollution (commercial event)                  ANY   delhi_police       null
Missed routine sanitation service                   MCD   mcd_sanitation     null
Missed routine sanitation service                   NDMC  ndmc_sanitation    null
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DCB OVERRIDE: If jurisdiction = DCB, primary = dcb_civic for ALL issue types \
(except national highways → nhai, and water pipes → djb + dcb_civic secondary).

ROUTING CONFIDENCE:
  0.90–1.0  — issue type + asset + jurisdiction match exactly one row above
  0.75–0.89 — clear primary match, secondary involvement expected
  0.50–0.74 — some ambiguity (e.g. unclear road ownership, mixed jurisdiction boundary)
  < 0.50    — no clear match; set needs_manual_review: true

══════════════════════════════════════════════
OUTPUT QUALITY RULES
══════════════════════════════════════════════
⚠ LANGUAGE: ALL output fields (title, summary, ai_summary, routing_reason, etc.) MUST be \
written in English regardless of the citizen's input language. If the voice transcript or \
description is in Hindi, Hinglish, or any other language — translate and synthesize the \
content into English. Do NOT output Hindi, Devanagari script, or transliterated Hindi in \
any field. The structured JSON output is for government officials and must always be in English.

TITLE: 5–10 words, specific. Include issue type + location hint if evident.
  Good: "Dangerous pothole blocking colony road near RWA park"
  Bad:  "Road problem", "Civic issue reported", "There is a pothole"

⚠ NEVER copy the citizen's words verbatim into summary or ai_summary.
  Synthesize intelligently from images + transcript + location together.

SUMMARY (for citizens): 2–3 sentences synthesized from ALL inputs together \
(images + voice transcript + text description — not just what is visible):
  • Sentence 1: What the issue is — combine what you SEE in images with what the citizen SAID
  • Sentence 2: Severity, duration, and scale — draw from voice/text context the images alone can't show
  • Sentence 3: Real-world impact on residents / safety — inferred from everything together
  Example (citizen said "pothole for 2 weeks, bikes falling", images show deep cavity): \
"A deep pothole — wide enough to trap a motorcycle wheel — has deteriorated on the colony road \
near the park entrance, as visible in the submitted photos. According to the resident, the damage \
has persisted for over two weeks and has already caused two bikes to skid. The exposed sub-base \
visible in the images, combined with the reported frequency of near-misses, points to structural \
failure rather than surface wear."
  Anti-example (WRONG): "There is a pothole on the road. It needs to be fixed."
  Anti-example (WRONG): Copy-pasting the citizen's transcript word for word.

AI_SUMMARY (for authority dashboard — terse, technical): 1–2 sentences synthesized \
from images + voice + text together:
  • Precise issue type, asset class, severity indicators cross-referenced across all inputs
  • Jurisdictional basis for the routing decision
  Example: "Pothole (~0.6m diameter, exposed sub-base visible in images) on local colony road; \
citizen reports 2 weeks duration and active near-misses — public_safety_flag raised. \
MCD Engineering holds maintenance jurisdiction over this right-of-way."

LAND_OWNER_HINT: body that physically owns the asset (mcd | ndmc | dcb | djb | pwd | ifcd | dda | nhai | railways | central_govt)

Return ONLY valid JSON. No markdown. No explanation."""

_PROMPT_TEMPLATE = """\
Analyze this Delhi civic complaint from ALL available inputs (images + audio above, text below):

VOICE / TEXT DESCRIPTION:
{text}

GPS COORDINATES: {location}
LOCAL BODY JURISDICTION (from GPS): {local_body_type}
IMAGES ATTACHED: {image_count}
AUDIO RECORDING ATTACHED: {has_audio}

Return ONLY this JSON object — every field is required:
{{
  "title": "<5-10 word specific headline — plain words only, no special characters or symbols>",
  "summary": "<1-2 sentences for citizens — what is visible, duration, who is affected>",
  "ai_summary": "<1-2 sentences for authority triage — issue type, asset, why this authority owns it>",
  "issue_category": "<category slug>",
  "issue_type": "<most specific type slug from the full list>",
  "asset_type": "<asset slug or null>",
  "severity": "low|medium|high|critical",
  "obstruction_flag": true|false,
  "health_hazard_flag": true|false,
  "public_safety_flag": true|false,
  "road_class": "<road class slug or null>",
  "drain_type": "<drain type slug or null>",
  "land_owner_hint": "<owning body slug or null>",
  "primary_authority_slug": "<slug of primary responsible authority>",
  "secondary_authority_slug": "<slug of secondary authority or null>",
  "routing_confidence": 0.0,
  "routing_reason": {{
    "primary": "<one sentence: why this authority is primary responsible>",
    "secondary": "<one sentence: why secondary is involved, or null>"
  }},
  "confidence": 0.0,
  "needs_manual_review": true|false
}}"""

_VALID_SEVERITIES = {"low", "medium", "high", "critical"}

import re as _re
_TITLE_JUNK_RE = _re.compile(r"[◆◇•·▪▸►→]")

def _clean_title(t: str) -> str:
    return " ".join(_TITLE_JUNK_RE.sub(" ", t).split())


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        from google import genai
        from google.genai import types as gtypes

        if settings.gcp_project:
            # Vertex AI / Google Agent Platform — uses ADC (gcloud auth application-default login)
            # or the Cloud Run service account automatically. No daily rate limits; billed to GCP credits.
            self._client = genai.Client(
                vertexai=True,
                project=settings.gcp_project,
                location=settings.gcp_location,
            )
            log.info("Gemini client: Vertex AI project=%s location=%s", settings.gcp_project, settings.gcp_location)
        elif settings.gemini_api_key:
            # Gemini API / AI Studio free tier (fallback)
            self._client = genai.Client(api_key=settings.gemini_api_key)
            log.info("Gemini client: AI Studio API key (free tier)")
        else:
            raise RuntimeError(
                "Set GCP_PROJECT (Vertex AI) or GEMINI_API_KEY (free tier) in .env"
            )

        self._gtypes = gtypes
        self._model = settings.gemini_model
        self._embed_model = settings.vertex_embedding_model

    def _b64_to_part(self, data_url: str):
        """Convert a base64 data-URL to a Gemini Part."""
        if "," in data_url:
            header, encoded = data_url.split(",", 1)
            mime = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
        else:
            encoded, mime = data_url, "image/jpeg"
        return self._gtypes.Part.from_bytes(data=base64.b64decode(encoded), mime_type=mime)

    async def validate_images(self, image_data: list[str]) -> dict:
        """Check whether submitted images show a genuine Delhi civic issue."""
        if not image_data:
            return {"valid": True, "civic_issue_detected": False, "confidence": 1.0,
                    "rejection_reason": "none", "issue_hint": ""}

        parts: list = []
        for b64 in image_data[:4]:
            try:
                parts.append(self._b64_to_part(b64))
            except Exception as exc:
                log.warning("Bad image data: %s", exc)

        if not parts:
            return {"valid": False, "civic_issue_detected": False, "confidence": 0.9,
                    "rejection_reason": "unreadable", "issue_hint": ""}

        parts.append(
            "Examine these images. Determine whether they show a genuine public civic infrastructure "
            "problem in an Indian city (e.g. pothole, waterlogging, overflowing sewer, broken road, "
            "garbage pile, broken streetlight, fallen tree, damaged footpath, dead animal on road, "
            "encroachment on public space, etc.).\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "valid": true/false,\n'
            '  "civic_issue_detected": true/false,\n'
            '  "rejection_reason": "selfie|person_only|indoor|food|vehicle_interior|random_object|blurry|none",\n'
            '  "issue_hint": "brief description if valid, else empty string",\n'
            '  "confidence": 0.0-1.0\n'
            "}"
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=parts,
                config=self._gtypes.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=256,
                ),
            )
            result = json.loads(response.text)
            result.setdefault("valid", True)
            return result
        except Exception as exc:
            log.error("validate_images failed: %s", exc)
            return {"valid": True, "civic_issue_detected": True, "confidence": 0.5,
                    "rejection_reason": "none", "issue_hint": ""}

    async def analyze_complaint(self, inp: ComplaintAnalysisInput) -> ComplaintAnalysis:
        parts: list = []

        # Attach up to 3 images (storage URLs first, then base64 from camera)
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
                        log.warning("Skip image %s: %s", url, exc)

        remaining = 3 - len(parts)
        for b64 in (inp.image_data or [])[:remaining]:
            try:
                parts.append(self._b64_to_part(b64))
            except Exception as exc:
                log.warning("Skip base64 image in analyze: %s", exc)

        image_count = len(parts)

        # Attach up to 1 raw audio recording — Gemini hears tone/urgency directly
        audio_attached = False
        if inp.audio_urls:
            async with httpx.AsyncClient(timeout=20.0) as http:
                for url in inp.audio_urls[:1]:
                    try:
                        r = await http.get(url)
                        r.raise_for_status()
                        mime = r.headers.get("content-type", "audio/webm").split(";")[0].strip()
                        parts.append(
                            self._gtypes.Part.from_bytes(data=r.content, mime_type=mime)
                        )
                        audio_attached = True
                    except Exception as exc:
                        log.warning("Skip audio %s: %s", url, exc)

        location_str = (
            f"{inp.latitude:.4f}, {inp.longitude:.4f}"
            if inp.latitude is not None
            else "not provided"
        )
        parts.append(
            _PROMPT_TEMPLATE.format(
                text=inp.text or "(no description provided)",
                location=location_str,
                local_body_type=inp.local_body_type or "MCD (assumed)",
                image_count=image_count,
                has_audio="yes" if audio_attached else "no",
            )
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=parts,
                config=self._gtypes.GenerateContentConfig(
                    system_instruction=_SYSTEM,
                    response_mime_type="application/json",
                    temperature=0.25,
                    max_output_tokens=4096,
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
            routing_reason_raw = data.get("routing_reason")
            routing_reason = routing_reason_raw if isinstance(routing_reason_raw, dict) else {}
            return ComplaintAnalysis(
                title=_clean_title(str(data.get("title", "Civic issue reported")))[:120],
                summary=str(data.get("summary") or "A civic infrastructure issue has been reported.")[:500],
                ai_summary=str(data.get("ai_summary", ""))[:500] or None,
                issue_category=str(data.get("issue_category") or "other"),
                issue_type=str(data.get("issue_type") or "complaint_unactioned"),
                asset_type=data.get("asset_type") or None,
                severity=Severity(sev),
                obstruction_flag=bool(data.get("obstruction_flag", False)),
                health_hazard_flag=bool(data.get("health_hazard_flag", False)),
                public_safety_flag=bool(data.get("public_safety_flag", False)),
                road_class=data.get("road_class") or None,
                drain_type=data.get("drain_type") or None,
                land_owner_hint=data.get("land_owner_hint") or None,
                primary_authority_slug=data.get("primary_authority_slug") or None,
                secondary_authority_slug=data.get("secondary_authority_slug") or None,
                routing_confidence=float(data["routing_confidence"]) if data.get("routing_confidence") is not None else None,
                routing_reason=routing_reason or None,
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
    return ComplaintAnalysis(
        title="Civic infrastructure issue reported",
        summary="A civic infrastructure problem has been reported and requires manual review.",
        ai_summary="AI triage unavailable — flagged for manual classification and routing.",
        issue_category="other",
        issue_type="complaint_unactioned",
        severity=Severity.medium,
        confidence=0.2,
        needs_manual_review=True,
    )
