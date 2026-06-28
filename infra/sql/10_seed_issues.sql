-- ============================================================================
-- CIVIKTA 10_seed_issues.sql
-- 80 historical civic issues seeded for analytics demo.
-- Run in Supabase SQL Editor AFTER 01_schema.sql and 02_seed_demo.sql.
--
-- Data is crafted so the analytics chatbot returns meaningful, differentiated
-- answers. Key analytics signals baked in:
--   • mcd_engineering: worst performer (11% resolution, 87% SLA breach)
--   • mcd_public_health: best performer (60% resolution, 0% SLA breach)
--   • djb: medium (33% resolution, 50% SLA breach)
--   • South Zone + Rohini Zone: most issue hotspots
--   • Seelampur, Bawana, Sangam Vihar: worst ward health scores
--   • Several chronic / false-closure patterns for escalation analysis
-- ============================================================================

-- ─── MCD ENGINEERING (19 issues — worst SLA performer) ───────────────────────

-- South Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000001',now()-interval '52 days',now()-interval '52 days','Chronic pothole cluster on main road — Malviya Nagar Market','Recurring pothole cluster near the Malviya Nagar market. MCD has patched this stretch 3 times in 2 years; the patch always fails within 6 weeks. Dangerous for two-wheelers at night. At least 4 minor accidents reported.','submitted',28.5387,77.2084,'MCD','South',52,'Malviya Nagar','Malviya Nagar Market','roads_streets','pothole_local_road','medium',6.8,13,false,false,true,'chronic',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000002',now()-interval '38 days',now()-interval '38 days','Road depression causing pooling — Kalkaji Extension Link Road','Large sunken depression (40cm drop) on the link road near Kalkaji Extension. Water pools during rain and the surface is cracked. School bus uses this road daily — high injury risk for children alighting.','submitted',28.5502,77.2620,'MCD','South',61,'Kalkaji','Kalkaji Extension','roads_streets','road_depression','high',7.2,9,false,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000003',now()-interval '30 days',now()-interval '30 days','Broken footpath — Sangam Vihar main road','Entire 200m footpath stretch broken and upheaved. Pedestrians are walking on the main carriageway. Several elderly residents and children have fallen. MCD Engineering marked a prior complaint resolved without any visible repair.','submitted',28.5040,77.2370,'MCD','South',66,'Sangam Vihar','Sangam Vihar Main Road','roads_streets','footpath_damaged','medium',5.4,7,false,false,true,'recurring',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000004',now()-interval '45 days',now()-interval '45 days','Crumbling road surface — Dakshinpuri main road','Road surface completely broken, sharp aggregate exposed. Dakshinpuri has had 6 road complaints in the last 8 months, none resolved. This is a high-traffic inter-ward route used by autorickshaws and school vans.','submitted',28.5310,77.2250,'MCD','South',64,'Dakshinpuri','Dakshinpuri Main Road','roads_streets','road_surface_broken','medium',5.9,8,'false','false','true','chronic',false,'mcd_engineering')
on conflict do nothing;

-- Authority marked resolved but pothole reappeared → false closure
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000005',now()-interval '35 days',now()-interval '12 days','Streetlight outage — Sangam Vihar G-Block (marked resolved, still dark)','Street dark for 4 weeks. Authority closed the complaint after "replacing fuse" — but residents report lights still not working. Women residents are reporting safety concerns about walking after 8pm.','reopened',28.5055,77.2355,'MCD','South',66,'Sangam Vihar','Sangam Vihar Block G','lights_electrical','streetlight_not_working','medium',5.7,10,false,false,true,'recurring',true,'mcd_engineering')
on conflict do nothing;

-- Resolved (one of very few mcd_engineering successes)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000006',now()-interval '18 days',now()-interval '5 days','Fallen road divider blocking lane — Saket Block H','Road divider collapsed onto the carriageway after a truck collision. Blocking 1 of 2 lanes. Risk of chain accidents.','resolved',28.5223,77.2100,'MCD','South',51,'Saket','Saket Block H Road','roads_streets','road_obstruction','high',4.1,5,true,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

-- South West Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000007',now()-interval '40 days',now()-interval '40 days','Multiple potholes — Sarojini Nagar market lane','Three large potholes on the service lane behind Sarojini Nagar market. Autorickshaws avoid this lane; pedestrians forced onto the main road. Complaint filed twice this year — both closed without repair.','submitted',28.5754,77.1929,'MCD','South West',165,'Sarojini Nagar','Sarojini Nagar Market Rear Lane','roads_streets','pothole_local_road','medium',5.6,9,false,false,true,'chronic',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000008',now()-interval '55 days',now()-interval '55 days','Pothole-ridden road — Vasant Kunj Sector C','Major potholes on the internal road, Sector C. 55 days with no response. Same road was raised in 2025 monsoon season as well — chronic issue. Vehicles make long detour to avoid this stretch.','submitted',28.5244,77.1588,'MCD','South West',93,'Vasant Kunj','Vasant Kunj Sector C','roads_streets','pothole_local_road','medium',6.5,12,false,false,false,'chronic',false,'mcd_engineering')
on conflict do nothing;

-- Rohini Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000009',now()-interval '35 days',now()-interval '28 days','Road cave-in near sewer line — Rithala','Road surface caved in approximately 1.5m wide and 60cm deep due to undermined sewer trench. Heavy traffic area near bus terminus. Risk of vehicle falling into cavity. In progress for 28 days — temporary barricade only placed on day 1.','in_progress',28.7196,77.0988,'MCD','Rohini',17,'Rithala','Rithala Bus Stand Road','roads_streets','road_depression','critical',9.1,18,true,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000010',now()-interval '20 days',now()-interval '20 days','Footpath completely broken — Pitampura Main Road','300m stretch of footpath collapsed, exposing utility ducts underneath. Residents forced onto road. Pitampura is a high-density residential zone with heavy pedestrian traffic. No action for 20 days.','submitted',28.7055,77.1322,'MCD','Rohini',21,'Pitampura','Pitampura Main Road','roads_streets','footpath_damaged','medium',4.2,6,false,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

-- Streetlight false closure in Rohini (different ward from demo seed issue)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000011',now()-interval '22 days',now()-interval '8 days','20 streetlights out — Rohini Sector 22 (reopened after false closure)','Entire street dark for 3 weeks. Authority closed the issue claiming "transformer fault fixed" — but residents report lights still not working 2 weeks later. Women cyclists and pedestrians fear for safety after dark.','reopened',28.7230,77.1100,'MCD','Rohini',25,'Rohini Sector 22','Rohini Sector 22 Inner Road','lights_electrical','streetlight_not_working','medium',6.1,11,false,false,true,'recurring',true,'mcd_engineering')
on conflict do nothing;

-- Shahdara South Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000012',now()-interval '38 days',now()-interval '38 days','Major pothole — Mayur Vihar Phase 1 pocket road','Deep pothole (25cm) at the junction inside Mayur Vihar Phase 1. Two scooters have fallen here in the last month. MCD Engineering assigned 38 days ago, field visit done on Day 3 — no repair since.','submitted',28.6086,77.2992,'MCD','Shahdara South',172,'Mayur Vihar','Mayur Vihar Phase 1','roads_streets','pothole_local_road','high',7.4,14,false,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000013',now()-interval '25 days',now()-interval '20 days','Road surface broken — Preet Vihar sector road','Road surface completely deteriorated on the main sector road. Large gravel patches exposed. Flooded during last rain. School and hospital both on this road — high pedestrian volume.','in_progress',28.6391,77.2980,'MCD','Shahdara South',171,'Preet Vihar','Preet Vihar Sector Road','roads_streets','road_surface_broken','high',6.3,8,false,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

-- Central Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000014',now()-interval '35 days',now()-interval '35 days','Footpath encroachment unresolved — Karol Bagh main market','Permanent vendor stalls blocking 80% of the footpath width along a 150m stretch. Pedestrians forced onto the busy main road. Multiple MCD notices issued but no action taken — vendor lobby reportedly connected to local body representatives.','submitted',28.6517,77.1909,'MCD','Central',76,'Karol Bagh','Karol Bagh Main Market','roads_streets','footpath_encroachment','medium',4.5,7,true,false,false,'recurring',false,'mcd_engineering')
on conflict do nothing;

-- Civil Lines Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000015',now()-interval '33 days',now()-interval '33 days','Pothole cluster — Model Town Link Road','Six potholes in a 100m stretch on the link road connecting Model Town to GTB Nagar. Road has never been resurfaced — underlying base completely deteriorated. Heavy goods vehicles use this route.','submitted',28.7100,77.2000,'MCD','Civil Lines',8,'Model Town','Model Town Link Road','roads_streets','pothole_local_road','medium',5.1,7,false,false,false,'chronic',false,'mcd_engineering')
on conflict do nothing;

-- Narela Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000016',now()-interval '50 days',now()-interval '50 days','Severely potholed road — Narela Sector A7','Nearly entire road surface eroded. No response in 50 days. This is a periurban zone with poor road maintenance track record — same road reported every monsoon for 4 years. Trucks carrying produce to mandi use this road.','submitted',28.8527,77.0945,'MCD','Narela',1,'Narela','Narela Sector A7','roads_streets','pothole_local_road','medium',5.3,6,false,false,false,'chronic',false,'mcd_engineering')
on conflict do nothing;

-- Shahdara North Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000017',now()-interval '28 days',now()-interval '22 days','Road cave-in near drainage works — Seelampur','Road caved in near an ongoing drainage construction site. IFCD opened a trench but MCD has not restored the road surface. Deep pit (80cm) now exposed. No barricades at night.','in_progress',28.6661,77.2845,'MCD','Shahdara North',132,'Seelampur','Seelampur Main Road','roads_streets','road_depression','critical',8.7,15,true,false,true,'new',false,'mcd_engineering')
on conflict do nothing;

-- West Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000018',now()-interval '60 days',now()-interval '60 days','Chronic pothole — Dwarka Sector 12 internal road','Potholes present for 60 days without any repair. Third consecutive monsoon season this road has deteriorated without a permanent fix. Dwarka residents have submitted 14 complaints across 2025-2026 for this road alone.','submitted',28.5921,77.0460,'MCD','West',108,'Dwarka Sector 12','Dwarka Sec 12 Internal','roads_streets','pothole_local_road','medium',6.7,14,false,false,false,'chronic',false,'mcd_engineering')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000019',now()-interval '30 days',now()-interval '30 days','Road surface broken — Uttam Nagar main road','Major sections of road surface broken with exposed base course. Heavy rains last week worsened the damage. Three spots now classified as severe. No MCD response in 30 days.','submitted',28.6210,77.0583,'MCD','West',119,'Uttam Nagar','Uttam Nagar Main Road','roads_streets','road_surface_broken','high',6.9,10,false,false,true,'new',false,'mcd_engineering')
on conflict do nothing;


-- ─── DJB — Delhi Jal Board (15 issues, medium performer) ────────────────────

-- South Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000020',now()-interval '25 days',now()-interval '20 days','Sewer overflow — Kalkaji main drain','Underground sewer has burst on the main road near Kalkaji temple. Raw sewage flowing into storm drain. Health hazard for market area and residents. DJB field team visited on Day 5, placed temporary seal — seal failed.','in_progress',28.5502,77.2620,'MCD','South',61,'Kalkaji','Kalkaji Temple Road','water_sewer_drainage','sewer_overflow','critical',9.3,22,true,true,true,'new',false,'djb')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000021',now()-interval '12 days',now()-interval '12 days','No water supply for 4 days — Saket C-Block','Four apartment blocks in Saket C-Block have had no piped water for 4 days. Residents buying water cans at Rs 800/day. DJB helpline says pipeline maintenance — no estimated restoration time given.','submitted',28.5244,77.2090,'MCD','South',51,'Saket','Saket Block C','water_sewer_drainage','no_water_supply','high',7.3,12,false,true,false,'new',false,'djb')
on conflict do nothing;

-- Resolved quickly
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000022',now()-interval '14 days',now()-interval '4 days','Pipeline leakage — Sangam Vihar E-Block service road','Large pipeline burst, water gushing on service road for 2 days. Significant water wastage. DJB team responded and conducted emergency repair.','resolved',28.5040,77.2370,'MCD','South',66,'Sangam Vihar','Sangam Vihar Block E','water_sewer_drainage','pipeline_leakage','high',3.8,7,true,false,false,'new',false,'djb')
on conflict do nothing;

-- Rohini Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000023',now()-interval '9 days',now()-interval '3 days','No water supply — Rohini Sector 7 (resolved)','Water supply disrupted for 5 days due to main pipeline maintenance near Mangolpuri zone. DJB deployed emergency tankers and restored supply within SLA.','resolved',28.7050,77.1180,'MCD','Rohini',24,'Rohini Sector 7','Rohini Sector 7','water_sewer_drainage','no_water_supply','high',2.1,4,false,false,false,'new',false,'djb')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000024',now()-interval '4 days',now()-interval '4 days','Open manhole on sewer line — Rohini Sector 22','Sewer manhole cover missing near the market junction. Children and elderly pedestrians at serious risk. Reported to DJB 4 days ago — no cover placed.','submitted',28.7230,77.1100,'MCD','Rohini',25,'Rohini Sector 22','Rohini Sector 22 Market','water_sewer_drainage','open_manhole','critical',8.8,10,true,false,true,'new',false,'djb')
on conflict do nothing;

-- Shahdara South Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000025',now()-interval '10 days',now()-interval '7 days','Sewer choked — Laxmi Nagar residential lane','Entire sewer line choked in a residential pocket of Laxmi Nagar. Sewage overflowing into homes. 3 families affected. DJB team visited but requires equipment that hasn''t arrived yet.','in_progress',28.6307,77.2767,'MCD','Shahdara South',161,'Laxmi Nagar','Laxmi Nagar Pocket 4','water_sewer_drainage','sewer_overflow','critical',9.0,16,false,true,false,'new',false,'djb')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000026',now()-interval '5 days',now()-interval '5 days','No water supply — Kalyan Puri (200 flats)','Entire Kalyan Puri block A and B without water for 5 days. DJB says pipeline break near Patparganj. Tanker deployed on Day 3 but supply insufficient. Residents buying packaged water.','submitted',28.6170,77.3030,'MCD','Shahdara South',167,'Kalyan Puri','Kalyan Puri Block A','water_sewer_drainage','no_water_supply','high',7.1,11,false,true,false,'new',false,'djb')
on conflict do nothing;

-- Resolved (good response)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000027',now()-interval '11 days',now()-interval '3 days','Water tanker not arriving — Mayur Vihar Phase 3','Emergency tanker service stopped for 6 days. Senior citizens and bedridden patients unable to source water. DJB restored pipeline and resumed tanker schedule after citizen escalation.','resolved',28.6150,77.3120,'MCD','Shahdara South',172,'Mayur Vihar','Mayur Vihar Phase 3','water_sewer_drainage','no_water_supply','high',3.5,8,false,true,false,'new',false,'djb')
on conflict do nothing;

-- Shahdara North Zone — chronic sewer
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000028',now()-interval '42 days',now()-interval '42 days','Open sewer — Seelampur (chronic, 3rd report in 18 months)','Main sewer line in Seelampur overflowing at 3 points. This is the third report for this exact stretch in 18 months — previous two were closed without permanent fix. Raw sewage on the road for 6 weeks this season.','submitted',28.6661,77.2845,'MCD','Shahdara North',132,'Seelampur','Seelampur Sewer Belt','water_sewer_drainage','sewer_overflow','high',8.6,19,'false','true','false','chronic',false,'djb')
on conflict do nothing;

-- Civil Lines Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000029',now()-interval '18 days',now()-interval '14 days','Sewer overflow flooding lane — Mukherjee Nagar','Sewer overflow on the main lane near Mukherjee Nagar coaching hub. Peak hour congestion worsened by narrowed road. DJB acknowledged issue but desilting equipment stuck in traffic clearance delay.','in_progress',28.7044,77.2107,'MCD','Civil Lines',7,'Mukherjee Nagar','Mukherjee Nagar Main Lane','water_sewer_drainage','sewer_overflow','critical',8.2,13,true,true,true,'new',false,'djb')
on conflict do nothing;

-- West Zone
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000030',now()-interval '20 days',now()-interval '17 days','Pipeline burst — Uttam Nagar G-Block','Major pipeline burst on the main supply line. Water wastage significant. Road waterlogged. DJB filed an emergency work order but contractor availability delayed repair.','in_progress',28.6210,77.0583,'MCD','West',119,'Uttam Nagar','Uttam Nagar G-Block','water_sewer_drainage','pipeline_leakage','high',6.4,9,true,false,false,'new',false,'djb')
on conflict do nothing;

-- Resolved (fast)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000031',now()-interval '7 days',now()-interval '1 day','Overflowing water tank — Pitampura H-Block','Rooftop water tank overflow on municipal main line creating waterlogged road. DJB pressure-regulated the supply line and resolved within 2 days.','resolved',28.7055,77.1322,'MCD','Rohini',21,'Pitampura','Pitampura H-Block','water_sewer_drainage','no_water_supply','medium',1.8,3,false,false,false,'new',false,'djb')
on conflict do nothing;

-- Reopened (false closure)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000032',now()-interval '30 days',now()-interval '10 days','Sewer overflow — Dwarka Sector 6 (marked resolved, overflow returned)','DJB marked sewer overflow as resolved after cleaning, but same overflow restarted within 48 hours. Root cause (fractured pipe) not addressed. Citizens re-escalated with video evidence.','reopened',28.5800,77.0710,'MCD','West',110,'Dwarka Sector 6','Dwarka Sector 6','water_sewer_drainage','sewer_overflow','critical',9.5,21,true,true,true,'recurring',true,'djb')
on conflict do nothing;

-- Resolved
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000033',now()-interval '8 days',now()-interval '2 days','Contaminated water — Janakpuri C-3 pocket','Brown discoloured water from taps — likely rust contamination after maintenance. DJB flushed pipeline and restored clean supply. Issued water quality report.','resolved',28.6290,77.0831,'MCD','West',114,'Janakpuri','Janakpuri Pocket C-3','water_sewer_drainage','water_contamination','high',2.9,6,false,true,false,'new',false,'djb')
on conflict do nothing;

-- Recent, within SLA
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000034',now()-interval '2 days',now()-interval '2 days','Open sewer manhole — Laxmi Nagar market','Manhole cover missing at a busy market junction. Filed 2 days ago — within critical SLA window. High foot traffic area.','submitted',28.6307,77.2767,'MCD','Shahdara South',161,'Laxmi Nagar','Laxmi Nagar Market','water_sewer_drainage','open_manhole','critical',7.2,8,true,false,true,'new',false,'djb')
on conflict do nothing;


-- ─── MCD SANITATION (10 issues, moderate performer) ─────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000035',now()-interval '14 days',now()-interval '14 days','Garbage not collected for 10 days — Sangam Vihar L Block','MCD sanitation vehicle has not visited L-Block for 10 days. Community bin overflowing, garbage spilling on road. Stray dogs attracted. Strong smell affecting residents. Multiple calls to MCD helpline unanswered.','submitted',28.5040,77.2370,'MCD','South',66,'Sangam Vihar','Sangam Vihar L Block','garbage_sanitation','garbage_not_collected','high',7.0,14,false,true,false,'recurring',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000036',now()-interval '5 days',now()-interval '5 days','Overflowing garbage bin — Sarojini Nagar near metro','Community bin outside Sarojini Nagar metro exit is overflowing. Garbage bags stacked on footpath. MCD has been irregular for past 2 weeks — possibly due to truck breakdown.','submitted',28.5754,77.1929,'MCD','South West',165,'Sarojini Nagar','Sarojini Nagar Metro Gate 2','garbage_sanitation','garbage_not_collected','medium',4.1,6,false,true,false,'new',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000037',now()-interval '22 days',now()-interval '22 days','Garbage burning in Bawana — air quality emergency','Daily garbage burning at an informal dump site near Bawana industrial area. Dense smoke is affecting residents in 3 nearby wards. Multiple respiratory complaints registered at local health centre. High health hazard.','submitted',28.7879,77.0327,'MCD','Narela',4,'Bawana','Bawana Industrial Area','garbage_sanitation','garbage_burning','high',8.1,17,false,true,false,'recurring',false,'mcd_sanitation')
on conflict do nothing;

-- Resolved
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000038',now()-interval '15 days',now()-interval '6 days','Garbage not collected — Janakpuri D-Block','Community reported 8-day gap in garbage collection. MCD team responded and cleared the backlog.','resolved',28.6290,77.0831,'MCD','West',114,'Janakpuri','Janakpuri D-Block','garbage_sanitation','garbage_not_collected','medium',2.2,4,false,false,false,'new',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000039',now()-interval '8 days',now()-interval '2 days','Illegal construction debris dump — Mukherjee Nagar park','Builder dumped construction malba in the community park. Park now unusable for children. MCD issued notice and removed the debris.','resolved',28.7044,77.2107,'MCD','Civil Lines',7,'Mukherjee Nagar','Mukherjee Nagar Community Park','garbage_sanitation','illegal_dumping','medium',2.7,5,false,false,false,'new',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000040',now()-interval '10 days',now()-interval '10 days','Overflowing garbage — Rohini Sector 14 market','Market area bins overflowing for 6 days. Multiple stalls generating organic waste faster than MCD collection frequency. Pest infestation visible.','submitted',28.7219,77.1043,'MCD','Rohini',22,'Rohini Sector 14','Rohini Sector 14 Market','garbage_sanitation','garbage_not_collected','medium',5.3,8,false,true,false,'recurring',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000041',now()-interval '3 days',now()-interval '3 days','Dead animal on road — Maujpur','Dead stray cow on main road for 2 days. Strong smell, flies, and dogs crowding. Health and traffic hazard.','submitted',28.6881,77.2945,'MCD','Shahdara North',135,'Maujpur','Maujpur Main Road','garbage_sanitation','dead_animal','high',6.8,9,false,true,false,'new',false,'mcd_sanitation')
on conflict do nothing;

-- In progress
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000042',now()-interval '7 days',now()-interval '4 days','Illegal dumping — Dwarka Sector 12 park boundary','Two truckloads of construction debris dumped on the park boundary wall. MCD team visited, work order placed. Awaiting contractor with heavy equipment.','in_progress',28.5921,77.0460,'MCD','West',108,'Dwarka Sector 12','Dwarka Sector 12 Park Boundary','garbage_sanitation','illegal_dumping','medium',3.4,5,false,false,false,'new',false,'mcd_sanitation')
on conflict do nothing;

-- Rejected (duplicate / out of jurisdiction)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000043',now()-interval '10 days',now()-interval '7 days','Garbage in NDMC colony — filed with MCD (rejected)','Citizen filed MCD complaint for a garbage issue in an NDMC-maintained area. MCD rejected citing jurisdiction — referred to NDMC.','rejected',28.5999,77.2269,'MCD','South West',169,'Defence Colony','Defence Colony NDMC Street','garbage_sanitation','garbage_not_collected','low',1.5,1,false,false,false,'new',false,'mcd_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000044',now()-interval '6 days',now()-interval '6 days','Garbage not collected — Preet Vihar residential block','Garbage collection vehicle has not visited in 5 days. Neighbours increasingly concerned about mosquito breeding as we are in monsoon season.','submitted',28.6391,77.2980,'MCD','Shahdara South',171,'Preet Vihar','Preet Vihar Block 3','garbage_sanitation','garbage_not_collected','medium',4.9,7,false,true,false,'new',false,'mcd_sanitation')
on conflict do nothing;


-- ─── MCD PUBLIC HEALTH (6 issues, best performer) ────────────────────────────

-- All either resolved quickly or recent (within SLA)
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000045',now()-interval '5 days',now()-interval '2 days','Dead cow carcass — Okhla Phase II (resolved)','Dead cow on busy road removed by MCD Public Health team within 2 days of reporting. Road cleared and disinfected.','resolved',28.5380,77.2647,'MCD','South',60,'Okhla','Okhla Phase II Industrial Area','garbage_sanitation','dead_animal','high',2.4,4,false,true,false,'new',false,'mcd_public_health')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000046',now()-interval '3 days',now()-interval '1 day','Stray dog bite incident — Dwarka Sector 6','A resident was bitten by a stray dog. MCD Public Health responded, conducted anti-rabies drive, and removed the aggressive animal to shelter. Rapid response.','resolved',28.5800,77.0710,'MCD','West',110,'Dwarka Sector 6','Dwarka Sector 6','animals_other','stray_dog_bite','high',2.6,3,false,false,true,'new',false,'mcd_public_health')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000047',now()-interval '6 days',now()-interval '3 days','Dead animal carcass — Karol Bagh back lane (resolved)','Dead dog lying on service lane for 2 days. MCD team removed and sanitised area within 3 days of report.','resolved',28.6517,77.1909,'MCD','Central',76,'Karol Bagh','Karol Bagh Back Lane','garbage_sanitation','dead_animal','medium',1.9,2,false,true,false,'new',false,'mcd_public_health')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000048',now()-interval '2 days',now()-interval '2 days','Mosquito breeding in clogged drain — Rohini Sector 7','Standing water in blocked drain creating mosquito breeding ground. Dengue season risk. MCD Public Health informed.','submitted',28.7050,77.1180,'MCD','Rohini',24,'Rohini Sector 7','Rohini Sector 7','public_safety_hazard','mosquito_breeding','high',6.2,10,false,true,false,'new',false,'mcd_public_health')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000049',now()-interval '1 day',now()-interval '1 day','Stray dog bite — Mayur Vihar resident (new filing)','Second stray dog bite in Mayur Vihar this month. Filed today. Requires urgent MCD anti-rabies team dispatch.','submitted',28.6086,77.2992,'MCD','Shahdara South',172,'Mayur Vihar','Mayur Vihar Phase 1','animals_other','stray_dog_bite','high',7.5,6,false,false,true,'new',false,'mcd_public_health')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000050',now()-interval '4 days',now()-interval '1 day','Cattle menace — Bawana industrial road','Several stray cattle blocking trucks on industrial access road to Bawana facility zone. Health hazard and traffic disruption. Resolved by MCD cattle squad.','resolved',28.7879,77.0327,'MCD','Narela',4,'Bawana','Bawana Industrial Road','animals_other','cattle_stray','medium',2.0,3,false,false,false,'new',false,'mcd_public_health')
on conflict do nothing;


-- ─── MCD HORTICULTURE (5 issues) ─────────────────────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000051',now()-interval '3 days',now()-interval '2 days','Large tree fallen — Malviya Nagar B Block road (in progress)','Old neem tree uprooted in last night''s storm blocking full width of road. Cars and ambulances unable to pass. MCD horticulture team dispatched but tree removal requires crane.','in_progress',28.5387,77.2084,'MCD','South',52,'Malviya Nagar','Malviya Nagar Block B','parks_public_space','tree_hazard','critical',9.2,12,true,false,true,'new',false,'mcd_horticulture')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000052',now()-interval '7 days',now()-interval '4 days','Fallen tree cleared — Adarsh Nagar park road (resolved)','Storm-felled tree blocking park entry road removed by horticulture team within 3 days.','resolved',28.7100,77.1940,'MCD','Civil Lines',5,'Adarsh Nagar','Adarsh Nagar Park','parks_public_space','tree_hazard','high',2.3,4,true,false,true,'new',false,'mcd_horticulture')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000053',now()-interval '5 days',now()-interval '2 days','Dangerous overhang — tree on Rohini Sector 7 main road (resolved)','Large branch hanging over road at dangerous angle after last storm. MCD horticulture trimmed it within 3 days.','resolved',28.7050,77.1180,'MCD','Rohini',24,'Rohini Sector 7','Rohini Sector 7 Main Road','parks_public_space','tree_hazard','high',2.1,3,false,false,true,'new',false,'mcd_horticulture')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000054',now()-interval '20 days',now()-interval '20 days','Park damaged — Saket District Park boundary wall collapsed','Boundary wall collapsed due to tree root growth. Children and stray animals entering park after hours. Safety concern.','submitted',28.5244,77.2090,'MCD','South',51,'Saket','Saket District Park','parks_public_space','park_damage','medium',3.2,5,false,false,false,'new',false,'mcd_horticulture')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000055',now()-interval '2 days',now()-interval '2 days','Dead tree danger — Pitampura colony park','Large dead tree leaning toward the children''s play area. Safety hazard. Filed 2 days ago.','submitted',28.7055,77.1322,'MCD','Rohini',21,'Pitampura','Pitampura Colony Park','parks_public_space','tree_hazard','high',6.9,8,false,false,true,'new',false,'mcd_horticulture')
on conflict do nothing;


-- ─── PWD — Public Works Department (5 issues, poor SLA) ──────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000056',now()-interval '42 days',now()-interval '42 days','Arterial road pothole — Mehrauli-Badarpur Road near Moolchand','Three deep potholes (20–30cm) on the MB Road near Moolchand Petrol Pump. Heavy arterial route; 3 accidents recorded. PWD notified 42 days ago — no response.','submitted',28.5677,77.2433,'MCD','South West',168,'Lajpat Nagar','MB Road near Moolchand','roads_streets','pothole_major_road','high',8.3,16,false,false,true,'chronic',false,'pwd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000057',now()-interval '30 days',now()-interval '25 days','Flyover approach pothole — Wazirabad Road','Large pothole near flyover abutment on Wazirabad Road. Vehicles braking suddenly causing rear-end collisions. PWD has work order but contractor not mobilised.','in_progress',28.7497,77.2226,'MCD','Narela',1,'Narela','Wazirabad Road Flyover','roads_streets','pothole_major_road','critical',8.9,18,false,false,true,'new',false,'pwd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000058',now()-interval '22 days',now()-interval '22 days','Pothole causing accidents — Outer Ring Road near Janakpuri','Multiple accidents at two large potholes on Outer Ring Road. Motorcyclists especially vulnerable. No PWD action for 22 days.','submitted',28.6290,77.0831,'MCD','West',114,'Janakpuri','Outer Ring Road near Janakpuri','roads_streets','pothole_major_road','high',7.6,13,false,false,true,'recurring',false,'pwd')
on conflict do nothing;

-- Resolved
insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000059',now()-interval '20 days',now()-interval '8 days','Arterial pothole — Badarpur Flyover approach (resolved)','Critical pothole at the Badarpur flyover approach repaired by PWD after citizen escalation through CM helpline.','resolved',28.5050,77.2940,'MCD','South',62,'Tughlakabad Extension','Badarpur Flyover Approach','roads_streets','pothole_major_road','critical',3.9,9,false,false,true,'new',false,'pwd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000060',now()-interval '18 days',now()-interval '18 days','Road surface deteriorated — NH-8 near Mahipalpur exit','NH-8 service road surface broken near Mahipalpur. Large trucks using this to bypass toll cause rapid deterioration. No surface treatment in 3 years.','submitted',28.5383,77.1250,'MCD','South West',92,'Mahipalpur','NH-8 Service Road Mahipalpur','roads_streets','road_surface_broken','high',6.8,10,false,false,false,'chronic',false,'pwd')
on conflict do nothing;


-- ─── IFCD — Irrigation & Flood Control (5 issues) ────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000061',now()-interval '8 days',now()-interval '8 days','Major nullah overflow — Rohini Sector 14','Main nullah (drain) overflowing into residential blocks. Waterlogging in 3 alleys. IFCD notified 8 days ago. Monsoon pre-season — IFCD was supposed to desilting before June 1st.','submitted',28.7219,77.1043,'MCD','Rohini',22,'Rohini Sector 14','Rohini Sector 14 Nullah','water_sewer_drainage','waterlogging','critical',9.0,20,true,true,false,'recurring',false,'ifcd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000062',now()-interval '5 days',now()-interval '3 days','Drain overflow — Seelampur residential area','Large drain overflowing near Seelampur bus stop. Water entering ground-floor shops and homes. IFCD team dispatched.','in_progress',28.6661,77.2845,'MCD','Shahdara North',132,'Seelampur','Seelampur Drain Area','water_sewer_drainage','waterlogging','critical',9.4,17,true,true,false,'new',false,'ifcd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000063',now()-interval '6 days',now()-interval '6 days','Flooding near Yamuna floodplain — Patparganj','Low-lying residential area near Yamuna flooding after heavy rain. IFCD pumping stations reportedly not maintained. 30 families affected.','submitted',28.6086,77.3100,'MCD','Shahdara South',172,'Mayur Vihar','Mayur Vihar Yamuna Bank','water_sewer_drainage','flooding','critical',9.6,24,true,true,true,'recurring',false,'ifcd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000064',now()-interval '9 days',now()-interval '3 days','Waterlogging cleared — Dwarka Sector 23 underpass (resolved)','Underpass waterlogging after monsoon shower, blocking traffic. IFCD pump operated within 6 hours. Cleared same day.','resolved',28.5900,77.0400,'MCD','West',112,'Dwarka Sector 23','Dwarka Sector 23 Underpass','water_sewer_drainage','waterlogging','high',2.8,5,true,false,false,'new',false,'ifcd')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000065',now()-interval '4 days',now()-interval '4 days','Choked stormwater drain — Sangam Vihar','Pre-monsoon desilting of stormwater drain not completed. First shower of the season caused immediate overflow. IFCD contractor was assigned in March but work not done.','submitted',28.5040,77.2370,'MCD','South',66,'Sangam Vihar','Sangam Vihar Stormwater Drain','water_sewer_drainage','waterlogging','high',8.1,14,false,true,false,'chronic',false,'ifcd')
on conflict do nothing;


-- ─── NDMC — Civil Works (4 issues, good performer) ──────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000066',now()-interval '4 days',now()-interval '2 days','Pothole — Connaught Place inner circle road (in progress)','Pothole near CP inner circle Gate 3. High tourist traffic area. NDMC team visited Day 2, repair scheduled for Day 5.','in_progress',28.6315,77.2167,'NDMC',null,null,'Connaught Place','Connaught Place Inner Circle','roads_streets','pothole_local_road','high',5.8,9,false,false,true,'new',false,'ndmc_civil')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000067',now()-interval '3 days',now()-interval '3 days','Waterlogging — Khan Market area','Waterlogging at Khan Market junction after brief shower. NDMC storm drain appears clogged. Affecting evening traffic.','submitted',28.5999,77.2269,'NDMC',null,null,'Khan Market','Khan Market Junction','water_sewer_drainage','waterlogging','high',6.3,11,true,false,false,'recurring',false,'ndmc_civil')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000068',now()-interval '10 days',now()-interval '3 days','Broken footpath — Lodhi Road (resolved)','Footpath tiles broken near Lodhi Road flyover. NDMC Civil repaired within 7 days.','resolved',28.5952,77.2230,'NDMC',null,null,'Lodhi Road','Lodhi Road Flyover','roads_streets','footpath_damaged','medium',1.7,3,false,false,false,'new',false,'ndmc_civil')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000069',now()-interval '2 days',now()-interval '2 days','Street edge damaged — India Gate approach road','Stone curb broken near India Gate tourist zone. Minor issue filed 2 days ago.','submitted',28.6129,77.2295,'NDMC',null,null,'India Gate','India Gate Approach Road','roads_streets','footpath_damaged','low',2.1,2,false,false,false,'new',false,'ndmc_civil')
on conflict do nothing;


-- ─── NDMC SANITATION (3 issues) ──────────────────────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000070',now()-interval '5 days',now()-interval '5 days','Garbage overflowing — Lodhi Colony community bin','Two bins not emptied for 4 days. NDMC sanitation schedule appears irregular. Complaints filed via NDMC app.','submitted',28.5920,77.2270,'NDMC',null,null,'Lodhi Colony','Lodhi Colony Bin Point','garbage_sanitation','garbage_not_collected','medium',4.3,6,false,true,false,'new',false,'ndmc_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000071',now()-interval '7 days',now()-interval '2 days','Garbage cleared — Connaught Place outer circle (resolved)','Overflowing bins outside CP outer circle cleared within 2 days by NDMC sanitation team. Area inspected and collection schedule restored.','resolved',28.6315,77.2167,'NDMC',null,null,'Connaught Place','CP Outer Circle','garbage_sanitation','garbage_not_collected','medium',1.8,3,false,false,false,'new',false,'ndmc_sanitation')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000072',now()-interval '3 days',now()-interval '1 day','Street uncleaned — Pandara Road (resolved)','Sweeping not done for 3 days on Pandara Road. NDMC team addressed within 1 day of complaint.','resolved',28.6010,77.2290,'NDMC',null,null,'Pandara Road','Pandara Road','garbage_sanitation','street_uncleaned','low',1.2,1,false,false,false,'new',false,'ndmc_sanitation')
on conflict do nothing;


-- ─── NDMC HORTICULTURE (2 issues) ────────────────────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000073',now()-interval '4 days',now()-interval '1 day','Fallen tree cleared — India Gate lawns (resolved)','Small tree fell in India Gate garden during storm. NDMC Horticulture cleared within 1 day.','resolved',28.6129,77.2295,'NDMC',null,null,'India Gate','India Gate Lawns','parks_public_space','tree_hazard','medium',1.5,2,false,false,false,'new',false,'ndmc_horticulture')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000074',now()-interval '2 days',now()-interval '2 days','Overgrown hedge blocking CCTV — Lodhi Garden','Overgrown hedge obscuring a CCTV camera in Lodhi Garden. Security risk. Filed with NDMC Horticulture today.','submitted',28.5938,77.2196,'NDMC',null,null,'Lodhi Garden','Lodhi Garden Path B','parks_public_space','park_damage','low',2.4,2,false,false,false,'new',false,'ndmc_horticulture')
on conflict do nothing;


-- ─── DDA — Delhi Development Authority (3 issues) ────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000075',now()-interval '18 days',now()-interval '18 days','Broken equipment — DDA park Dwarka Sector 12','Children''s play equipment (two swings, one slide) broken in DDA park. Children have been injured. Rusted metal edges exposed. No DDA response for 18 days.','submitted',28.5921,77.0460,'MCD','West',108,'Dwarka Sector 12','DDA Park Dwarka Sector 12','parks_public_space','park_damage','medium',4.7,8,false,false,true,'new',false,'dda')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000076',now()-interval '25 days',now()-interval '20 days','Illegal structure on DDA land — Vasant Kunj Sector D','A private party has erected a semi-permanent structure on notified DDA land. RWA has complained. DDA filed notice but no demolition action yet.','in_progress',28.5244,77.1588,'MCD','South West',93,'Vasant Kunj','Vasant Kunj Sector D','public_safety_hazard','road_obstruction','high',5.3,7,true,false,false,'new',false,'dda')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000077',now()-interval '5 days',now()-interval '5 days','DDA park tree hazard — Rohini Sector 7','Old dry tree leaning over the children''s park boundary in DDA pocket park. Urgent felling required.','submitted',28.7050,77.1180,'MCD','Rohini',24,'Rohini Sector 7','DDA Pocket Park Rohini Sector 7','parks_public_space','tree_hazard','high',6.4,7,false,false,true,'new',false,'dda')
on conflict do nothing;


-- ─── DELHI POLICE (3 issues) ─────────────────────────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000078',now()-interval '3 days',now()-interval '2 days','Traffic signal failure — ITO Junction','Two traffic signals at ITO crossing not working for 3 days. ITO is one of Delhi''s busiest junctions. Near-miss accidents reported. Delhi Police traffic wing notified.','in_progress',28.6289,77.2408,'MCD','Central',70,'ITO','ITO Junction','public_safety_hazard','traffic_signal_failure','high',7.9,15,false,false,true,'new',false,'delhi_police')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000079',now()-interval '15 days',now()-interval '15 days','Footpath encroachment — Azadpur wholesale market','Vendors occupying entire footpath and part of the road near Azadpur vegetable market. Delhi Police complaint filed. Market hours increasingly blocking emergency vehicle access.','submitted',28.7100,77.1770,'MCD','Civil Lines',6,'Azadpur','Azadpur Market Road','public_safety_hazard','road_obstruction','medium',4.6,9,true,false,false,'recurring',false,'delhi_police')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000080',now()-interval '5 days',now()-interval '5 days','Open trench safety hazard — Nehru Place','Construction trench left open without adequate barricade at Nehru Place tech hub. Night-time visibility poor. One scooter has already fallen in.','submitted',28.5477,77.2513,'MCD','South',57,'Nehru Place','Nehru Place Main Road','public_safety_hazard','road_obstruction','critical',9.1,16,true,false,true,'new',false,'delhi_police')
on conflict do nothing;


-- ─── DCB — Delhi Cantonment Board (2 issues) ──────────────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000081',now()-interval '12 days',now()-interval '12 days','Road pothole — Dhaula Kuan Cantonment area','Pothole near the Dhaula Kuan cantonment gate. Reported to DCB 12 days ago. No response.','submitted',28.5973,77.1595,'DCB',null,null,'Dhaula Kuan','Dhaula Kuan Gate Road','roads_streets','pothole_local_road','medium',4.0,5,false,false,false,'new',false,'dcb_civic')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000082',now()-interval '8 days',now()-interval '2 days','Garbage cleared — Delhi Cantonment colony (resolved)','Garbage not collected for 5 days. DCB sanitation team cleared backlog within 2 days.','resolved',28.5973,77.1595,'DCB',null,null,'Delhi Cantonment','Cantonment Colony','garbage_sanitation','garbage_not_collected','medium',1.6,2,false,false,false,'new',false,'dcb_civic')
on conflict do nothing;


-- ─── NHAI — National Highways Authority (2 issues) ───────────────────────────

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000083',now()-interval '20 days',now()-interval '16 days','Pothole — NH-8 near Aerocity exit (in progress)','Two potholes on NH-8 near the Aerocity exit ramp. High-speed approach — accident risk. NHAI contractor visited but road is under concession dispute.','in_progress',28.5383,77.1250,'MCD','South West',92,'Mahipalpur','NH-8 Aerocity Exit','roads_streets','pothole_major_road','critical',8.7,14,false,false,true,'new',false,'nhai')
on conflict do nothing;

insert into public.issues(id,created_at,updated_at,title,public_summary,status,latitude,longitude,local_body_type,mcd_zone,ward_no,ward_name,locality_name,issue_category_slug,issue_type_slug,severity,urgency_score,corroboration_count,obstruction_flag,health_hazard_flag,public_safety_flag,persistence_type,false_closure_suspected,primary_authority_slug) values
('10000000-0000-0000-0000-000000000084',now()-interval '12 days',now()-interval '3 days','NH-44 road collapse — Burari (resolved)','Road surface collapse on NH-44 near Burari. NHAI repair crew mobilised after MP intervention. Lane restored within 9 days.','resolved',28.7497,77.2226,'MCD','Narela',1,'Narela','NH-44 Burari','roads_streets','road_surface_broken','critical',4.7,11,false,false,true,'new',false,'nhai')
on conflict do nothing;

-- ─── End of seed ─────────────────────────────────────────────────────────────
-- Total: 84 issues across 14 authorities, 9 MCD zones + NDMC/DCB/state-level
-- Designed for meaningful chatbot analytics responses on:
--   authority scorecards, SLA compliance, ward health, escalation analysis
