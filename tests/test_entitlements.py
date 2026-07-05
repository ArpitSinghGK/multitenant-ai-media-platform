"""Feature entitlement engine + gateway gating by subscription plan."""
import pytest

from aiplatform.core.errors import EntitlementError
from aiplatform.domain.models import GenerationRequest, Modality, TenantContext
from aiplatform.providers.registry import build_default_registry
from aiplatform.repositories.base import InMemoryJobRepository, InMemoryWalletRepository
from aiplatform.services.credits import CreditsService
from aiplatform.services.entitlements import EntitlementService
from aiplatform.services.gateway import GatewayService


def _ctx(plan: str) -> TenantContext:
    return TenantContext(org_id="org", user_id="u1", plan_code=plan)


def test_free_plan_unlocks_only_lyrics():
    svc = EntitlementService()
    svc.check_modality(_ctx("free"), Modality.LYRICS)  # no raise
    with pytest.raises(EntitlementError):
        svc.check_modality(_ctx("free"), Modality.VIDEO)


def test_studio_plan_unlocks_video():
    EntitlementService().check_modality(_ctx("studio"), Modality.VIDEO)


def _gateway() -> tuple[GatewayService, list[str]]:
    enqueued: list[str] = []
    wallet = InMemoryWalletRepository(seed={"org": 10_000})
    return (
        GatewayService(
            registry=build_default_registry(runpod=None),
            entitlements=EntitlementService(),
            credits=CreditsService(wallet),
            jobs=InMemoryJobRepository(),
            enqueue=enqueued.append,
        ),
        enqueued,
    )


def test_gateway_queues_job_and_holds_credits_for_entitled_request():
    gateway, enqueued = _gateway()
    job = gateway.submit(
        _ctx("creator"),
        GenerationRequest(modality=Modality.MUSIC, prompt="lofi beat"),
    )
    assert job.status.value == "queued"
    assert job.credits_hold > 0
    assert enqueued == [job.id]  # handed off to the async plane exactly once


def test_gateway_blocks_unentitled_modality_before_enqueue():
    gateway, enqueued = _gateway()
    with pytest.raises(EntitlementError):
        gateway.submit(
            _ctx("free"),
            GenerationRequest(modality=Modality.VIDEO, prompt="a cat surfing"),
        )
    assert enqueued == []  # nothing queued, no credits spent
