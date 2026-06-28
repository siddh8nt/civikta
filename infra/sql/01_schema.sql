-- ============================================================================
-- CIVIKTA — Supabase Schema
-- Run this once in your Supabase SQL editor (Dashboard → SQL Editor → New Query)
-- ============================================================================

-- Extensions
-- PostGIS (spatial): already enabled on Supabase by default
-- pgvector (embeddings): uncomment line below when ready for semantic duplicate detection
-- create extension if not exists vector;

-- ── USERS ────────────────────────────────────────────────────────────────────
-- Covers citizens, authority personnel, and oversight staff.
-- ID matches the UUID stored in the browser's localStorage (civikta_user_id).

create table if not exists public.users (
  id                uuid        primary key,          -- same UUID as localStorage
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),

  name              text,
  phone             text,
  role              text        not null default 'citizen'
                    check (role in ('citizen', 'authority', 'oversight', 'admin')),

  -- Locality set during onboarding
  ward_no           integer,
  ward_name         text,
  zone              text,
  local_body_type   text        check (local_body_type in ('MCD', 'NDMC', 'DCB')),
  district          text,
  home_lat          double precision,
  home_lng          double precision,

  -- Authority-specific (only for role = 'authority')
  authority_slug    text,

  is_demo           boolean     not null default false
);

create index if not exists users_role_idx on public.users (role);

-- Updated-at trigger
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end;
$$;

create or replace trigger users_updated_at
  before update on public.users
  for each row execute procedure set_updated_at();

-- ── AUTHORITIES ──────────────────────────────────────────────────────────────
-- Static reference — Delhi civic departments and agencies.

create table if not exists public.authorities (
  slug              text        primary key,
  authority_name    text        not null,
  department_name   text,
  authority_family  text        not null,
  local_body_scope  text,
  category_slugs    text[]      not null default '{}',
  sla_target_hours  integer,        -- expected resolution time
  contact_portal_url text            -- grievance portal / helpline
);

-- ── DELHI WARDS ──────────────────────────────────────────────────────────────
-- Reference table: all 250 MCD wards + NDMC areas + DCB.
-- Centroid lat/lng for nearest-neighbour ward resolution.
-- Commissioner data: Sep 2024 MCD reallocation order.

create table if not exists public.delhi_wards (
  ward_no                    integer     primary key,
  ward_name                  text        not null,
  zone                       text        not null,
  district                   text        not null,
  local_body_type            text        not null
                             check (local_body_type in ('MCD', 'NDMC', 'DCB')),
  lat                        double precision not null,
  lng                        double precision not null,
  zonal_commissioner         text,
  zonal_commissioner_cadre   text,
  commissioner_confirmed     boolean     not null default false
);

create index if not exists delhi_wards_zone_idx     on public.delhi_wards (zone);
create index if not exists delhi_wards_district_idx on public.delhi_wards (district);
create index if not exists delhi_wards_lbt_idx      on public.delhi_wards (local_body_type);
create index if not exists delhi_wards_latlon_idx   on public.delhi_wards (lat, lng);

-- ── ROUTING RULES ────────────────────────────────────────────────────────────
-- Maps issue attributes → responsible authority.

create table if not exists public.routing_rules (
  id                         uuid   primary key default gen_random_uuid(),
  local_body_type            text,
  issue_type_slug            text,
  asset_type_slug            text,
  road_class                 text,
  drain_type                 text,
  land_owner_hint            text,
  primary_authority_slug     text   not null references public.authorities(slug),
  secondary_authority_slug   text   references public.authorities(slug),
  escalation_authority_slug  text   references public.authorities(slug),
  rule_priority              integer not null default 100,
  confidence_score           double precision not null default 0.8,
  notes                      text
);

-- ── ISSUES ───────────────────────────────────────────────────────────────────
-- Canonical civic issue records — deduplicated, corroborated, AI-enriched.

create table if not exists public.issues (
  id                       uuid        primary key default gen_random_uuid(),
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now(),
  original_report_id       uuid,       -- soft ref to issue_reports.id (FK added below)
  created_by               text,       -- user UUID (soft ref)

  title                    text,
  canonical_description    text,
  public_summary           text,

  status                   text        not null default 'submitted',
  status_reason            text,

  -- Location (plain lat/lng — PostGIS geography upgrade path: add `location geography(Point,4326)`)
  latitude                 double precision,
  longitude                double precision,

  -- Delhi admin geography
  local_body_type          text,
  revenue_district         text,
  tehsil_subdivision       text,
  mcd_zone                 text,
  ward_no                  integer,
  ward_name                text,
  locality_name            text,
  landmark                 text,

  -- Issue classification (3-level taxonomy)
  issue_category_slug      text,
  issue_subcategory_slug   text,       -- L2 e.g. 'road_surface_damage'
  issue_type_slug          text,
  asset_type_slug          text,

  -- Scoring
  severity                 text        not null default 'medium',
  urgency_score            double precision not null default 1.0,
  corroboration_count      integer     not null default 0,
  total_report_count       integer     not null default 1,
  total_evidence_count     integer     not null default 0,
  last_corroborated_at     timestamptz,

  -- Impact flags (boolean shortcuts for quick filtering)
  obstruction_flag         boolean     not null default false,
  health_hazard_flag       boolean     not null default false,
  public_safety_flag       boolean     not null default false,

  -- Extended impact tags (array of slugs for rich cross-cutting classification)
  -- e.g. 'school_zone_risk', 'women_safety_risk', 'hospital_zone_risk', 'night_visibility_risk'
  impact_tags              text[]      not null default '{}',

  -- Lifecycle tracking
  persistence_type         text        not null default 'new'
                           check (persistence_type in ('new', 'recurring', 'chronic')),
  false_closure_suspected  boolean     not null default false,

  -- Routing hints
  road_class               text,
  drain_type               text,
  land_owner_hint          text,

  -- AI
  ai_summary               text,
  ai_confidence            double precision,
  -- summary_embedding    vector(768),  -- enable with pgvector for semantic dedup

  -- Authority routing
  primary_authority_slug   text        references public.authorities(slug),
  secondary_authority_slug text        references public.authorities(slug),
  routing_confidence       double precision,
  routing_reason           jsonb       not null default '{}'
);

create index if not exists issues_status_idx    on public.issues (status);
create index if not exists issues_ward_idx      on public.issues (ward_no);
create index if not exists issues_authority_idx on public.issues (primary_authority_slug);
create index if not exists issues_category_idx  on public.issues (issue_category_slug);
create index if not exists issues_latlon_idx    on public.issues (latitude, longitude);
create index if not exists issues_created_idx   on public.issues (created_at desc);

create or replace trigger issues_updated_at
  before update on public.issues
  for each row execute procedure set_updated_at();

-- ── ISSUE REPORTS ────────────────────────────────────────────────────────────
-- Each citizen submission (original or corroboration).
-- NOTE: image_data (base64) is NOT stored here — too large. Media lives in
-- issue_media (storage URLs) or Supabase Storage bucket.

create table if not exists public.issue_reports (
  id                           uuid        primary key default gen_random_uuid(),
  created_at                   timestamptz not null default now(),
  updated_at                   timestamptz not null default now(),
  created_by                   text,       -- user UUID

  raw_title                    text,
  raw_description              text,
  media_summary                text,

  latitude                     double precision,
  longitude                    double precision,

  issue_category_slug          text,
  issue_type_slug              text,
  asset_type_slug              text,

  ai_summary                   text,
  ai_confidence                double precision,
  ai_raw                       jsonb       not null default '{}',

  duplicate_confidence         double precision,
  duplicate_candidate_issue_id uuid        references public.issues(id),

  report_role                  text        not null default 'original',
  merge_decision               text,
  merged_into_issue_id         uuid        references public.issues(id),

  still_unresolved_flag        boolean     not null default false,
  affected_too_flag            boolean     not null default false,

  source                       text        not null default 'citizen_app'
);

create index if not exists reports_user_idx  on public.issue_reports (created_by);
create index if not exists reports_issue_idx on public.issue_reports (merged_into_issue_id);

create or replace trigger reports_updated_at
  before update on public.issue_reports
  for each row execute procedure set_updated_at();

-- Add soft FK from issues back to original_report_id now that issue_reports exists
-- (not enforced at DB level to avoid circular constraint complexity)

-- ── ISSUE MEDIA ──────────────────────────────────────────────────────────────

create table if not exists public.issue_media (
  id            uuid        primary key default gen_random_uuid(),
  report_id     uuid        not null references public.issue_reports(id) on delete cascade,
  media_type    text        not null default 'image',
  storage_url   text        not null,
  thumbnail_url text,
  created_at    timestamptz not null default now()
);

create index if not exists media_report_idx on public.issue_media (report_id);

-- ── ISSUE EVENTS ─────────────────────────────────────────────────────────────
-- Immutable audit trail: status changes, assignments, resolutions, AI actions.

create table if not exists public.issue_events (
  id          uuid        primary key default gen_random_uuid(),
  issue_id    uuid        not null references public.issues(id) on delete cascade,
  actor_type  text        not null default 'system',
  actor_id    text,
  event_type  text        not null default 'created',
  payload     jsonb       not null default '{}',
  created_at  timestamptz not null default now()
);

create index if not exists events_issue_idx   on public.issue_events (issue_id);
create index if not exists events_created_idx on public.issue_events (created_at desc);
