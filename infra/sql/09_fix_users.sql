-- Fix: add missing password_hash column + restore demo user rows
-- Run in Supabase SQL editor

-- 1. Add password_hash column (no-op if already exists)
alter table public.users add column if not exists password_hash text;

-- 2. Restore demo users with ALL fields (seed only updates name+updated_at on conflict)
insert into public.users(id, name, phone, role, ward_name, ward_no, zone, local_body_type, home_lat, home_lng, is_demo)
values
  ('a1b2c3d4-0001-0001-0001-000000000001','Priya Sharma','9810012345','citizen','Lajpat Nagar II',168,'South West','MCD',28.5677,77.2433,true),
  ('a1b2c3d4-0002-0002-0002-000000000002','Rahul Verma','9899012345','citizen','Defence Colony',169,'South West','MCD',28.5717,77.2294,true),
  ('a1b2c3d4-0003-0003-0003-000000000003','Sunita Kapoor','9811012345','citizen','Mayur Vihar',172,'Shahdara South','MCD',28.6086,77.2992,true),
  ('a1b2c3d4-0004-0004-0004-000000000004','Amit Srivastava','9800012345','authority',null,null,null,'MCD',null,null,true),
  ('a1b2c3d4-0005-0005-0005-000000000005','Dr. Alok Nath','9810099999','oversight',null,null,null,null,null,null,true)
on conflict(id) do update set
  name            = excluded.name,
  phone           = excluded.phone,
  role            = excluded.role,
  ward_name       = excluded.ward_name,
  ward_no         = excluded.ward_no,
  zone            = excluded.zone,
  local_body_type = excluded.local_body_type,
  home_lat        = excluded.home_lat,
  home_lng        = excluded.home_lng,
  is_demo         = excluded.is_demo,
  updated_at      = now();
