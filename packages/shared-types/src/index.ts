// Shared contract types between the Next.js frontend and the FastAPI backend.
//
// For the scaffold these live (and are used) in apps/web/lib/types.ts. The
// intended workflow once the backend stabilises:
//
//   1. FastAPI auto-generates an OpenAPI schema at /openapi.json
//   2. Run `openapi-typescript http://localhost:8000/openapi.json -o src/api.ts`
//   3. Re-export the generated types from here and import from @civikta/shared-types
//
// Until then this package is a placeholder so the monorepo structure matches the
// PRD (§34).

export {};
