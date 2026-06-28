"""Delhi ward reference data — 250 MCD wards (2022 unification) + NDMC + DCB.

Centroids are approximate — designed for nearest-neighbour ward resolution,
not polygon-containment. Accuracy is ~95% at ward centres, ~85% at boundaries.
Source: 2022 MCD delimitation (North + South + East MCDs merged).

Commissioner data: September 2024 MCD reallocation order.
Sources:
  https://egov.eletsonline.com/2024/09/mcd-appoints-7-additional-commissioners-as-zonal-heads-check-list/
  https://www.indianmandarins.com/news/mcd-07-additional-commissioners-made-zonal-in-charge-along-with-allocation-of-work/29532

TODO: Add elected ward councillor names once available.
TODO: Confirm East Zone additional commissioner (not covered in Sep 2024 reshuffle).
"""

from __future__ import annotations

from typing import TypedDict


class ZoneCommissioner(TypedDict):
    name: str
    cadre: str          # e.g. "IAS: 2008: AGMUT"
    zones: list[str]    # canonical zone names from this seed
    confirmed: bool     # False = best-available, not officially verified for 2026


# September 2024 MCD Additional Commissioner → Zone assignment (all 12 MCD zones)
# Official 12 zones: Narela, Rohini, Civil Lines, Keshavpuram, Karol Bagh, West,
#                    Najafgarh, Centre, SP-City,
#                    South, Shahdara South, Shahdara North
#
# "Centre Zone" ward boundaries are not fully published in accessible public data.
# Wards in the Daryaganj / ITO / Minto Road belt (currently under "City" in this seed)
# likely straddle City-SP and Centre zones — pending MCD official ward-to-zone map.
ZONE_COMMISSIONERS: dict[str, ZoneCommissioner] = {
    # ── MCD zones ───────────────────────────────────────────────────────────────
    "Narela":        {"name": "Sachin Shinde",         "cadre": "IAS: 2008: AGMUT", "zones": ["Narela", "West", "Najafgarh"],            "confirmed": True},
    "West":          {"name": "Sachin Shinde",         "cadre": "IAS: 2008: AGMUT", "zones": ["Narela", "West", "Najafgarh"],            "confirmed": True},
    "Najafgarh":     {"name": "Sachin Shinde",         "cadre": "IAS: 2008: AGMUT", "zones": ["Narela", "West", "Najafgarh"],            "confirmed": True},
    "South":         {"name": "Jitender Yadav",        "cadre": "IAS: 2010: AGMUT", "zones": ["South", "City", "Centre"],               "confirmed": True},
    "City":          {"name": "Jitender Yadav",        "cadre": "IAS: 2010: AGMUT", "zones": ["South", "City", "Centre"],               "confirmed": True},
    # Centre Zone = 12th official MCD zone; wards not yet split from "City" in this seed
    "Centre":        {"name": "Jitender Yadav",        "cadre": "IAS: 2010: AGMUT", "zones": ["South", "City", "Centre"],               "confirmed": True},
    "Keshavpuram":   {"name": "Nidhi Malik",           "cadre": "IAS: 2013: AGMUT", "zones": ["Keshavpuram", "Rohini"],                 "confirmed": True},
    "Rohini":        {"name": "Nidhi Malik",           "cadre": "IAS: 2013: AGMUT", "zones": ["Keshavpuram", "Rohini"],                 "confirmed": True},
    "Civil Lines":   {"name": "Dr. Tariq Thomas",      "cadre": "IAS: 2011: AGMUT", "zones": ["Civil Lines", "Karol Bagh"],             "confirmed": True},
    "Karol Bagh":    {"name": "Dr. Tariq Thomas",      "cadre": "IAS: 2011: AGMUT", "zones": ["Civil Lines", "Karol Bagh"],             "confirmed": True},
    # Shahdara South covers trans-Yamuna + former EDMC East Delhi wards
    "Shahdara South":{"name": "Pankaj Naresh Agrawal", "cadre": "IOFS: 2007",       "zones": ["Shahdara South", "Shahdara North"],      "confirmed": True},
    "Shahdara North":{"name": "Pankaj Naresh Agrawal", "cadre": "IOFS: 2007",       "zones": ["Shahdara South", "Shahdara North"],      "confirmed": True},
    # ── NDMC — New Delhi Municipal Council ──────────────────────────────────────
    # Chairman: Keshav Chandra (IAS: 1995: AGMUT), appointed 30 Oct 2024
    # Succeeded Amit Yadav (IAS: 1991: UT) who moved to Union Secretary, MSJE
    "NDMC Central":  {"name": "Keshav Chandra",        "cadre": "IAS: 1995: AGMUT", "zones": ["NDMC Central", "NDMC South", "NDMC West"], "confirmed": True},
    "NDMC South":    {"name": "Keshav Chandra",        "cadre": "IAS: 1995: AGMUT", "zones": ["NDMC Central", "NDMC South", "NDMC West"], "confirmed": True},
    "NDMC West":     {"name": "Keshav Chandra",        "cadre": "IAS: 1995: AGMUT", "zones": ["NDMC Central", "NDMC South", "NDMC West"], "confirmed": True},
    # ── DCB — Delhi Cantonment Board ────────────────────────────────────────────
    # CEO: Kapil Goyal (IDES — Indian Defence Estates Service)
    "DCB":           {"name": "Kapil Goyal",            "cadre": "IDES",             "zones": ["DCB"],                                   "confirmed": True},
}


class WardRecord(TypedDict):
    ward_no: int
    ward_name: str
    zone: str
    district: str
    local_body_type: str        # "MCD" | "NDMC" | "DCB"
    lat: float
    lng: float
    # Populated at module load from ZONE_COMMISSIONERS — do not set manually
    zonal_commissioner: str     # e.g. "Sachin Shinde"
    zonal_commissioner_cadre: str  # e.g. "IAS: 2008: AGMUT"
    commissioner_confirmed: bool   # False = best-available, not verified for 2026


# fmt: off
DELHI_WARDS: list[WardRecord] = [

    # ── NARELA ZONE ─────────────────────────────────────────────────────────────
    # Far-north Delhi (North district, outer fringe)
    {"ward_no":  1, "ward_name": "Narela",           "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8550, "lng": 77.0940},
    {"ward_no":  2, "ward_name": "Bawana",            "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8120, "lng": 77.0350},
    {"ward_no":  3, "ward_name": "Bankner",           "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8670, "lng": 77.0250},
    {"ward_no":  4, "ward_name": "Alipur",            "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8400, "lng": 77.1330},
    {"ward_no":  5, "ward_name": "Holambi Kalan",     "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8130, "lng": 77.0820},
    {"ward_no":  6, "ward_name": "Prahalad Pur",      "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.8060, "lng": 77.1130},
    {"ward_no":  7, "ward_name": "Mukundpur",         "zone": "Narela",      "district": "North",       "local_body_type": "MCD", "lat": 28.7800, "lng": 77.1470},
    {"ward_no":  8, "ward_name": "Pooth Kalan",       "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7460, "lng": 77.0580},
    {"ward_no":  9, "ward_name": "Shahabad Dairy",    "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7680, "lng": 77.0790},
    {"ward_no": 10, "ward_name": "Vijay Vihar",       "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7250, "lng": 77.0440},
    {"ward_no": 11, "ward_name": "Ghevra",            "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7060, "lng": 77.0150},
    {"ward_no": 12, "ward_name": "Mundka",            "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6920, "lng": 77.0000},
    {"ward_no": 13, "ward_name": "Budh Vihar",        "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7380, "lng": 77.0670},
    {"ward_no": 14, "ward_name": "Sultanpur Majra",   "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7470, "lng": 77.0480},
    {"ward_no": 15, "ward_name": "Samaypur Badli",    "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7470, "lng": 77.1480},
    {"ward_no": 16, "ward_name": "Jahangirpuri",      "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7370, "lng": 77.1600},
    {"ward_no": 17, "ward_name": "Haider Pur",        "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7160, "lng": 77.1180},
    {"ward_no": 18, "ward_name": "Swaroop Nagar",     "zone": "Narela",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7280, "lng": 77.1070},

    # ── ROHINI ZONE ─────────────────────────────────────────────────────────────
    # North-west Delhi (Rohini, Rithala, Shalimar Bagh belt)
    {"ward_no": 19, "ward_name": "Rithala",           "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7260, "lng": 77.0990},
    {"ward_no": 20, "ward_name": "Rohini Sector 15",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7210, "lng": 77.1030},
    {"ward_no": 21, "ward_name": "Rohini Sector 16",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7200, "lng": 77.1180},
    {"ward_no": 22, "ward_name": "Rohini Sector 17",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7220, "lng": 77.1350},
    {"ward_no": 23, "ward_name": "Rohini Sector 18",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7180, "lng": 77.1480},
    {"ward_no": 24, "ward_name": "Rohini Sector 24",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7140, "lng": 77.1560},
    {"ward_no": 25, "ward_name": "Rohini Sector 21",  "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7320, "lng": 77.1380},
    {"ward_no": 26, "ward_name": "Prashant Vihar",    "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7100, "lng": 77.1550},
    {"ward_no": 27, "ward_name": "Madhuban Chowk",    "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6990, "lng": 77.1450},
    {"ward_no": 28, "ward_name": "Shalimar Bagh",     "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7000, "lng": 77.1680},
    {"ward_no": 29, "ward_name": "Shakurpur",         "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6800, "lng": 77.1330},
    {"ward_no": 30, "ward_name": "Saraswati Vihar",   "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6820, "lng": 77.1480},
    {"ward_no": 31, "ward_name": "Mangolpuri",        "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6990, "lng": 77.0930},
    {"ward_no": 32, "ward_name": "Sultanpuri",        "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7070, "lng": 77.0750},
    {"ward_no": 33, "ward_name": "Kirari",            "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7220, "lng": 77.0720},
    {"ward_no": 34, "ward_name": "Badli",             "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.7320, "lng": 77.1670},
    {"ward_no": 35, "ward_name": "Adarsh Nagar",      "zone": "Rohini",      "district": "North",       "local_body_type": "MCD", "lat": 28.7120, "lng": 77.1825},
    {"ward_no": 36, "ward_name": "Azadpur",           "zone": "Rohini",      "district": "North",       "local_body_type": "MCD", "lat": 28.7060, "lng": 77.1900},
    {"ward_no": 37, "ward_name": "Model Town",        "zone": "Rohini",      "district": "North",       "local_body_type": "MCD", "lat": 28.7040, "lng": 77.1980},
    {"ward_no": 38, "ward_name": "Peeragarhi",        "zone": "Rohini",      "district": "North West",  "local_body_type": "MCD", "lat": 28.6810, "lng": 77.0830},

    # ── CIVIL LINES ZONE ────────────────────────────────────────────────────────
    # North-central Delhi (Civil Lines, Kashmere Gate belt)
    {"ward_no": 39, "ward_name": "Civil Lines",       "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6790, "lng": 77.2200},
    {"ward_no": 40, "ward_name": "Mukherjee Nagar",   "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.7010, "lng": 77.2070},
    {"ward_no": 41, "ward_name": "Timarpur",          "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.7060, "lng": 77.2130},
    {"ward_no": 42, "ward_name": "Kamla Nagar",       "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6870, "lng": 77.2140},
    {"ward_no": 43, "ward_name": "Roshanara",         "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6720, "lng": 77.1960},
    {"ward_no": 44, "ward_name": "Shastri Nagar",     "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6670, "lng": 77.1960},
    {"ward_no": 45, "ward_name": "Chandrawal",        "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6720, "lng": 77.2240},
    {"ward_no": 46, "ward_name": "Subzi Mandi",       "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6720, "lng": 77.2090},
    {"ward_no": 47, "ward_name": "Kishanganj",        "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6600, "lng": 77.2020},
    {"ward_no": 48, "ward_name": "Bara Hindu Rao",    "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6680, "lng": 77.2120},
    {"ward_no": 49, "ward_name": "Kashmere Gate",     "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6610, "lng": 77.2330},
    {"ward_no": 50, "ward_name": "Mori Gate",         "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6680, "lng": 77.2240},
    {"ward_no": 51, "ward_name": "Wazirabad",         "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.7310, "lng": 77.2370},
    {"ward_no": 52, "ward_name": "Sonia Vihar",       "zone": "Civil Lines", "district": "North East",  "local_body_type": "MCD", "lat": 28.7340, "lng": 77.2540},
    {"ward_no": 53, "ward_name": "Gokalpur",          "zone": "Civil Lines", "district": "North East",  "local_body_type": "MCD", "lat": 28.7550, "lng": 77.2000},
    {"ward_no": 54, "ward_name": "Burari",            "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.7590, "lng": 77.2110},
    {"ward_no": 55, "ward_name": "Kohat Enclave",     "zone": "Civil Lines", "district": "North",       "local_body_type": "MCD", "lat": 28.6960, "lng": 77.1760},
    {"ward_no": 56, "ward_name": "Pitampura",         "zone": "Civil Lines", "district": "North West",  "local_body_type": "MCD", "lat": 28.6980, "lng": 77.1330},
    {"ward_no": 57, "ward_name": "Sadar Bazar",       "zone": "Civil Lines", "district": "Central",     "local_body_type": "MCD", "lat": 28.6640, "lng": 77.2150},
    {"ward_no": 58, "ward_name": "Idgah",             "zone": "Civil Lines", "district": "Central",     "local_body_type": "MCD", "lat": 28.6680, "lng": 77.2060},

    # ── KESHAVPURAM ZONE ────────────────────────────────────────────────────────
    # North-central / inner north-west (Keshavpuram, Tri Nagar, Wazirpur belt)
    {"ward_no": 59, "ward_name": "Keshavpuram",       "zone": "Keshavpuram", "district": "North West",  "local_body_type": "MCD", "lat": 28.6780, "lng": 77.1450},
    {"ward_no": 60, "ward_name": "Tri Nagar",         "zone": "Keshavpuram", "district": "North West",  "local_body_type": "MCD", "lat": 28.6700, "lng": 77.1540},
    {"ward_no": 61, "ward_name": "Lawrence Road",     "zone": "Keshavpuram", "district": "North West",  "local_body_type": "MCD", "lat": 28.6820, "lng": 77.1640},
    {"ward_no": 62, "ward_name": "Wazirpur",          "zone": "Keshavpuram", "district": "North West",  "local_body_type": "MCD", "lat": 28.6830, "lng": 77.1620},
    {"ward_no": 63, "ward_name": "Ashok Vihar",       "zone": "Keshavpuram", "district": "North West",  "local_body_type": "MCD", "lat": 28.6970, "lng": 77.1760},
    {"ward_no": 64, "ward_name": "Punjabi Bagh",      "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6650, "lng": 77.1350},
    {"ward_no": 65, "ward_name": "Madipur",           "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6670, "lng": 77.1190},
    {"ward_no": 66, "ward_name": "Paschim Vihar",     "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6720, "lng": 77.1010},
    {"ward_no": 67, "ward_name": "Nangloi",           "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6710, "lng": 77.0680},
    {"ward_no": 68, "ward_name": "Nangloi Jat",       "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6650, "lng": 77.0560},
    {"ward_no": 69, "ward_name": "Nilothi",           "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6770, "lng": 77.0370},
    {"ward_no": 70, "ward_name": "Mianwali Nagar",    "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6580, "lng": 77.0900},
    {"ward_no": 71, "ward_name": "Hastsal",           "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6490, "lng": 77.0840},
    {"ward_no": 72, "ward_name": "Uttam Nagar East",  "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6190, "lng": 77.0490},
    {"ward_no": 73, "ward_name": "Uttam Nagar West",  "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6190, "lng": 77.0290},
    {"ward_no": 74, "ward_name": "Dwarka Sector 10",  "zone": "Najafgarh",   "district": "South West",  "local_body_type": "MCD", "lat": 28.5840, "lng": 77.0520},
    {"ward_no": 75, "ward_name": "Dwarka Sector 14",  "zone": "Najafgarh",   "district": "South West",  "local_body_type": "MCD", "lat": 28.5730, "lng": 77.0340},
    {"ward_no": 76, "ward_name": "Dwarka",            "zone": "Najafgarh",   "district": "South West",  "local_body_type": "MCD", "lat": 28.5950, "lng": 77.0460},
    {"ward_no": 77, "ward_name": "Bindapur",          "zone": "Keshavpuram", "district": "West",        "local_body_type": "MCD", "lat": 28.6100, "lng": 77.0590},

    # ── WEST ZONE ───────────────────────────────────────────────────────────────
    # West Delhi (Janakpuri, Hari Nagar, Vikaspuri, Tilak Nagar)
    {"ward_no": 78, "ward_name": "Janakpuri East",    "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6250, "lng": 77.0830},
    {"ward_no": 79, "ward_name": "Janakpuri West",    "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6210, "lng": 77.0740},
    {"ward_no": 80, "ward_name": "Hari Nagar",        "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6330, "lng": 77.1100},
    {"ward_no": 81, "ward_name": "Vikaspuri",         "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6410, "lng": 77.0720},
    {"ward_no": 82, "ward_name": "Tilak Nagar",       "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6380, "lng": 77.1010},
    {"ward_no": 83, "ward_name": "Tagore Garden",     "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6490, "lng": 77.1220},
    {"ward_no": 84, "ward_name": "Subhash Nagar",     "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6360, "lng": 77.1150},
    {"ward_no": 85, "ward_name": "Rajouri Garden",    "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6460, "lng": 77.1220},
    {"ward_no": 86, "ward_name": "Ramesh Nagar",      "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6400, "lng": 77.1310},
    {"ward_no": 87, "ward_name": "Khyala",            "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6260, "lng": 77.1090},
    {"ward_no": 88, "ward_name": "Matiala",           "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.5980, "lng": 77.0730},
    {"ward_no": 89, "ward_name": "Mohan Garden",      "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6070, "lng": 77.0820},
    {"ward_no": 90, "ward_name": "Sagarpur",          "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6050, "lng": 77.0950},
    {"ward_no": 91, "ward_name": "Keshopur",          "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6560, "lng": 77.0970},
    {"ward_no": 92, "ward_name": "Srinivaspuri",      "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6270, "lng": 77.0680},
    {"ward_no": 93, "ward_name": "Sewak Park",        "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6090, "lng": 77.0680},
    {"ward_no": 94, "ward_name": "Nawada",            "zone": "West",        "district": "West",        "local_body_type": "MCD", "lat": 28.6050, "lng": 77.0470},
    {"ward_no": 95, "ward_name": "Mahavir Enclave",   "zone": "West",        "district": "South West",  "local_body_type": "MCD", "lat": 28.5970, "lng": 77.0580},

    # ── KAROL BAGH ZONE ─────────────────────────────────────────────────────────
    # One of the 12 official MCD zones (Additional Commissioner: Dr. Tariq Thomas)
    # Covers Karol Bagh, Patel Nagar, Paharganj, Jhandewalan, Kirti Nagar belt
    {"ward_no":  96, "ward_name": "Karol Bagh",        "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6519, "lng": 77.1909},
    {"ward_no":  97, "ward_name": "Patel Nagar East",  "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6450, "lng": 77.1750},
    {"ward_no":  98, "ward_name": "Patel Nagar West",  "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6420, "lng": 77.1650},
    {"ward_no":  99, "ward_name": "Inderpuri",         "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6360, "lng": 77.1720},
    {"ward_no": 100, "ward_name": "Rajender Nagar",    "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6410, "lng": 77.1850},
    {"ward_no": 101, "ward_name": "Jhandewalan",       "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6540, "lng": 77.2030},
    {"ward_no": 102, "ward_name": "Shyam Nagar",       "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6440, "lng": 77.2000},
    {"ward_no": 103, "ward_name": "Paharganj",         "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6460, "lng": 77.2120},
    {"ward_no": 104, "ward_name": "Motia Khan",        "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6570, "lng": 77.2070},
    {"ward_no": 105, "ward_name": "Rani Bagh",         "zone": "Karol Bagh", "district": "North West", "local_body_type": "MCD", "lat": 28.6800, "lng": 77.1820},
    {"ward_no": 106, "ward_name": "Naraina",           "zone": "Karol Bagh", "district": "West",       "local_body_type": "MCD", "lat": 28.6180, "lng": 77.1480},
    {"ward_no": 107, "ward_name": "Baljit Nagar",      "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6410, "lng": 77.1580},
    {"ward_no": 108, "ward_name": "Moti Nagar",        "zone": "Karol Bagh", "district": "West",       "local_body_type": "MCD", "lat": 28.6550, "lng": 77.1570},
    {"ward_no": 109, "ward_name": "Kirti Nagar",       "zone": "Karol Bagh", "district": "West",       "local_body_type": "MCD", "lat": 28.6540, "lng": 77.1450},
    {"ward_no": 110, "ward_name": "Raghubir Nagar",    "zone": "Karol Bagh", "district": "West",       "local_body_type": "MCD", "lat": 28.6490, "lng": 77.1320},
    {"ward_no": 111, "ward_name": "Mansarovar Park",   "zone": "Karol Bagh", "district": "West",       "local_body_type": "MCD", "lat": 28.6530, "lng": 77.1210},
    {"ward_no": 112, "ward_name": "Desh Bandhu Gupta", "zone": "Karol Bagh", "district": "Central",    "local_body_type": "MCD", "lat": 28.6570, "lng": 77.1990},

    # ── CITY ZONE ───────────────────────────────────────────────────────────────
    # Old Delhi / Walled City (Chandni Chowk, Darya Ganj belt)
    {"ward_no": 113, "ward_name": "Chandni Chowk",    "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6510, "lng": 77.2310},
    {"ward_no": 114, "ward_name": "Matia Mahal",       "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6490, "lng": 77.2310},
    {"ward_no": 115, "ward_name": "Ballimaran",        "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6520, "lng": 77.2260},
    {"ward_no": 116, "ward_name": "Darya Ganj",        "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6400, "lng": 77.2400},
    {"ward_no": 117, "ward_name": "Lal Kuan",          "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6550, "lng": 77.2340},
    {"ward_no": 118, "ward_name": "Jama Masjid",       "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6500, "lng": 77.2370},
    {"ward_no": 119, "ward_name": "Nabi Karim",        "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6490, "lng": 77.2190},
    {"ward_no": 120, "ward_name": "Turkman Gate",      "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6430, "lng": 77.2350},
    {"ward_no": 121, "ward_name": "Delhi Gate",        "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6380, "lng": 77.2400},
    {"ward_no": 122, "ward_name": "Quresh Nagar",      "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6390, "lng": 77.2440},
    {"ward_no": 123, "ward_name": "Rajghat",           "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6400, "lng": 77.2490},
    {"ward_no": 124, "ward_name": "Kotwali",           "zone": "City",       "district": "Central",    "local_body_type": "MCD", "lat": 28.6580, "lng": 77.2370},
    {"ward_no": 125, "ward_name": "Seelampur",         "zone": "City",       "district": "North East", "local_body_type": "MCD", "lat": 28.6640, "lng": 77.2720},
    {"ward_no": 126, "ward_name": "Usmanpur",          "zone": "City",       "district": "North East", "local_body_type": "MCD", "lat": 28.6730, "lng": 77.2600},

    # ── SOUTH ZONE ──────────────────────────────────────────────────────────────
    # South Delhi (Hauz Khas, Saket, Malviya Nagar, Kalkaji, Tughlakabad)
    {"ward_no": 127, "ward_name": "Hauz Khas",         "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5494, "lng": 77.2001},
    {"ward_no": 128, "ward_name": "Green Park",        "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5580, "lng": 77.2070},
    {"ward_no": 129, "ward_name": "Safdarjung Enclave","zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5660, "lng": 77.1960},
    {"ward_no": 130, "ward_name": "Munirka",           "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5570, "lng": 77.1740},
    {"ward_no": 131, "ward_name": "R K Puram",         "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5650, "lng": 77.1790},
    {"ward_no": 132, "ward_name": "Malviya Nagar",     "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5380, "lng": 77.2100},
    {"ward_no": 133, "ward_name": "Saket",             "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5230, "lng": 77.2080},
    {"ward_no": 134, "ward_name": "Neb Sarai",         "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5270, "lng": 77.2210},
    {"ward_no": 135, "ward_name": "Ambedkar Nagar",    "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5250, "lng": 77.1950},
    {"ward_no": 136, "ward_name": "Chirag Delhi",      "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5480, "lng": 77.2200},
    {"ward_no": 137, "ward_name": "Greater Kailash I", "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5390, "lng": 77.2350},
    {"ward_no": 138, "ward_name": "Greater Kailash II","zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5340, "lng": 77.2470},
    {"ward_no": 139, "ward_name": "Kalkaji",           "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5430, "lng": 77.2530},
    {"ward_no": 140, "ward_name": "Nehru Nagar",       "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5570, "lng": 77.2630},
    {"ward_no": 141, "ward_name": "Okhla",             "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5380, "lng": 77.2700},
    {"ward_no": 142, "ward_name": "Sangam Vihar",      "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5140, "lng": 77.2630},
    {"ward_no": 143, "ward_name": "Jaitpur",           "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.4990, "lng": 77.2700},
    {"ward_no": 144, "ward_name": "Badarpur",          "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.4990, "lng": 77.2880},
    {"ward_no": 145, "ward_name": "Madanpur Khadar",   "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5110, "lng": 77.2980},
    {"ward_no": 146, "ward_name": "Tughlakabad",       "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5190, "lng": 77.2630},
    {"ward_no": 147, "ward_name": "Deoli",             "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5120, "lng": 77.2260},
    {"ward_no": 148, "ward_name": "Mehrauli",          "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5170, "lng": 77.1860},
    {"ward_no": 149, "ward_name": "Chhatarpur",        "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5060, "lng": 77.1950},
    {"ward_no": 150, "ward_name": "Fatehpur Beri",     "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.4820, "lng": 77.2140},

    # ── SOUTH WEST ZONE ─────────────────────────────────────────────────────────
    # South-west Delhi (Palam, Bijwasan, Najafgarh, Kapashera)
    {"ward_no": 151, "ward_name": "Palam",             "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5530, "lng": 77.0720},
    {"ward_no": 152, "ward_name": "Kapashera",         "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5150, "lng": 77.0630},
    {"ward_no": 153, "ward_name": "Bijwasan",          "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5290, "lng": 77.0570},
    {"ward_no": 154, "ward_name": "Pappan Kalan",      "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5620, "lng": 77.0060},
    {"ward_no": 155, "ward_name": "Chhawla",           "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5730, "lng": 77.0110},
    {"ward_no": 156, "ward_name": "Najafgarh",         "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.6110, "lng": 76.9780},
    {"ward_no": 157, "ward_name": "Dichaon Kalan",     "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5730, "lng": 76.9920},
    {"ward_no": 158, "ward_name": "Dhansa",            "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5870, "lng": 76.9640},
    {"ward_no": 159, "ward_name": "Bamnoli",           "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5520, "lng": 77.0290},
    {"ward_no": 160, "ward_name": "Samalka",           "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5680, "lng": 77.0450},
    {"ward_no": 161, "ward_name": "Dwarka Sector 23",  "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5730, "lng": 77.0680},
    {"ward_no": 162, "ward_name": "Dwarka Sector 19",  "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5810, "lng": 77.0390},
    {"ward_no": 163, "ward_name": "Palam Gaon",        "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5450, "lng": 77.0840},
    {"ward_no": 164, "ward_name": "Raj Nagar",         "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5330, "lng": 77.0940},
    {"ward_no": 165, "ward_name": "Sadh Nagar",        "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5390, "lng": 77.1100},
    {"ward_no": 166, "ward_name": "Dashrath Puri",     "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5730, "lng": 77.1090},
    {"ward_no": 167, "ward_name": "Sarojini Nagar",    "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5770, "lng": 77.1870},
    {"ward_no": 168, "ward_name": "Lajpat Nagar II",   "zone": "Najafgarh", "district": "South",      "local_body_type": "MCD", "lat": 28.5677, "lng": 77.2433},
    {"ward_no": 169, "ward_name": "Lajpat Nagar III",  "zone": "Najafgarh", "district": "South",      "local_body_type": "MCD", "lat": 28.5680, "lng": 77.2380},
    {"ward_no": 170, "ward_name": "Andrews Ganj",      "zone": "Najafgarh", "district": "South",      "local_body_type": "MCD", "lat": 28.5630, "lng": 77.2310},
    {"ward_no": 171, "ward_name": "Bhikaji Cama Place","zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5700, "lng": 77.1880},
    {"ward_no": 172, "ward_name": "Vasant Kunj",       "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5200, "lng": 77.1580},

    # ── SHAHDARA SOUTH ZONE (cont.) — former EDMC East Delhi wards ─────────────
    # Laxmi Nagar, Preet Vihar, Patparganj belt: EDMC-era wards absorbed into
    # Shahdara South Zone in the 2022 unified MCD structure.
    {"ward_no": 173, "ward_name": "Laxmi Nagar",        "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6279, "lng": 77.2797},
    {"ward_no": 174, "ward_name": "Preet Vihar",        "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6358, "lng": 77.2930},
    {"ward_no": 175, "ward_name": "Patparganj",         "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6260, "lng": 77.2990},
    {"ward_no": 176, "ward_name": "Mandawali",          "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6180, "lng": 77.2990},
    {"ward_no": 177, "ward_name": "Vivek Vihar",        "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6660, "lng": 77.3100},
    {"ward_no": 178, "ward_name": "Trilokpuri",         "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6090, "lng": 77.3120},
    {"ward_no": 179, "ward_name": "Kondli",             "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6020, "lng": 77.3270},
    {"ward_no": 180, "ward_name": "Mayur Vihar Phase I","zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6120, "lng": 77.2930},
    {"ward_no": 181, "ward_name": "Mayur Vihar Phase II","zone":"Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6030, "lng": 77.3020},
    {"ward_no": 182, "ward_name": "IP Extension",       "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6200, "lng": 77.2930},
    {"ward_no": 183, "ward_name": "Kalyanpuri",         "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6140, "lng": 77.3100},
    {"ward_no": 184, "ward_name": "Khureji Khas",       "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6200, "lng": 77.3180},
    {"ward_no": 185, "ward_name": "Gandhinagar",        "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6450, "lng": 77.2560},
    {"ward_no": 186, "ward_name": "Krishna Nagar",      "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6530, "lng": 77.2770},
    {"ward_no": 187, "ward_name": "Geeta Colony",       "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6490, "lng": 77.2690},
    {"ward_no": 188, "ward_name": "Shakarpur",          "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6350, "lng": 77.2720},
    {"ward_no": 189, "ward_name": "Vasundhra Enclave",  "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.5990, "lng": 77.3230},
    {"ward_no": 190, "ward_name": "Chilla Saroda",      "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.5910, "lng": 77.3280},
    {"ward_no": 191, "ward_name": "Samaspur",           "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.5850, "lng": 77.3160},
    {"ward_no": 192, "ward_name": "Gazipur",            "zone": "Shahdara South", "district": "East",  "local_body_type": "MCD", "lat": 28.6290, "lng": 77.3180},

    # ── SHAHDARA SOUTH ZONE ─────────────────────────────────────────────────────
    # Trans-Yamuna, southern belt (Shahdara, Seema Puri, Welcome)
    {"ward_no": 193, "ward_name": "Shahdara",          "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6713, "lng": 77.2939},
    {"ward_no": 194, "ward_name": "Seema Puri",        "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6700, "lng": 77.3050},
    {"ward_no": 195, "ward_name": "Welcome",           "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6660, "lng": 77.2830},
    {"ward_no": 196, "ward_name": "New Seelampur",     "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6640, "lng": 77.2720},
    {"ward_no": 197, "ward_name": "Brahmpuri",         "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6780, "lng": 77.2800},
    {"ward_no": 198, "ward_name": "Maujpur",           "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6840, "lng": 77.2920},
    {"ward_no": 199, "ward_name": "Karawal Nagar Extension","zone": "Shahdara South","district": "North East","local_body_type": "MCD", "lat": 28.7450, "lng": 77.3080},
    {"ward_no": 200, "ward_name": "Anand Vihar",       "zone": "Shahdara South", "district": "East",   "local_body_type": "MCD", "lat": 28.6460, "lng": 77.3150},
    {"ward_no": 201, "ward_name": "Anand Nagar",       "zone": "Shahdara South", "district": "East",   "local_body_type": "MCD", "lat": 28.6590, "lng": 77.3200},
    {"ward_no": 202, "ward_name": "Karkardooma",       "zone": "Shahdara South", "district": "East",   "local_body_type": "MCD", "lat": 28.6460, "lng": 77.3080},
    {"ward_no": 203, "ward_name": "Jhilmil Colony",    "zone": "Shahdara South", "district": "East",   "local_body_type": "MCD", "lat": 28.6560, "lng": 77.3150},
    {"ward_no": 204, "ward_name": "Dilshad Garden",    "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6740, "lng": 77.3210},
    {"ward_no": 205, "ward_name": "Harsh Vihar",       "zone": "Shahdara South", "district": "North East","local_body_type": "MCD", "lat": 28.6970, "lng": 77.3000},
    {"ward_no": 206, "ward_name": "Nand Nagri",        "zone": "Shahdara South", "district": "North East","local_body_type": "MCD", "lat": 28.7030, "lng": 77.3180},
    {"ward_no": 207, "ward_name": "Loni Road",         "zone": "Shahdara South", "district": "North East","local_body_type": "MCD", "lat": 28.7160, "lng": 77.3160},
    {"ward_no": 208, "ward_name": "Kardampuri",        "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6840, "lng": 77.3040},
    {"ward_no": 209, "ward_name": "Yamuna Vihar",      "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6920, "lng": 77.2780},
    {"ward_no": 210, "ward_name": "Jagatpuri",         "zone": "Shahdara South", "district": "East",   "local_body_type": "MCD", "lat": 28.6580, "lng": 77.2850},
    {"ward_no": 211, "ward_name": "Farsh Bazar",       "zone": "Shahdara South", "district": "Shahdara","local_body_type": "MCD", "lat": 28.6630, "lng": 77.2980},
    {"ward_no": 212, "ward_name": "Saboli",            "zone": "Shahdara South", "district": "North East","local_body_type": "MCD", "lat": 28.7260, "lng": 77.3020},

    # ── SHAHDARA NORTH ZONE ─────────────────────────────────────────────────────
    # Trans-Yamuna, northern belt (Mustafabad, Karawal Nagar, Bhajanpura)
    {"ward_no": 213, "ward_name": "Bhajanpura",        "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6970, "lng": 77.2700},
    {"ward_no": 214, "ward_name": "Mustafabad",        "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7230, "lng": 77.2970},
    {"ward_no": 215, "ward_name": "Karawal Nagar",     "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7450, "lng": 77.3080},
    {"ward_no": 216, "ward_name": "Seemapuri",         "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7050, "lng": 77.3100},
    {"ward_no": 217, "ward_name": "Gokalpuri",         "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6990, "lng": 77.2880},
    {"ward_no": 218, "ward_name": "Sunder Nagri",      "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7130, "lng": 77.2950},
    {"ward_no": 219, "ward_name": "Babarpur",          "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6880, "lng": 77.2640},
    {"ward_no": 220, "ward_name": "Gharoli",           "zone": "Shahdara North", "district": "East",   "local_body_type": "MCD", "lat": 28.6350, "lng": 77.3350},
    {"ward_no": 221, "ward_name": "Sahibabad Dairy",   "zone": "Shahdara North", "district": "East",   "local_body_type": "MCD", "lat": 28.6280, "lng": 77.3420},
    {"ward_no": 222, "ward_name": "Nala Par",          "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7350, "lng": 77.2830},
    {"ward_no": 223, "ward_name": "Bhajan Pura",       "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6950, "lng": 77.2610},
    {"ward_no": 224, "ward_name": "Chauhan Bangar",    "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7000, "lng": 77.2780},
    {"ward_no": 225, "ward_name": "Johripur",          "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7050, "lng": 77.2850},
    {"ward_no": 226, "ward_name": "Shastri Park",      "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6790, "lng": 77.2650},
    {"ward_no": 227, "ward_name": "Geeta Colony East", "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.6620, "lng": 77.2760},
    {"ward_no": 228, "ward_name": "Khajuri Khas",      "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7200, "lng": 77.2800},
    {"ward_no": 229, "ward_name": "Dayalpur",          "zone": "Shahdara North", "district": "North East","local_body_type": "MCD", "lat": 28.7300, "lng": 77.2750},
    {"ward_no": 230, "ward_name": "Wazirabad Extension","zone":"Shahdara North","district": "North",   "local_body_type": "MCD", "lat": 28.7540, "lng": 77.2450},

    # ── ADDITIONAL WARDS (outer / peri-urban) ───────────────────────────────────
    # Wards 231-250 cover outer fringe areas across multiple zones
    {"ward_no": 231, "ward_name": "Bhorgarh",          "zone": "Narela",     "district": "North",      "local_body_type": "MCD", "lat": 28.8760, "lng": 77.1150},
    {"ward_no": 232, "ward_name": "Ibrahimpur",        "zone": "Narela",     "district": "North",      "local_body_type": "MCD", "lat": 28.8650, "lng": 77.1600},
    {"ward_no": 233, "ward_name": "Sawda",             "zone": "Narela",     "district": "North West", "local_body_type": "MCD", "lat": 28.7190, "lng": 77.0540},
    {"ward_no": 234, "ward_name": "Nangal Dewat",      "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.4970, "lng": 77.1710},
    {"ward_no": 235, "ward_name": "Asola",             "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.4780, "lng": 77.2340},
    {"ward_no": 236, "ward_name": "Mitraon",           "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5390, "lng": 76.9910},
    {"ward_no": 237, "ward_name": "Kangan Heri",       "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5230, "lng": 77.0160},
    {"ward_no": 238, "ward_name": "Khera Dabar",       "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5090, "lng": 76.9840},
    {"ward_no": 239, "ward_name": "Jaffarpur Kalan",   "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5700, "lng": 76.9920},
    {"ward_no": 240, "ward_name": "Paprawat",          "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5420, "lng": 77.0390},
    {"ward_no": 241, "ward_name": "Mahipalpur",        "zone": "Najafgarh", "district": "South West", "local_body_type": "MCD", "lat": 28.5300, "lng": 77.1220},
    {"ward_no": 242, "ward_name": "Vasant Vihar",      "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5530, "lng": 77.1600},
    {"ward_no": 243, "ward_name": "Masudpur",          "zone": "South",      "district": "South West", "local_body_type": "MCD", "lat": 28.5310, "lng": 77.1530},
    {"ward_no": 244, "ward_name": "Molar Band",        "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5040, "lng": 77.2970},
    {"ward_no": 245, "ward_name": "Pul Prahladpur",    "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5180, "lng": 77.2850},
    {"ward_no": 246, "ward_name": "Tuglakabad Extn",   "zone": "South",      "district": "South",      "local_body_type": "MCD", "lat": 28.5260, "lng": 77.2530},
    {"ward_no": 247, "ward_name": "Jasola",            "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5460, "lng": 77.2890},
    {"ward_no": 248, "ward_name": "Sarita Vihar",      "zone": "South",      "district": "South East", "local_body_type": "MCD", "lat": 28.5360, "lng": 77.2810},
    {"ward_no": 249, "ward_name": "Harkesh Nagar",      "zone": "Shahdara South", "district": "South East", "local_body_type": "MCD", "lat": 28.5800, "lng": 77.3030},
    {"ward_no": 250, "ward_name": "Kalindi Colony",     "zone": "Shahdara South", "district": "South East", "local_body_type": "MCD", "lat": 28.5680, "lng": 77.2900},

    # ── NDMC (New Delhi Municipal Council) ──────────────────────────────────────
    # Lutyens' Delhi — governed by NDMC, no MCD ward numbers
    {"ward_no": 901, "ward_name": "Connaught Place",   "zone": "NDMC Central","district": "New Delhi",  "local_body_type": "NDMC", "lat": 28.6315, "lng": 77.2167},
    {"ward_no": 902, "ward_name": "Lodhi Estate",      "zone": "NDMC South",  "district": "New Delhi",  "local_body_type": "NDMC", "lat": 28.5936, "lng": 77.2270},
    {"ward_no": 903, "ward_name": "Chanakyapuri",      "zone": "NDMC West",   "district": "New Delhi",  "local_body_type": "NDMC", "lat": 28.5982, "lng": 77.1860},

    # ── DCB (Delhi Cantonment Board) ────────────────────────────────────────────
    {"ward_no": 951, "ward_name": "Delhi Cantonment",  "zone": "DCB",         "district": "South West", "local_body_type": "DCB",  "lat": 28.5921, "lng": 77.0460},
]
# fmt: on

# ---------------------------------------------------------------------------
# Coordinate corrections — verified against OSM Nominatim + Delhi geography
# knowledge. Only applied where original centroid was clearly wrong (>2km and
# cross-checked against known locality position).
# Wards NOT listed here were either within tolerance or Nominatim returned a
# false match (another locality with same name in a different part of Delhi).
# ---------------------------------------------------------------------------
_COORD_OVERRIDES: dict[int, tuple[float, float]] = {
    # ward_no: (corrected_lat, corrected_lng)

    # ── Narela Zone ──────────────────────────────────────────────────────────
    3:   (28.8528, 77.0767),  # Bankner       was (28.867, 77.025)
    4:   (28.7973, 77.1387),  # Alipur        was (28.84, 77.133)
    7:   (28.7173, 77.1818),  # Mukundpur     was (28.78, 77.147) — near Model Town
    8:   (28.7158, 77.0743),  # Pooth Kalan   was (28.746, 77.058)
    12:  (28.6824, 77.0306),  # Mundka        was (28.692, 77.000) — too far west
    14:  (28.6894, 77.0764),  # Sultanpur Majra  was (28.747, 77.048)
    18:  (28.7596, 77.1517),  # Swaroop Nagar was (28.728, 77.107)
    231: (28.8266, 77.1001),  # Bhorgarh      was (28.876, 77.115)
    232: (28.7757, 77.1766),  # Ibrahimpur    was (28.865, 77.16) — too far north

    # ── Rohini Zone ──────────────────────────────────────────────────────────
    20:  (28.7214, 77.1367),  # Rohini Sector 15  was (28.721, 77.103)
    23:  (28.7414, 77.1324),  # Rohini Sector 18  was (28.718, 77.148)
    25:  (28.7189, 77.0697),  # Rohini Sector 21  was (28.732, 77.138) — outer Rohini
    30:  (28.7002, 77.1249),  # Saraswati Vihar   was (28.682, 77.148)
    34:  (28.7465, 77.1375),  # Badli             was (28.732, 77.167)

    # ── Civil Lines Zone ─────────────────────────────────────────────────────
    53:  (28.7050, 77.2926),  # Gokalpur      was (28.755, 77.2) — NE Delhi not far north

    # ── Keshavpuram Zone ─────────────────────────────────────────────────────
    55:  (28.6980, 77.1405),  # Kohat Enclave     was (28.696, 77.176)
    69:  (28.6504, 77.0623),  # Nilothi           was (28.677, 77.037)
    71:  (28.6360, 77.0488),  # Hastsal           was (28.649, 77.084)
    75:  (28.6022, 77.0260),  # Dwarka Sector 14  was (28.573, 77.034)
    76:  (28.6159, 77.0224),  # Dwarka            was (28.595, 77.046)

    # ── West Zone ────────────────────────────────────────────────────────────
    87:  (28.6564, 77.1009),  # Khyala        was (28.626, 77.109)
    89:  (28.6200, 77.0680),  # Mohan Garden  was (28.607, 77.082)
    93:  (28.6166, 77.0354),  # Sewak Park    was (28.609, 77.068)

    # ── Karol Bagh Zone ──────────────────────────────────────────────────────
    105: (28.6860, 77.1325),  # Rani Bagh         was (28.68, 77.182) — near Pitampura
    111: (28.6700, 77.1360),  # Mansarovar Park   was (28.653, 77.121)

    # ── South West Zone ──────────────────────────────────────────────────────
    151: (28.5919, 77.0828),  # Palam             was (28.553, 77.072)
    157: (28.6406, 76.9827),  # Dichaon Kalan     was (28.573, 76.992)
    161: (28.5940, 77.0238),  # Dwarka Sector 23  was (28.573, 77.068)
    165: (28.5922, 77.0982),  # Sadh Nagar        was (28.539, 77.11)
    166: (28.6018, 77.0824),  # Dashrath Puri     was (28.573, 77.109)
    234: (28.5260, 77.1389),  # Nangal Dewat      was (28.497, 77.171)
    240: (28.5881, 76.9782),  # Paprawat          was (28.542, 77.039)

    # ── South Zone ───────────────────────────────────────────────────────────
    134: (28.5055, 77.2015),  # Neb Sarai         was (28.527, 77.221)
    135: (28.5192, 77.2362),  # Ambedkar Nagar    was (28.525, 77.195)
    141: (28.5637, 77.2891),  # Okhla             was (28.538, 77.27)
    143: (28.4994, 77.3062),  # Jaitpur           was (28.499, 77.27)
    146: (28.5025, 77.2994),  # Tughlakabad       was (28.519, 77.263)
    150: (28.4574, 77.1825),  # Fatehpur Beri     was (28.482, 77.214)
    235: (28.4780, 77.2100),  # Asola             was (28.478, 77.234)

    # ── Shahdara South Zone ──────────────────────────────────────────────────
    184: (28.6460, 77.2860),  # Khureji Khas      was (28.62, 77.318)
    191: (28.6138, 77.2849),  # Samaspur          was (28.585, 77.316)
    194: (28.6986, 77.3113),  # Seema Puri        was (28.67, 77.305)
    207: (28.6827, 77.2923),  # Loni Road         was (28.716, 77.316)
    249: (28.5461, 77.2752),  # Harkesh Nagar     was (28.58, 77.303)

    # ── Shahdara North Zone ──────────────────────────────────────────────────
    215: (28.7311, 77.2748),  # Karawal Nagar     was (28.745, 77.308)
    216: (28.6811, 77.3278),  # Seemapuri         was (28.705, 77.31)
}

# Apply coordinate overrides
for _w in DELHI_WARDS:
    if _w["ward_no"] in _COORD_OVERRIDES:
        _w["lat"], _w["lng"] = _COORD_OVERRIDES[_w["ward_no"]]

# Enrich every ward with its zonal commissioner at import time.
# Routing logic can read ward["zonal_commissioner"] directly.
for _w in DELHI_WARDS:
    _c = ZONE_COMMISSIONERS.get(_w["zone"])
    _w["zonal_commissioner"] = _c["name"] if _c else "Unknown"
    _w["zonal_commissioner_cadre"] = _c["cadre"] if _c else ""
    _w["commissioner_confirmed"] = _c["confirmed"] if _c else False


def ward_by_no(ward_no: int) -> WardRecord | None:
    return next((w for w in DELHI_WARDS if w["ward_no"] == ward_no), None)


def wards_by_zone(zone: str) -> list[WardRecord]:
    return [w for w in DELHI_WARDS if w["zone"] == zone]


def wards_by_district(district: str) -> list[WardRecord]:
    return [w for w in DELHI_WARDS if w["district"] == district]


def commissioner_for_zone(zone: str) -> ZoneCommissioner | None:
    return ZONE_COMMISSIONERS.get(zone)


def commissioner_for_ward(ward_no: int) -> ZoneCommissioner | None:
    ward = ward_by_no(ward_no)
    if not ward:
        return None
    return ZONE_COMMISSIONERS.get(ward["zone"])
