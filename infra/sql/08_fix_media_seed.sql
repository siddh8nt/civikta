-- CIVIKTA — Media seed fix
-- Run in Supabase SQL Editor AFTER 01_schema.sql and 02_seed_demo.sql
-- Idempotent: safe to run multiple times.

-- ── 1. Add cover_media_url column to issues ───────────────────────────────
ALTER TABLE public.issues ADD COLUMN IF NOT EXISTS cover_media_url text;

-- ── 2. Link original reports to their canonical issues ────────────────────
-- Fixes the bug where original reports had merged_into_issue_id = NULL
UPDATE public.issue_reports ir
SET merged_into_issue_id = i.id
FROM public.issues i
WHERE ir.id = i.original_report_id
  AND ir.merged_into_issue_id IS NULL;

-- ── 3. Seed issue_media rows based on issue category ─────────────────────
-- Uses the actual original_report_id UUIDs already in the DB,
-- so this works regardless of which UUIDs were assigned at seed time.
INSERT INTO public.issue_media (report_id, media_type, storage_url)
SELECT
  i.original_report_id,
  'image',
  CASE i.issue_category_slug
    WHEN 'water_sewer_drainage' THEN
      CASE i.issue_type_slug
        WHEN 'waterlogging' THEN 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Morogoro_road_B129_flooded_%281%29_01.jpg/960px-Morogoro_road_B129_flooded_%281%29_01.jpg'
        WHEN 'contaminated_water' THEN 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/India_-_Rural_-_03_-_drinking_water_and_waste_water_meet_on_the_street_%282564575360%29.jpg/960px-India_-_Rural_-_03_-_drinking_water_and_waste_water_meet_on_the_street_%282564575360%29.jpg'
        ELSE 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Open_sewer_%282731597018%29.jpg/960px-Open_sewer_%282731597018%29.jpg'
      END
    WHEN 'roads_streets' THEN
      CASE i.issue_type_slug
        WHEN 'footpath_encroachment' THEN 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Potholed_road_outside_Kolkata_Airport.jpg/960px-Potholed_road_outside_Kolkata_Airport.jpg'
        ELSE 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Potholes_on_road.jpg/960px-Potholes_on_road.jpg'
      END
    WHEN 'garbage_sanitation' THEN
      CASE i.issue_type_slug
        WHEN 'dead_animal' THEN 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Dead_animal_on_Rozoda_road.jpg/960px-Dead_animal_on_Rozoda_road.jpg'
        WHEN 'stray_dog_menace' THEN 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Stray_dog_in_the_streets_of_Pune.jpg/960px-Stray_dog_in_the_streets_of_Pune.jpg'
        ELSE 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/A_burning_roadside_garbage_dump_at_Panvel_Naka_near_Mumbai.jpg/960px-A_burning_roadside_garbage_dump_at_Panvel_Naka_near_Mumbai.jpg'
      END
    WHEN 'lights_electrical' THEN
      'https://upload.wikimedia.org/wikipedia/commons/e/e2/India-5144_-_Flickr_-_archer10_%28Dennis%29.jpg'
    WHEN 'parks_public_space' THEN
      'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Fallen_Tree_in_Dormer_Place%2C_Leamington_Spa_%281%29.jpg/960px-Fallen_Tree_in_Dormer_Place%2C_Leamington_Spa_%281%29.jpg'
    ELSE
      'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Potholes_on_road.jpg/960px-Potholes_on_road.jpg'
  END
FROM public.issues i
WHERE i.original_report_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM public.issue_media m WHERE m.report_id = i.original_report_id
  );

-- ── 4. Populate cover_media_url directly on the issue ────────────────────
UPDATE public.issues i
SET cover_media_url = m.storage_url
FROM public.issue_media m
WHERE m.report_id = i.original_report_id
  AND i.cover_media_url IS NULL;
