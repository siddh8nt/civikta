-- 07_ndmc_ward_boundaries.sql
-- Run AFTER 06_jurisdiction_boundaries.sql
--
-- Creates NDMC ward boundaries by intersecting the NDMC jurisdiction polygon
-- with simple split planes. This guarantees:
--   (a) Ward boundaries are exactly within NDMC territory — no bleed into MCD
--   (b) The three wards tile to cover the full NDMC area with no gaps/overlaps
--   (c) Kartavya Path / India Gate resolves to ward 902, not ward 901
--
-- Split logic:
--   Horizontal split: lat 28.615N (Kartavya Path / Rajpath level)
--   Vertical split:   lon 77.200E (Vijay Chowk / Rashtrapati Bhavan meridian)
--
--   Ward 901 "Connaught Place" → northern NDMC  (above 28.615N)
--   Ward 902 "Lodhi Estate"    → south-east NDMC (below 28.615N, east of 77.200E)
--   Ward 903 "Chanakyapuri"    → south-west NDMC (below 28.615N, west of 77.200E)
--
-- Verification:
--   Connaught Place  28.633N 77.217E → above 28.615 → ward 901 ✓
--   Kartavya Path    28.612N 77.229E → below 28.615, east of 77.200 → ward 902 ✓
--   India Gate       28.612N 77.229E → below 28.615, east of 77.200 → ward 902 ✓
--   Chanakyapuri     28.598N 77.186E → below 28.615, west of 77.200 → ward 903 ✓

-- Ward 901 "Connaught Place" — northern NDMC
UPDATE public.delhi_wards
SET boundary = st_multi(
  st_intersection(
    (SELECT boundary FROM public.jurisdiction_boundaries WHERE jurisdiction = 'NDMC'),
    st_makeenvelope(76.80, 28.615, 77.40, 29.00, 4326)
  )
)
WHERE ward_no = 901;

-- Ward 902 "Lodhi Estate" — south-east NDMC (India Gate, Lodhi Road, Khan Market)
UPDATE public.delhi_wards
SET boundary = st_multi(
  st_intersection(
    (SELECT boundary FROM public.jurisdiction_boundaries WHERE jurisdiction = 'NDMC'),
    st_makeenvelope(77.200, 28.40, 77.40, 28.615, 4326)
  )
)
WHERE ward_no = 902;

-- Ward 903 "Chanakyapuri" — south-west NDMC (diplomatic enclave, Teen Murti)
UPDATE public.delhi_wards
SET boundary = st_multi(
  st_intersection(
    (SELECT boundary FROM public.jurisdiction_boundaries WHERE jurisdiction = 'NDMC'),
    st_makeenvelope(76.80, 28.40, 77.200, 28.615, 4326)
  )
)
WHERE ward_no = 903;

-- DCB ward 951 — boundary = the full DCB jurisdiction polygon
-- Any point inside DCB territory now resolves directly to ward 951 via ST_Contains.
-- Points outside (e.g. Dwarka) get no match → fall to Nominatim/centroid → MCD.
UPDATE public.delhi_wards
SET boundary = st_multi(
  (SELECT boundary FROM public.jurisdiction_boundaries WHERE jurisdiction = 'DCB')
)
WHERE ward_no = 951;
