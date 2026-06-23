-- CIVIKTA authority master (PRD §12, §43.1)
insert into authorities (authority_name, department_name, authority_family, local_body_scope, slug) values
  ('MCD - Sanitation',        'Department of Environment Management Services', 'municipal',        'MCD',  'mcd_sanitation'),
  ('MCD - Engineering',       'Engineering Department',                        'municipal',        'MCD',  'mcd_engineering'),
  ('MCD - Horticulture',      'Horticulture Department',                       'municipal',        'MCD',  'mcd_horticulture'),
  ('MCD - Public Health',     'Public Health Department',                      'municipal',        'MCD',  'mcd_public_health'),
  ('NDMC - Sanitation',       'Sanitation Department',                         'municipal',        'NDMC', 'ndmc_sanitation'),
  ('NDMC - Civil',            'Civil Engineering',                             'municipal',        'NDMC', 'ndmc_civil'),
  ('NDMC - Horticulture',     'Horticulture Department',                       'municipal',        'NDMC', 'ndmc_horticulture'),
  ('Delhi Cantonment Board',  'Civic Services',                               'municipal',        'DCB',  'dcb_civic'),
  ('Delhi Jal Board',         'Water & Sewer',                                'service_specific', null,   'djb'),
  ('Public Works Department', 'Roads & Major Corridors',                      'service_specific', null,   'pwd'),
  ('Irrigation & Flood Control', 'Major Drains & Flood Control',              'service_specific', null,   'ifcd'),
  ('Delhi Development Authority', 'DDA Land & Parks',                         'service_specific', null,   'dda'),
  ('Delhi Police',            'Enforcement',                                  'enforcement',      null,   'delhi_police'),
  ('National Highways Authority of India', 'National Highways',               'service_specific', null,   'nhai')
on conflict (slug) do nothing;
