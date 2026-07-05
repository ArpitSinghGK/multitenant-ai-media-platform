"""Job status API — poll a submitted generation job (org-scoped)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...core.tenancy import assert_same_tenant
from ...domain.models import Job, TenantContext
from ...repositories.base import JobRepository
from ..deps import get_job_repo, get_tenant

router = APIRouter(prefix="/v1", tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=Job)
def get_job(
    job_id: str,
    ctx: TenantContext = Depends(get_tenant),
    jobs: JobRepository = Depends(get_job_repo),
) -> Job:
    job = jobs.get(job_id)
    # Multi-tenant guard: never expose another org's job.
    assert_same_tenant(ctx, job.org_id)
    return job
