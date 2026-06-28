-- 06_jurisdiction_boundaries.sql
-- Run in Supabase SQL Editor AFTER 05_postgis_geo.sql
--
-- Adds authoritative NDMC and DCB jurisdiction boundary polygons.
-- These are used to correctly identify jurisdiction (MCD/NDMC/DCB) independent
-- of ward resolution, handling the case where NDMC/DCB ward boundary polygons
-- were not imported by the Overpass import script.
--
-- Boundary coordinates: approximate administrative boundaries derived from
-- publicly known Delhi civic geography. Accurate enough to correctly classify:
--   - Connaught Place, India Gate, Lodhi Road belt → NDMC
--   - Delhi Cantonment / Dhaula Kuan belt          → DCB
--   - All other Delhi areas                         → MCD
--
-- Source provenance: well-known Delhi civic geography; official GeoJSON from
-- NDMC / MoUD can replace these polygons when available.
-- TODO: Replace with official GeoJSON from https://ndmc.gov.in or Data.gov.in

-- 1. Jurisdiction boundaries table
create table if not exists public.jurisdiction_boundaries (
  id              serial      primary key,
  jurisdiction    text        not null unique check (jurisdiction in ('NDMC', 'DCB')),
  boundary        geometry(Polygon, 4326) not null,
  source_note     text,
  updated_at      timestamptz default now()
);

create index if not exists jurisdiction_boundaries_gist
  on public.jurisdiction_boundaries using gist (boundary);

-- 2. Seed NDMC approximate boundary
-- Covers: Connaught Place, India Gate, Rashtrapati Bhavan, Lodhi Estate,
--         Chanakyapuri (diplomatic enclave), Safdarjung area, Teen Murti House
-- North edge: Paharganj / Panchkuian Road
-- East edge:  Mathura Road / Ring Road near ITO
-- South edge: Safdarjung / Lodi Road
-- West edge:  Chanakyapuri western boundary
insert into public.jurisdiction_boundaries (jurisdiction, boundary, source_note)
values (
  'NDMC',
  st_geomfromtext(
    'POLYGON((
      77.1530 28.6420,
      77.2050 28.6480,
      77.2350 28.6420,
      77.2550 28.6200,
      77.2520 28.5950,
      77.2400 28.5700,
      77.2100 28.5550,
      77.1800 28.5580,
      77.1550 28.5720,
      77.1430 28.5920,
      77.1480 28.6150,
      77.1530 28.6420
    ))',
    4326
  ),
  'Approximate NDMC boundary. Covers Connaught Place, India Gate, Lodhi Road, Chanakyapuri. Source: known civic geography. Replace with official NDMC GeoJSON when available.'
)
on conflict (jurisdiction) do update
  set boundary    = excluded.boundary,
      source_note = excluded.source_note,
      updated_at  = now();

-- 3. Seed DCB approximate boundary
-- Covers: Shankar Vihar, Brar Square, Dhaula Kuan, Air Force Station Palam (core cantonment belt)
-- North edge: Dhaula Kuan / NH-48 junction area (~28.62N)
-- East edge:  Near Naraina / Ring Road (~77.14E)
-- South edge: Near Palam (~28.55N)
-- West edge:  77.065E — keeps ALL Dwarka sectors (including Sector 7 at 77.064E) outside.
--             The cantonment railway station (77.046E) is west of this polygon and is
--             correctly classified as DCB via ward fuzzy-match (ward 951) independently;
--             the boundary polygon covers the main residential/cantonment belt.
insert into public.jurisdiction_boundaries (jurisdiction, boundary, source_note)
values (
  'DCB',
  st_geomfromtext(
    'POLYGON((
      77.0850 28.5490,
      77.1100 28.5500,
      77.1420 28.5720,
      77.1380 28.6100,
      77.0950 28.6260,
      77.0850 28.6150,
      77.0850 28.5490
    ))',
    4326
  ),
  'Approximate DCB boundary. West edge 77.085E. Covers Brar Square, Sadar Cantonment, Dhaula Kuan. Excludes Dwarka sectors and adjacent fringe (<77.085E). Python skip logic handles any residual Dwarka misclassification. Replace with official DCB GeoJSON when available.'
)
on conflict (jurisdiction) do update
  set boundary    = excluded.boundary,
      source_note = excluded.source_note,
      updated_at  = now();

-- 4. resolve_jurisdiction RPC
-- Returns NDMC if point is inside NDMC polygon,
--         DCB if inside DCB polygon,
--         MCD otherwise (default — covers all remaining Delhi territory).
-- Runs INDEPENDENTLY of ward resolution so it can catch cases where
-- NDMC/DCB ward boundary polygons were not imported via import_ward_boundaries.py.
create or replace function public.resolve_jurisdiction(lat float8, lng float8)
returns table (
  jurisdiction  text,
  method        text,   -- 'boundary_polygon' | 'default_mcd'
  source_note   text
)
language sql
stable
as $$
  select jurisdiction, method, source_note
  from (
    -- Check NDMC and DCB boundary polygons (boundary_polygon wins over default_mcd)
    (
      select
        j.jurisdiction,
        'boundary_polygon'::text as method,
        j.source_note
      from public.jurisdiction_boundaries j
      where st_contains(j.boundary, st_setsrid(st_makepoint(lng, lat), 4326))
      order by j.id   -- NDMC (id=1) before DCB (id=2) if somehow both match
      limit 1
    )
    union all
    -- Default: MCD — covers all Delhi territory outside NDMC/DCB polygons
    (
      select
        'MCD'::text,
        'default_mcd'::text,
        'Outside NDMC and DCB boundary polygons; defaults to MCD'::text
    )
  ) candidates
  order by (case when method = 'boundary_polygon' then 0 else 1 end)
  limit 1;
$$;

grant execute on function public.resolve_jurisdiction(float8, float8) to anon, authenticated, service_role;
