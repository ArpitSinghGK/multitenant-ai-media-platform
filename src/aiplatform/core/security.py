"""JWT verification (self-hosted Supabase) + RBAC helpers.

Supabase signs access tokens with a shared HS256 secret; we verify locally so
the hot path never round-trips to the auth server. Claims carry the org and role.
"""
from __future__ import annotations

from jose import JWTError, jwt

from ..config import Settings
from ..domain.models import Role, TenantContext
from .errors import AuthError, ForbiddenError

# Roles ranked for hierarchical checks (owner ⊇ admin ⊇ developer ⊇ member).
_ROLE_RANK = {Role.MEMBER: 0, Role.DEVELOPER: 1, Role.ADMIN: 2, Role.OWNER: 3}


def decode_tenant_context(token: str, settings: Settings) -> TenantContext:
    """Verify a Supabase JWT and project it onto our TenantContext.

    Raises AuthError on any signature/expiry/claim problem — never trust
    unverified input to identify a tenant.
    """
    try:
        claims = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as exc:  # signature, expiry, audience, etc.
        raise AuthError(f"invalid token: {exc}") from exc

    # Supabase stores custom claims under app_metadata.
    app_meta = claims.get("app_metadata", {})
    org_id = app_meta.get("org_id")
    if not org_id:
        raise AuthError("token missing org_id claim")

    return TenantContext(
        org_id=org_id,
        user_id=claims.get("sub", ""),
        role=Role(app_meta.get("role", Role.MEMBER.value)),
        plan_code=app_meta.get("plan_code", "free"),
    )


def require_role(ctx: TenantContext, minimum: Role) -> None:
    """Enforce a minimum RBAC role; raise ForbiddenError otherwise."""
    if _ROLE_RANK[ctx.role] < _ROLE_RANK[minimum]:
        raise ForbiddenError(f"requires role >= {minimum.value}")
