-- CIVIKTA routing rules (PRD §13, §43.3)
-- Evaluation is by rule_priority ASC (lower = more specific = wins first).
-- NULL columns mean "wildcard / not constrained".

insert into routing_rules
  (local_body_type, issue_type_slug, asset_type_slug, road_class, drain_type, land_owner_hint,
   primary_authority_slug, secondary_authority_slug, rule_priority, confidence_score, notes) values

  -- Water / sewer always DJB regardless of local body
  (null, 'sewer_overflow',          null, null, null, null, 'djb', 'mcd_sanitation', 10, 0.95, 'Sewer = DJB; co-tag local sanitation for cleanup'),
  (null, 'no_water_supply',         null, null, null, null, 'djb', null,             10, 0.95, 'Water supply = DJB'),
  (null, 'contaminated_water',      null, null, null, null, 'djb', null,             10, 0.95, 'Water quality = DJB'),

  -- Major road potholes / corridor waterlogging = PWD
  (null, 'pothole_major_road',      null, 'arterial', null, null, 'pwd', null,       20, 0.9,  'Arterial/flyover roads = PWD'),
  (null, 'waterlogging',            null, 'arterial', null, null, 'pwd', 'ifcd',     20, 0.85, 'Corridor waterlogging = PWD, escalate IFCD'),

  -- Trunk drain = IFCD
  (null, 'clogged_local_drain',     'trunk_drain', null, 'trunk', null, 'ifcd', null, 20, 0.9, 'Trunk drain / nallah = IFCD'),

  -- Local body engineering: local roads + local drains
  ('MCD',  'pothole_local_road',    null, null, null, null, 'mcd_engineering',  null, 50, 0.85, null),
  ('NDMC', 'pothole_local_road',    null, null, null, null, 'ndmc_civil',       null, 50, 0.85, null),
  ('DCB',  'pothole_local_road',    null, null, null, null, 'dcb_civic',        null, 50, 0.85, null),
  ('MCD',  'clogged_local_drain',   null, null, null, null, 'mcd_engineering',  null, 50, 0.85, null),
  ('NDMC', 'clogged_local_drain',   null, null, null, null, 'ndmc_civil',       null, 50, 0.85, null),
  ('DCB',  'clogged_local_drain',   null, null, null, null, 'dcb_civic',        null, 50, 0.85, null),
  ('MCD',  'broken_footpath',       null, null, null, null, 'mcd_engineering',  null, 50, 0.8,  null),
  ('NDMC', 'broken_footpath',       null, null, null, null, 'ndmc_civil',       null, 50, 0.8,  null),

  -- Sanitation: garbage / dumping
  ('MCD',  'garbage_not_collected', null, null, null, null, 'mcd_sanitation',   null, 50, 0.9,  null),
  ('NDMC', 'garbage_not_collected', null, null, null, null, 'ndmc_sanitation',  null, 50, 0.9,  null),
  ('DCB',  'garbage_not_collected', null, null, null, null, 'dcb_civic',        null, 50, 0.9,  null),
  ('MCD',  'overflowing_garbage',   null, null, null, null, 'mcd_sanitation',   null, 50, 0.9,  null),
  ('MCD',  'illegal_dumping',       null, null, null, null, 'mcd_sanitation',   null, 50, 0.85, null),

  -- Streetlights
  ('MCD',  'streetlight_not_working', null, null, null, null, 'mcd_engineering', null, 50, 0.8, null),
  ('NDMC', 'streetlight_not_working', null, null, null, null, 'ndmc_civil',      null, 50, 0.8, null),

  -- Parks by owner
  ('MCD',  'park_maintenance_issue', 'park', null, null, null,  'mcd_horticulture',  null, 50, 0.85, null),
  ('NDMC', 'park_maintenance_issue', 'park', null, null, null,  'ndmc_horticulture', null, 50, 0.85, null),
  (null,   'park_maintenance_issue', 'park', null, null, 'dda', 'dda',               null, 40, 0.85, 'DDA parks'),
  ('MCD',  'tree_hazard',            'tree', null, null, null,  'mcd_horticulture',  null, 50, 0.8,  null),

  -- Animals / public health
  ('MCD',  'stray_dog_issue', null, null, null, null, 'mcd_public_health', null, 50, 0.85, null),
  ('MCD',  'dead_animal',     null, null, null, null, 'mcd_public_health', null, 50, 0.85, null),

  -- Encroachment / obstruction (owner + police if obstruction)
  (null, 'footpath_encroachment', null, null, null, null, 'mcd_engineering', 'delhi_police', 60, 0.7, 'Co-tag police if traffic obstruction'),
  (null, 'road_obstruction',      null, null, null, null, 'mcd_engineering', 'delhi_police', 60, 0.7, null),

  -- Catch-all fallbacks (lowest priority)
  ('MCD',  null, null, null, null, null, 'mcd_engineering', null, 200, 0.4, 'MCD default fallback'),
  ('NDMC', null, null, null, null, null, 'ndmc_civil',      null, 200, 0.4, 'NDMC default fallback'),
  ('DCB',  null, null, null, null, null, 'dcb_civic',       null, 200, 0.4, 'DCB default fallback');
