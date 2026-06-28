-- ============================================================================
-- CIVIKTA — Routing Rules Seed
-- Run AFTER 01_schema.sql and 02_seed_demo.sql
-- Implements the Delhi civic jurisdiction routing matrix.
-- ============================================================================

-- Update authorities with SLA targets and contact portals
update public.authorities set
  sla_target_hours = 24,  contact_portal_url = 'https://mcdonline.nic.in'
  where slug = 'mcd_sanitation';
update public.authorities set
  sla_target_hours = 72,  contact_portal_url = 'https://mcdonline.nic.in'
  where slug = 'mcd_engineering';
update public.authorities set
  sla_target_hours = 72,  contact_portal_url = 'https://mcdonline.nic.in'
  where slug = 'mcd_horticulture';
update public.authorities set
  sla_target_hours = 24,  contact_portal_url = 'https://mcdonline.nic.in'
  where slug = 'mcd_public_health';
update public.authorities set
  sla_target_hours = 24,  contact_portal_url = 'https://ndmc.gov.in'
  where slug in ('ndmc_sanitation','ndmc_civil','ndmc_horticulture');
update public.authorities set
  sla_target_hours = 72,  contact_portal_url = null
  where slug = 'dcb_civic';
update public.authorities set
  sla_target_hours = 12,  contact_portal_url = 'https://djb.gov.in'
  where slug = 'djb';
update public.authorities set
  sla_target_hours = 72,  contact_portal_url = 'https://pwd.delhi.gov.in'
  where slug = 'pwd';
update public.authorities set
  sla_target_hours = 48,  contact_portal_url = 'https://ifc.delhi.gov.in'
  where slug = 'ifcd';
update public.authorities set
  sla_target_hours = 168, contact_portal_url = 'https://dda.gov.in'
  where slug = 'dda';
update public.authorities set
  sla_target_hours = 4,   contact_portal_url = 'https://delhipolice.gov.in'
  where slug = 'delhi_police';
update public.authorities set
  sla_target_hours = 168, contact_portal_url = 'https://nhai.gov.in'
  where slug = 'nhai';

-- ── Helper: insert rule ignoring duplicates ──────────────────────────────────
-- We use a unique index concept — just use on conflict do nothing with explicit ids.

-- ── PRIORITY 5 — National Highway ────────────────────────────────────────────
insert into public.routing_rules(id,issue_type_slug,road_class,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('e210b45b-aaae-9b93-198d-4eca0caae78c','pothole_major_road','national_highway','nhai',5,0.90,'National highway → NHAI'),
  ('4abdd04c-b7fb-1c41-7868-7317127e283c','road_obstruction_debris','national_highway','nhai',5,0.85,'NH debris → NHAI')
  on conflict do nothing;

-- ── PRIORITY 10 — Infrastructure owners ──────────────────────────────────────
insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score,notes) values
  ('26d602a1-96b0-2b02-f954-a8014b3f5bb3','sewer_overflow','djb','mcd_sanitation',10,0.95,'DJB owns all sewer infrastructure'),
  ('61ddb78e-1f20-ddef-ece6-9449dec4c99d','pipeline_leakage','djb',null,10,0.95,null),
  ('2e16198d-52d3-9891-8dec-53fc20e4fa0c','no_water_supply','djb',null,10,0.95,null),
  ('3c726dbf-05a2-33bf-c688-f60aca1fb36a','contaminated_water','djb',null,10,0.95,null),
  ('f468cdcc-a97c-8d89-b53c-0a778b954257','overflowing_water_tank','djb',null,10,0.90,null),
  ('f6ad7483-963e-f1f0-a209-8b87013f58be','broken_public_tap','djb',null,10,0.90,null),
  ('fddc7a97-b594-3215-20d4-1ee24f2d57dd','water_body_pollution','djb','mcd_sanitation',10,0.85,null),
  ('befacfc7-d2f1-b5a4-1e2d-a69659dc3f65','open_manhole','djb','mcd_engineering',10,0.90,'DJB owns manhole; MCD restores road'),
  ('822cf60a-3d02-7136-60eb-5f49ccae935b','broken_manhole_cover','djb','mcd_engineering',10,0.90,null),
  ('c745d0fa-26cd-4b9d-e0f1-286903d394f6','public_toilet_sewage','djb','mcd_sanitation',10,0.85,'Toilet sewer connection → DJB')
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,road_class,primary_authority_slug,rule_priority,confidence_score) values
  ('ccb705f1-bbdf-08e6-ac78-e76998122ca2','pothole_major_road','arterial','pwd',10,0.90),
  ('620cf670-fd78-f006-0fd0-451de65b4167','road_depression','arterial','pwd',10,0.90),
  ('4d7faacc-d69a-6e50-c9af-82e494c54574','road_collapse','arterial','pwd',10,0.90),
  ('0c3ad479-a533-ec12-6322-a584a7c2e737','road_divider_damaged','arterial','pwd',10,0.85),
  ('5f3bc6ba-ef05-e672-50f4-709562194e7f','missing_road_sign','arterial','pwd',10,0.85)
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,road_class,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('fcc83084-ee1a-82ce-8dfd-e8be9c44e839','waterlogging','arterial','pwd','ifcd',10,0.85)
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('2696dca0-8045-8616-eef0-3349f61a7ff2','traffic_signal_failure','delhi_police',10,0.85,'Traffic signals = Delhi Police Traffic Wing')
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('40043967-befd-f4a1-5819-0a9f38486023','fallen_tree_road','mcd_horticulture','mcd_engineering',20,0.90)
  on conflict do nothing;

-- ── PRIORITY 20 — Asset-class overrides ──────────────────────────────────────
insert into public.routing_rules(id,issue_type_slug,drain_type,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('4e61f048-7ddf-5193-9967-b69fa80f2528','clogged_local_drain','trunk','ifcd',20,0.90,'Trunk drain → IFCD'),
  ('5a4c3e66-de1e-113c-cd6d-bcebb384bde2','stagnant_water','trunk','ifcd',20,0.80,null)
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,asset_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('8ff5b84f-d363-d622-2251-fbfdd5e50a46','clogged_local_drain','trunk_drain','ifcd',20,0.90),
  ('67bc0f9d-c69c-c396-cb80-ed8e3713e011','clogged_local_drain','nallah','ifcd',20,0.90),
  ('1dc1f87b-cbc6-a156-a1ad-3278661a9083','open_drain_cover_missing','sewer_line','djb',20,0.85)
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score,notes) values
  ('bf3a3e4d-735c-7abc-655d-9af357a2b275','major_flooding','ifcd','pwd',20,0.85,'Trunk drain/Yamuna flood infra = IFCD')
  on conflict do nothing;

-- ── PRIORITY 40 — DDA land owner overrides ────────────────────────────────────
insert into public.routing_rules(id,issue_type_slug,land_owner_hint,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('4c003672-2967-9736-a4e1-9e44a8aa84fe','park_maintenance_issue','dda','dda',40,0.88,'DDA owns and maintains DDA parks'),
  ('11bd8915-e5e6-c683-ed4b-a093caed8083','broken_play_equipment','dda','dda',40,0.85,null),
  ('0aea44b1-458a-725d-dc43-fb729f56d968','illegal_structure_public_land','dda','dda',40,0.85,'Encroachment on DDA land')
  on conflict do nothing;

insert into public.routing_rules(id,issue_type_slug,land_owner_hint,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('1dcb93e6-3097-db86-d2a6-1b015c8f052a','park_lighting_failure','dda','dda','mcd_engineering',40,0.80),
  ('f597456a-daed-8d65-68b6-44ec21fdb031','illegal_dumping','dda','mcd_sanitation','dda',40,0.82)
  on conflict do nothing;

-- ── PRIORITY 50 — Local-body-specific defaults ────────────────────────────────
-- Roads (local)
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('e4b10e57-2a22-e2ec-1071-a8f97ce12ad7','MCD','pothole_local_road','mcd_engineering',50,0.85),
  ('9bf16d1e-e390-336f-e6c2-e150cdc668f3','MCD','road_surface_crack','mcd_engineering',50,0.80),
  ('9f2da0d7-7baf-b856-feb5-dc7c8b19ff46','MCD','road_depression','mcd_engineering',50,0.80),
  ('9a557352-7381-cfb1-fbdc-4fb207de6b1c','MCD','road_collapse','mcd_engineering',50,0.80),
  ('1f946d03-0cc8-6a43-9299-ba5b0a8e8c31','MCD','road_obstruction_debris','mcd_engineering',50,0.80),
  ('14a184e1-9f64-022d-8de1-289ad5bb9733','MCD','bus_shelter_damaged','mcd_engineering',50,0.75),
  ('58198342-bd02-80e0-4ec4-8eed3d5fcd6e','MCD','broken_footpath','mcd_engineering',50,0.80),
  ('38be535d-779e-2a9d-9209-d0d56f7a05c9','MCD','footpath_missing_ramp','mcd_engineering',50,0.80),
  ('e6694d08-2ffa-e076-39d2-a85f2c254d75','MCD','road_divider_damaged','mcd_engineering',50,0.75),
  ('fec447c1-01ed-33ff-0d68-6aa43df7b011','MCD','missing_road_sign','mcd_engineering',50,0.75),
  ('efe24644-c8d8-1233-fb66-9b95f01b39e3','NDMC','pothole_local_road','ndmc_civil',50,0.85),
  ('be2af923-4e7a-cf15-16c6-a33d4f3757aa','NDMC','broken_footpath','ndmc_civil',50,0.80),
  ('a701eece-6cc5-880c-6de8-ea2073bf5acc','NDMC','bus_shelter_damaged','ndmc_civil',50,0.75),
  ('c595a63e-0b79-e9c5-fd5d-27786f68da8f','DCB','pothole_local_road','dcb_civic',50,0.85)
  on conflict do nothing;

-- Drainage (local)
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('2fcd0368-3535-24c3-3008-3b643cec2cd2','MCD','clogged_local_drain','mcd_engineering',50,0.85,null),
  ('f0cfe4a7-1186-7980-2eff-bcd32aff87b2','MCD','open_drain_cover_missing','mcd_engineering',50,0.80,null),
  ('62cbf50e-0091-76b8-9be7-96de0dddac8e','MCD','waterlogging','mcd_engineering',50,0.80,'Local colony waterlogging = MCD'),
  ('352eb55d-32eb-0ad3-e9c3-5f1e8726aead','MCD','drain_encroachment','mcd_engineering',50,0.80,null),
  ('c2fa34cc-2b62-e039-e625-896ecff4e99b','NDMC','clogged_local_drain','ndmc_civil',50,0.85,null)
  on conflict do nothing;

insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('c7b32bb1-287a-0575-d503-85041270696f','MCD','stagnant_water','mcd_sanitation','mcd_engineering',50,0.80)
  on conflict do nothing;

-- Sanitation
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('1970fe81-f1c1-2b2a-813a-42406cc9287e','MCD','garbage_not_collected','mcd_sanitation',50,0.92),
  ('6e1dd5d5-b15f-8be1-a7ae-059d7756f71b','MCD','overflowing_garbage','mcd_sanitation',50,0.90),
  ('bc0b97b5-c544-582b-b855-0275110b848d','MCD','illegal_dumping','mcd_sanitation',50,0.85),
  ('92c55e86-245f-0854-8b64-1a2635ff543e','MCD','dead_animal','mcd_public_health',50,0.88),
  ('36f97230-ecaa-a5b9-c520-41e1e4025e43','MCD','garbage_burning','mcd_sanitation',50,0.85),
  ('6bc54b15-9a88-023b-82c2-bcdc2c30d964','MCD','missing_public_dustbin','mcd_sanitation',50,0.80),
  ('0cce7df1-d7a4-4e64-d5be-0f5d68c8af34','MCD','street_uncleaned','mcd_sanitation',50,0.88),
  ('f9d25cdb-70de-d78a-f78c-3867595e82d1','MCD','public_toilet_dirty','mcd_sanitation',50,0.85),
  ('73c9adbe-9f8f-e79b-4875-b23f829275dd','MCD','public_toilet_locked','mcd_sanitation',50,0.85),
  ('d8833f70-c63e-26ad-2c48-63b8ad8bc484','NDMC','garbage_not_collected','ndmc_sanitation',50,0.92),
  ('307410b1-5e62-b94f-e8d5-77eafa814dbd','NDMC','street_uncleaned','ndmc_sanitation',50,0.88),
  ('b6c9f365-19d5-674b-a604-4390b071811c','DCB','garbage_not_collected','dcb_civic',50,0.90)
  on conflict do nothing;

insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('cc040f45-4f01-8b37-0408-4a18e7656853','MCD','construction_debris_dump','mcd_sanitation','pwd',50,0.80),
  ('b7ee845a-3c01-1125-2a8e-ea9c3ad22e4b','MCD','public_toilet_no_water','djb','mcd_sanitation',50,0.80)
  on conflict do nothing;

-- Streetlights / Electrical
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('5850156e-03d0-897d-8be2-9d27adfc6fd5','MCD','streetlight_not_working','mcd_engineering',50,0.80),
  ('02dcf9b7-c734-83d7-29a3-a8fe3e5997f5','MCD','streetlights_stretch_dark','mcd_engineering',50,0.82),
  ('0916d968-1089-e6f5-a725-3c83afebe1f1','MCD','streetlight_flickering','mcd_engineering',50,0.80),
  ('44f2c0b3-fcf3-ab22-ad50-1e95f7c4b17c','MCD','broken_lamp_pole','mcd_engineering',50,0.82),
  ('de3d02a0-d4e4-b4c2-f38c-36119de3e6f5','MCD','exposed_wire','mcd_engineering',50,0.75),
  ('ee0e9d4b-30c7-0a78-5f15-cd727d433057','MCD','leaning_electric_pole','mcd_engineering',50,0.75),
  ('d0da8ec6-60ed-9734-eba5-046fd0cbf035','MCD','sparking_junction_box','mcd_engineering',50,0.75),
  ('026b3277-0a3c-d18c-d35f-63b405cbfd83','NDMC','streetlight_not_working','ndmc_civil',50,0.80),
  ('827feac0-2c72-4548-3dcd-f98198696917','NDMC','exposed_wire','ndmc_civil',50,0.75),
  ('00c83bd6-0ce7-18db-e2c0-14111af98038','DCB','streetlight_not_working','dcb_civic',50,0.80)
  on conflict do nothing;

-- Safety
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('827fec97-4b98-0c81-39f5-7ace319b2683','MCD','structural_hazard','mcd_engineering',50,0.80),
  ('bebe8d9c-125a-5208-717a-3dc7d8f82f69','MCD','open_trench','mcd_engineering',50,0.80),
  ('d5c28ce5-1374-f5a3-eeb0-f24451e3abcf','MCD','slip_hazard','mcd_engineering',50,0.75),
  ('8b1aaa62-8244-9ba1-790a-7fb8c4ad83c6','MCD','unsafe_structure','mcd_engineering',50,0.78),
  ('9ff1e60b-1d82-6a0a-2446-1c7503ab9f91','MCD','electrical_hazard_public','mcd_engineering',50,0.75)
  on conflict do nothing;

-- Parks
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('fb8426f7-0abc-58aa-a00f-54307b6783fb','MCD','park_maintenance_issue','mcd_horticulture',50,0.85),
  ('0d1dc1a3-acf2-49fc-f2e1-77340c62086b','MCD','broken_play_equipment','mcd_horticulture',50,0.82),
  ('c6e1d4f7-1e7b-906f-73da-1ed7888f98b5','MCD','broken_bench','mcd_horticulture',50,0.78),
  ('de64a60d-67a4-5d67-c9d8-d4e386b263bc','MCD','broken_public_fixture','mcd_engineering',50,0.75),
  ('072740bd-7db7-2857-9f01-15bd969266ac','MCD','illegal_structure_public_land','mcd_engineering',50,0.75),
  ('73820ad6-9a54-315a-af2f-4d505eec5dc5','NDMC','park_maintenance_issue','ndmc_horticulture',50,0.85),
  ('4e70f217-7953-0737-15b5-3978d2c81251','NDMC','tree_hazard','ndmc_horticulture',50,0.85)
  on conflict do nothing;

insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('5f47bbf6-f547-700d-95f8-05ab40ff187f','MCD','tree_hazard','mcd_horticulture','mcd_engineering',50,0.85),
  ('88788210-4a1a-7c92-fac7-ac9c42ba68bb','MCD','park_lighting_failure','mcd_horticulture','mcd_engineering',50,0.80)
  on conflict do nothing;

-- Animals / Public Health
insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,rule_priority,confidence_score) values
  ('8581682c-07ba-4069-2cc7-41290dbd5ca1','MCD','stray_dog_issue','mcd_public_health',50,0.87),
  ('49e175b7-4bec-726e-9ce5-815617cb7ec6','MCD','cattle_nuisance','mcd_public_health',50,0.82),
  ('22d9794d-119d-7857-fab5-56eaeb0593dc','MCD','animal_nuisance','mcd_public_health',50,0.78)
  on conflict do nothing;

insert into public.routing_rules(id,local_body_type,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score) values
  ('4c6ca2b4-d00d-811e-09b6-c66d4cf52141','MCD','mosquito_breeding','mcd_public_health','djb',50,0.82)
  on conflict do nothing;

-- Civic service failure
insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('7810ee43-781c-127a-0ef3-4cdb3141ec78','complaint_unactioned','mcd_engineering',50,0.50,'Re-route to original authority; escalate to oversight'),
  ('b4db1ce1-777e-4405-3612-ac119d58d7c9','false_closure_reported','mcd_engineering',50,0.50,'Flag for oversight review; bump urgency'),
  ('cb555f6a-9612-65c3-af99-61c1df808685','chronic_issue_hotspot','mcd_engineering',50,0.50,'3+ reports same location 90 days → auto-escalate'),
  ('54776f9d-3ea6-bb6f-c8c9-e82200c80155','missed_routine_service','mcd_sanitation',50,0.60,null)
  on conflict do nothing;

-- ── PRIORITY 60 — Enforcement co-tags ────────────────────────────────────────
insert into public.routing_rules(id,issue_type_slug,primary_authority_slug,secondary_authority_slug,rule_priority,confidence_score,notes) values
  ('1825965b-056f-c6d6-d490-5d3ed4ebd2bb','footpath_encroachment','mcd_engineering','delhi_police',60,0.72,'Police support for hawker/vehicle removal'),
  ('6f797880-167e-26d9-2275-231d49a4930a','road_encroachment_material','mcd_engineering','delhi_police',60,0.72,null),
  ('73261477-4d67-cfba-b809-cf0e9defa30a','vehicle_on_footpath','delhi_police','mcd_engineering',60,0.82,'Vehicle removal = police primary'),
  ('7b8a1f19-e371-2a66-826f-25e65923b727','road_obstruction','mcd_engineering','delhi_police',60,0.70,null),
  ('e1de36b4-ad8a-2b20-2f52-61a5cb5c0b40','noise_pollution','delhi_police',null,60,0.75,'Noise = law enforcement'),
  ('444e2fc1-0322-4aa8-5a4a-19a08d3081d5','construction_dust_pollution','mcd_engineering',null,60,0.70,null)
  on conflict do nothing;

-- ── PRIORITY 200 — Catch-all fallbacks ───────────────────────────────────────
insert into public.routing_rules(id,local_body_type,primary_authority_slug,rule_priority,confidence_score,notes) values
  ('750d6698-49a9-96e3-bff5-171f5db2d49c','MCD','mcd_engineering',200,0.40,'MCD default'),
  ('006ef2fa-4069-2241-7a83-e1f07e4d6a40','NDMC','ndmc_civil',200,0.40,'NDMC default'),
  ('3eff5254-55e6-708f-52ff-fb496849d30c','DCB','dcb_civic',200,0.40,'DCB default')
  on conflict do nothing;
