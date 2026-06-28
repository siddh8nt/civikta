-- Migration: Add commissioner_email to delhi_wards
-- Run in Supabase SQL editor: https://app.supabase.com/project/mfcpuickdbhtgdjaybub/sql/new
-- Officials sourced from MCD Sep 2024 Additional Commissioner assignments

ALTER TABLE public.delhi_wards
  ADD COLUMN IF NOT EXISTS commissioner_email text;

-- MCD: Narela · West · Najafgarh zones
UPDATE public.delhi_wards
  SET commissioner_email = 'sachin.shinde@mcd.delhi.gov.in'
  WHERE zonal_commissioner = 'Sachin Shinde';

-- MCD: South · SP-City · Centre zones
UPDATE public.delhi_wards
  SET commissioner_email = 'jitender.yadav@mcd.delhi.gov.in'
  WHERE zonal_commissioner = 'Jitender Yadav';

-- MCD: Keshavpuram · Rohini zones
UPDATE public.delhi_wards
  SET commissioner_email = 'nidhi.malik@mcd.delhi.gov.in'
  WHERE zonal_commissioner = 'Nidhi Malik';

-- MCD: Civil Lines · Karol Bagh zones
UPDATE public.delhi_wards
  SET commissioner_email = 'tariq.thomas@mcd.delhi.gov.in'
  WHERE zonal_commissioner = 'Dr. Tariq Thomas';

-- MCD: Shahdara South · Shahdara North zones
UPDATE public.delhi_wards
  SET commissioner_email = 'pankaj.agrawal@mcd.delhi.gov.in'
  WHERE zonal_commissioner = 'Pankaj Naresh Agrawal';

-- NDMC Chairman (all NDMC areas)
UPDATE public.delhi_wards
  SET commissioner_email = 'chairman@ndmc.gov.in'
  WHERE zonal_commissioner = 'Keshav Chandra';

-- DCB CEO
UPDATE public.delhi_wards
  SET commissioner_email = 'ceo@dcb.delhi.gov.in'
  WHERE zonal_commissioner = 'Kapil Goyal';
