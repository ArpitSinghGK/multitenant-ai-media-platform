"""FastAPI application factory — the Control Plane HTTP surface.

Wires routers, maps domain errors to clean JSON responses, and (in non-test
environments) initializes the Postgres engine at startup.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .core.errors import PlatformError
from .api.routers import generation, health, jobs, wallet


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        summary="Provider-independent AI Gateway for Lyrics, Music, Voice and Video.",
    )

    @app.exception_handler(PlatformError)
    async def _platform_error_handler(_: Request, exc: PlatformError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(health.router)
    app.include_router(generation.router)
    app.include_router(jobs.router)
    app.include_router(wallet.router)
    return app


app = create_app()
