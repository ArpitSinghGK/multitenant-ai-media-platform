"""Liveness / readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from ... import __version__

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "version": __version__}
