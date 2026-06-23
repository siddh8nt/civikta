-- CIVIKTA database schema (PRD §23, patched two-layer model)
-- Target: Supabase Postgres. Requires PostGIS + pgvector.
-- The canonical public object is `issues`; every citizen submission is an `issue_report`.
-- There is intentionally NO single `complaints` table.

create extension if not exists postgis;
create extension if not exists vector;
create extension if not exists "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Reference / master data
-- ---------------------------------------------------------------------------

create table if not exists users (
  id            uuid primary key default uuid_generate_v4(), -- set to Firebase UID in prod
  role          text not null default 'citizen',             -- citizen / authority / oversight / admin
  name          text,
  email         text,
  phone         text,
  home_locality text,
  created_at    timestamptz not null default now()
);

create table if not exists authorities (
  id                 uuid primary key default uuid_generate_v4(),
  authority_name     text not null,
  department_name    text,
  authority_family   text not null,
  local_body_scope   text,
  slug               text unique not null
);

create table if not exists issue_categories (
  id        uuid primary key default uuid_generate_v4(),
  parent_id uuid references issue_categories(id),
  level     int not null default 1,
  name      text not null,
  slug      text unique not null,
  active    boolean not null default true
);

create table if not exists asset_types (
  id           uuid primary key default uuid_generate_v4(),
  name         text not null,
  slug         text unique not null,
  asset_family text
);

create table if not exists routing_rules (
  id                       uuid primary key default uuid_generate_v4(),
  local_body_type          text,
  issue_type_slug          text,
  asset_type_slug          text,
  road_class               text,
  drain_type               text,
  land_owner_hint          text,
  primary_authority_slug   text not null,
  secondary_authority_slug text,
  rule_priority            int not null default 100,
  confidence_score         numeric not null default 0.8,
  notes                    text
);

create table if not exists delhi_boundaries (
  id            uuid primary key default uuid_generate_v4(),
  boundary_type text not null,   -- ndmc / cantonment / ward / zone / district
  name          text not null,
  code          text,
  parent_code   text,
  geom          geometry(MultiPolygon, 4326) not null
);
create index if not exists idx_delhi_boundaries_geom on delhi_boundaries using gist (geom);

-- ---------------------------------------------------------------------------
-- Canonical public issue
-- ---------------------------------------------------------------------------

create table if not exists issues (
  id                       uuid primary key default uuid_generate_v4(),
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now(),
  original_report_id       uuid,
  created_by               uuid references users(id),

  title                    text,
  canonical_description    text,
  public_summary           text,

  status                   text not null default 'submitted',
  status_reason            text,

  latitude                 numeric,
  longitude                numeric,
  location                 geography(Point, 4326),

  local_body_type          text,
  revenue_district         text,
  tehsil_subdivision       text,
  mcd_zone                 text,
  ward_no                  int,
  ward_name                text,
  locality_name            text,
  landmark                 text,

  issue_category_slug      text,
  issue_type_slug          text,
  asset_type_slug          text,

  severity                 text,
  urgency_score            numeric not null default 1.0,
  corroboration_count      int not null default 0,
  total_report_count       int not null default 1,
  total_evidence_count     int not null default 0,
  last_corroborated_at     timestamptz,

  obstruction_flag         boolean not null default false,
  health_hazard_flag       boolean not null default false,
  public_safety_flag       boolean not null default false,

  road_class               text,
  drain_type               text,
  land_owner_hint          text,

  ai_summary               text,
  ai_confidence            numeric,
  summary_embedding        vector(768),   -- Vertex AI text-embedding-004

  primary_authority_slug   text,
  secondary_authority_slug text,
  routing_confidence       numeric,
  routing_reason           jsonb
);
create index if not exists idx_issues_location on issues using gist (location);
create index if not exists idx_issues_status   on issues (status);
create index if not exists idx_issues_ward      on issues (ward_no);
-- Semantic duplicate search (cosine). Tune lists/probes once seeded.
create index if not exists idx_issues_embedding on issues using ivfflat (summary_embedding vector_cosine_ops);

-- ---------------------------------------------------------------------------
-- Individual citizen submissions (raw input layer)
-- ---------------------------------------------------------------------------

create table if not exists issue_reports (
  id                           uuid primary key default uuid_generate_v4(),
  created_at                   timestamptz not null default now(),
  updated_at                   timestamptz not null default now(),
  created_by                   uuid references users(id),

  raw_title                    text,
  raw_description              text,
  media_summary                text,

  latitude                     numeric,
  longitude                    numeric,
  location                     geography(Point, 4326),

  issue_category_slug          text,
  issue_type_slug              text,
  asset_type_slug              text,

  ai_summary                   text,
  ai_confidence                numeric,
  ai_raw                       jsonb,

  duplicate_confidence         numeric,
  duplicate_candidate_issue_id uuid references issues(id),

  report_role                  text not null default 'original',  -- original / corroboration
  merge_decision               text,                              -- pending / merged / forced_new / manual_review
  merged_into_issue_id         uuid references issues(id),

  still_unresolved_flag        boolean not null default false,
  affected_too_flag            boolean not null default false,

  source                       text not null default 'citizen_app'
);
create index if not exists idx_reports_location on issue_reports using gist (location);
create index if not exists idx_reports_merged   on issue_reports (merged_into_issue_id);

alter table issues
  add constraint fk_issues_original_report
  foreign key (original_report_id) references issue_reports(id)
  deferrable initially deferred;

-- ---------------------------------------------------------------------------
-- Media / timeline / comments
-- ---------------------------------------------------------------------------

create table if not exists issue_media (
  id            uuid primary key default uuid_generate_v4(),
  report_id     uuid not null references issue_reports(id),
  media_type    text not null,            -- image / video / audio
  storage_url   text not null,            -- Firebase Storage URL
  thumbnail_url text,
  created_at    timestamptz not null default now()
);

create table if not exists issue_events (
  id         uuid primary key default uuid_generate_v4(),
  issue_id   uuid not null references issues(id),
  actor_type text not null,               -- citizen / authority / system / oversight
  actor_id   uuid,
  event_type text not null,               -- created / classified / assigned / verified / resolved /
                                          -- reopened / duplicate_candidate_found /
                                          -- community_verification_prompt_shown / issue_corroborated /
                                          -- issue_merged / urgency_score_updated / still_unresolved_confirmed
  payload    jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_events_issue on issue_events (issue_id, created_at);

create table if not exists issue_comments (
  id         uuid primary key default uuid_generate_v4(),
  issue_id   uuid not null references issues(id),
  user_id    uuid references users(id),
  body       text not null,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Oversight (predictive anomaly alerts, PRD §10.4)
-- ---------------------------------------------------------------------------

create table if not exists oversight_alerts (
  id            uuid primary key default uuid_generate_v4(),
  created_at    timestamptz not null default now(),
  ward_no       int,
  ward_name     text,
  category_slug text,
  severity      text not null default 'watch',  -- watch / alert / critical
  headline      text not null,
  detail        text,
  metrics       jsonb
);
