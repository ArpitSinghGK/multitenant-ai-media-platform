"""Feature entitlement engine — maps a tenant's plan to allowed actions."""
from __future__ import annotations

from ..core.errors import EntitlementError
from ..domain.entitlements import Plan, get_plan
from ..domain.models import Modality, TenantContext


class EntitlementService:
    def plan_for(self, ctx: TenantContext) -> Plan:
        return get_plan(ctx.plan_code)

    def check_modality(self, ctx: TenantContext, modality: Modality) -> None:
        """Raise EntitlementError unless the tenant's plan unlocks `modality`."""
        plan = self.plan_for(ctx)
        if modality not in plan.features:
            raise EntitlementError(
                f"plan '{plan.code}' does not include {modality.value} generation"
            )

    def max_concurrency(self, ctx: TenantContext) -> int:
        return self.plan_for(ctx).max_concurrency
