-- 05_postgis_geo.sql
-- Run in Supabase SQL Editor AFTER 04_seed_wards.sql
-- Adds PostGIS polygon-first ward resolution.

-- 1. Enable PostGIS
create extension if not exists postgis;

-- 2. Add boundary column to delhi_wards
alter table public.delhi_wards
  add column if not exists boundary geometry(MultiPolygon, 4326);

-- 3. GIST spatial index for fast ST_Contains / ST_DWithin queries
create index if not exists delhi_wards_boundary_gist
  on public.delhi_wards using gist (boundary);

-- 4. resolve_ward RPC
-- Returns best ward for a lat/lng point:
--   Stage 1: exact polygon containment       → confidence 0.97
--   Stage 2: nearest boundary within 150 m   → confidence 0.80  (handles GPS noise)
-- Returns empty if no boundaries loaded yet; geo_service.py falls back to centroid.
create or replace function public.resolve_ward(lat float8, lng float8)
returns table (
  ward_no         integer,
  ward_name       text,
  zone            text,
  district        text,
  local_body_type text,
  confidence      float8,
  method          text
)
language sql
stable
as $$
  select ward_no, ward_name, zone, district, local_body_type, confidence, method
  from (
    -- Stage 1: point strictly inside polygon
    (
      select
        w.ward_no::integer,
        w.ward_name::text,
        w.zone::text,
        w.district::text,
        w.local_body_type::text,
        0.97::float8    as confidence,
        'polygon'::text as method
      from public.delhi_wards w
      where w.boundary is not null
        and st_contains(w.boundary, st_setsrid(st_makepoint(lng, lat), 4326))
      limit 1
    )

    union all

    -- Stage 2: nearest boundary edge within 150 m (GPS noise / border straddling)
    (
      select
        w.ward_no::integer,
        w.ward_name::text,
        w.zone::text,
        w.district::text,
        w.local_body_type::text,
        0.80::float8   as confidence,
        'buffer'::text as method
      from public.delhi_wards w
      where w.boundary is not null
        and st_dwithin(
          w.boundary::geography,
          st_setsrid(st_makepoint(lng, lat), 4326)::geography,
          150
        )
      order by st_distance(
        w.boundary::geography,
        st_setsrid(st_makepoint(lng, lat), 4326)::geography
      )
      limit 1
    )
  ) candidates
  order by confidence desc
  limit 1;
$$;

-- 5. update_ward_boundary helper — called by the Python import pipeline
create or replace function public.update_ward_boundary(p_ward_no integer, p_geojson text)
returns void
language sql
as $$
  update public.delhi_wards
  set boundary = st_multi(st_geomfromgeojson(p_geojson))
  where ward_no = p_ward_no;
$$;

-- Grant execute
grant execute on function public.resolve_ward(float8, float8)         to anon, authenticated, service_role;
grant execute on function public.update_ward_boundary(integer, text)  to service_role;
