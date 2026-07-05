"""Feature-based subscription plans → what a tenant is allowed to do.

Plans are declarative so a white-label operator can add tiers without code
changes (in production these rows live in Postgres; here they are seeded).
"""
from __future__ import annotations

from pydantic import BaseModel

from .models import Modality


class Plan(BaseModel):
    code: str
    name: str
    # Which modalities this plan unlocks.
    features: frozenset[Modality]
    # Credits granted per billing cycle.
    monthly_credits: int
    # Max concurrent in-flight jobs (queue fairness / abuse control).
    max_concurrency: int


# Seed catalog. A real deployment loads these per white-label tenant.
PLAN_CATALOG: dict[str, Plan] = {
    "free": Plan(
        code="free",
        name="Free",
        features=frozenset({Modality.LYRICS}),
        monthly_credits=100,
        max_concurrency=1,
    ),
    "creator": Plan(
        code="creator",
        name="Creator",
        features=frozenset({Modality.LYRICS, Modality.MUSIC, Modality.VOICE}),
        monthly_credits=5_000,
        max_concurrency=4,
    ),
    "studio": Plan(
        code="studio",
        name="Studio",
        features=frozenset(Modality),  # everything, incl. video
        monthly_credits=50_000,
        max_concurrency=16,
    ),
}


def get_plan(code: str) -> Plan:
    """Resolve a plan, falling back to free for unknown codes."""
    return PLAN_CATALOG.get(code, PLAN_CATALOG["free"])
