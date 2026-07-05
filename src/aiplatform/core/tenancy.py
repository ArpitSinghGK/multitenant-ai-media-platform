"""Tenant isolation helper.

Every repository query is scoped by org_id. Centralizing the guard here means a
missing scope is a loud failure, not a silent cross-tenant data leak.
"""
from __future__ import annotations

from ..domain.models import TenantContext
from .errors import ForbiddenError


def assert_same_tenant(ctx: TenantContext, resource_org_id: str) -> None:
    """Reject any attempt to touch another organization's resource."""
    if ctx.org_id != resource_org_id:
        raise ForbiddenError("resource belongs to a different organization")
