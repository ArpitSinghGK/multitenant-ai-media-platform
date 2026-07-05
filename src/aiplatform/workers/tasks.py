"""Generation task — runs on a Celery worker, dispatches to a RunPod GPU worker.

This closes the credit lifecycle opened by the gateway: on success we settle the
hold (refunding any over-estimate); on failure we refund the whole hold so a
tenant never pays for a job that produced nothing.
"""
from __future__ import annotations

import asyncio

from ..config import get_settings
from ..domain.models import GenerationRequest, JobStatus
from ..engines.registry import get_engine
from ..infra.runpod_client import RunPodClient
from ..providers.registry import build_default_registry
from ..repositories.base import JobRepository, WalletRepository
from ..services.credits import CreditsService
from .celery_app import celery_app


async def _execute(job_id: str, jobs: JobRepository, wallet: WalletRepository) -> None:
    settings = get_settings()
    registry = build_default_registry(RunPodClient(settings))
    credits = CreditsService(wallet)

    job = jobs.get(job_id)
    job.status = JobStatus.RUNNING
    jobs.update(job)

    request = GenerationRequest(**job.request)
    adapter = registry.get(job.provider)
    engine = get_engine(job.modality)

    try:
        result = await engine.run(adapter, request)
        job.result_url = result.artifact_url
        job.status = JobStatus.SUCCEEDED
        # Settle: actual cost == held estimate here; refine with real usage meters.
        credits.settle(job.org_id, job.credits_hold, job.credits_hold)
    except Exception as exc:  # noqa: BLE001 — worker boundary: never lose the hold
        job.status = JobStatus.FAILED
        job.error = str(exc)
        credits.refund(job.org_id, job.credits_hold)
    finally:
        jobs.update(job)


@celery_app.task(name="aiplatform.generate", bind=True, max_retries=2)
def generate(self, job_id: str) -> str:  # noqa: ANN001 — Celery self
    """Celery entrypoint. Repositories are constructed from real backends in
    production wiring; kept as a thin sync shell over the async pipeline."""
    from ..repositories.base import InMemoryJobRepository, InMemoryWalletRepository

    # NOTE: swap these for Postgres-backed repositories in production DI.
    jobs = InMemoryJobRepository()
    wallet = InMemoryWalletRepository()
    asyncio.run(_execute(job_id, jobs, wallet))
    return job_id
