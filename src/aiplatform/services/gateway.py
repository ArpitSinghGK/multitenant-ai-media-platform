"""AI Gateway — the single entry point that turns a request into a queued job.

Control-plane sequence (all provider-independent):
    1. entitlement check  — is this tenant's plan allowed this modality?
    2. provider resolve   — pick an adapter via the registry (model-agnostic)
    3. credit quote+hold  — reserve credits before spending GPU time
    4. persist job        — QUEUED, scoped to the org
    5. enqueue            — hand off to Celery → RunPod GPU worker

Actual inference happens off this thread in workers.tasks; settle/refund of the
credit hold is finalized there based on the outcome.
"""
from __future__ import annotations

from ..domain.models import GenerationRequest, Job, JobStatus, TenantContext
from ..providers.registry import ProviderRegistry
from ..repositories.base import JobRepository
from .credits import CreditsService
from .entitlements import EntitlementService


class GatewayService:
    def __init__(
        self,
        registry: ProviderRegistry,
        entitlements: EntitlementService,
        credits: CreditsService,
        jobs: JobRepository,
        enqueue,  # callable(job_id) -> None; injected so tests stay synchronous
    ):
        self._registry = registry
        self._entitlements = entitlements
        self._credits = credits
        self._jobs = jobs
        self._enqueue = enqueue

    def submit(self, ctx: TenantContext, request: GenerationRequest) -> Job:
        # 1. Entitlement — fail fast before touching credits or providers.
        self._entitlements.check_modality(ctx, request.modality)

        # 2. Model-agnostic provider resolution.
        adapter = self._registry.resolve(request.modality, request.provider)

        # 3. Quote and hold credits up front.
        cost = self._credits.quote(request.modality, adapter)
        self._credits.hold(ctx.org_id, cost)

        # 4. Persist the job (org-scoped) in QUEUED state.
        job = self._jobs.create(
            Job(
                org_id=ctx.org_id,
                user_id=ctx.user_id,
                modality=request.modality,
                provider=adapter.name,
                credits_hold=cost,
                status=JobStatus.QUEUED,
                request=request.model_dump(mode="json"),
            )
        )

        # 5. Hand off to the async plane.
        self._enqueue(job.id)
        return job
