"""FastAPI dependency wiring — assembles the object graph and resolves the tenant.

This is the composition root for a request: it builds (process-cached) singletons
for the registry/services and derives the per-request TenantContext from the JWT.
Swapping in-memory repositories for Postgres-backed ones happens here only.
"""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, Header

from ..config import Settings, get_settings
from ..core.errors import AuthError
from ..core.security import decode_tenant_context
from ..domain.models import TenantContext
from ..infra.runpod_client import RunPodClient
from ..providers.registry import ProviderRegistry, build_default_registry
from ..repositories.base import (
    InMemoryJobRepository,
    InMemoryWalletRepository,
    JobRepository,
    WalletRepository,
)
from ..services.credits import CreditsService
from ..services.entitlements import EntitlementService
from ..services.gateway import GatewayService


@lru_cache
def _registry() -> ProviderRegistry:
    return build_default_registry(RunPodClient(get_settings()))


@lru_cache
def _wallet_repo() -> WalletRepository:
    # Seed a couple of orgs with credits so the demo endpoints are exercisable.
    return InMemoryWalletRepository(seed={"org_demo": 10_000})


@lru_cache
def _job_repo() -> JobRepository:
    return InMemoryJobRepository()


def get_job_repo() -> JobRepository:
    return _job_repo()


def _enqueue(job_id: str) -> None:
    """Hand a job to Celery. Imported lazily so the API boots without a broker."""
    from ..workers.tasks import generate

    generate.delay(job_id)


def get_gateway() -> GatewayService:
    return GatewayService(
        registry=_registry(),
        entitlements=EntitlementService(),
        credits=CreditsService(_wallet_repo()),
        jobs=_job_repo(),
        enqueue=_enqueue,
    )


def get_tenant(
    authorization: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> TenantContext:
    """Resolve the caller from a Bearer JWT (self-hosted Supabase)."""
    if not authorization.lower().startswith("bearer "):
        raise AuthError("missing Bearer token")
    token = authorization.split(" ", 1)[1]
    return decode_tenant_context(token, settings)
