# CIVIKTA — Cloud Run deploy script
# Run from: civikta/ directory
# Pre-req: gcloud auth login && gcloud auth application-default login

$PROJECT   = "project-0f18c2bf-7bd4-4753-844"
$REGION    = "us-central1"
$MAPS_KEY  = "AIzaSyBBbQdFeOAtu7DyI4Sq8BO_AMQ8K1iMOXM"

$SUPABASE_URL = "https://mfcpuickdbhtgdjaybub.supabase.co"
$SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mY3B1aWNrZGJodGdkamF5YnViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjMxMzUzMCwiZXhwIjoyMDk3ODg5NTMwfQ._PwkSchxYe4nUJ6Q56M1z0Lancvzy7q6v-tFKcYsOfw"

# ── 0. Set project & enable APIs ─────────────────────────────────────────────
Write-Host "`n==> Setting project..." -ForegroundColor Cyan
gcloud config set project $PROJECT

Write-Host "`n==> Enabling Cloud Run + Cloud Build APIs..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# ── 1. Deploy backend ─────────────────────────────────────────────────────────
Write-Host "`n==> Deploying civikta-api (backend)..." -ForegroundColor Cyan

$BACKEND_ENV = @(
  "CIVIKTA_REPO=supabase",
  "CIVIKTA_LLM=gemini",
  "CIVIKTA_AUTH=stub",
  "GEMINI_MODEL=gemini-2.5-flash",
  "SUPABASE_URL=$SUPABASE_URL",
  "SUPABASE_SERVICE_KEY=$SUPABASE_KEY",
  "GCP_PROJECT=$PROJECT",
  "GCP_LOCATION=$REGION"
) -join ","

gcloud run deploy civikta-api `
  --source ./services/api `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 512Mi `
  --cpu 1 `
  --set-env-vars $BACKEND_ENV

if ($LASTEXITCODE -ne 0) { Write-Host "Backend deploy failed." -ForegroundColor Red; exit 1 }

# ── 2. Get backend URL & patch CORS ──────────────────────────────────────────
Write-Host "`n==> Getting backend URL..." -ForegroundColor Cyan
$BACKEND_URL = (gcloud run services describe civikta-api --region $REGION --format "value(status.url)").Trim()
Write-Host "Backend: $BACKEND_URL" -ForegroundColor Green

gcloud run services update civikta-api `
  --region $REGION `
  --update-env-vars "CIVIKTA_CORS_ORIGINS=$BACKEND_URL,http://localhost:3000"

# ── 3. Deploy frontend ────────────────────────────────────────────────────────
Write-Host "`n==> Deploying civikta-web (frontend)..." -ForegroundColor Cyan

gcloud run deploy civikta-web `
  --source ./apps/web `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 512Mi `
  --cpu 1 `
  --build-env-vars "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL,NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$MAPS_KEY"

if ($LASTEXITCODE -ne 0) { Write-Host "Frontend deploy failed." -ForegroundColor Red; exit 1 }

# ── 4. Get frontend URL & patch CORS ─────────────────────────────────────────
$FRONTEND_URL = (gcloud run services describe civikta-web --region $REGION --format "value(status.url)").Trim()
Write-Host "`nFrontend: $FRONTEND_URL" -ForegroundColor Green

gcloud run services update civikta-api `
  --region $REGION `
  --update-env-vars "CIVIKTA_CORS_ORIGINS=$FRONTEND_URL,http://localhost:3000,http://192.168.29.108:3000"

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host "`n======================================" -ForegroundColor Green
Write-Host " CIVIKTA is live!" -ForegroundColor Green
Write-Host " Frontend : $FRONTEND_URL" -ForegroundColor Green
Write-Host " Backend  : $BACKEND_URL" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Green
