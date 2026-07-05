"""Generation API — the public REST/SDK surface for all four modalities.

One uniform endpoint; the modality in the body selects the engine + provider.
This is what the SDK and enterprise API clients call.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...domain.models import GenerationRequest, Job, TenantContext
from ...services.gateway import GatewayService
from ..deps import get_gateway, get_tenant

router = APIRouter(prefix="/v1", tags=["generation"])


@router.post("/generate", response_model=Job, status_code=202)
def create_generation(
    request: GenerationRequest,
    ctx: TenantContext = Depends(get_tenant),
    gateway: GatewayService = Depends(get_gateway),
) -> Job:
    """Submit a generation job. Returns 202 with a QUEUED job to poll via /v1/jobs."""
    return gateway.submit(ctx, request)
