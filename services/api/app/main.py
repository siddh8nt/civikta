"""CIVIKTA API entrypoint.

Runs end-to-end with zero external services (stub LLM + in-memory repo, seeded
with demo issues). Visit /docs for the interactive API, /api/config to confirm
which seams are active.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import authority, feed, issues, meta, oversight, reports

settings = get_settings()

app = FastAPI(
    title="CIVIKTA API",
    version="0.1.0",
    description="Delhi civic issue transparency & routing platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (meta.router, reports.router, issues.router, feed.router,
          authority.router, oversight.router):
    app.include_router(r)


@app.get("/")
async def root() -> dict:
    return {"name": "CIVIKTA API", "docs": "/docs", "config": "/api/config"}
