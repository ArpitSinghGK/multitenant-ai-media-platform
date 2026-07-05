"""Domain error hierarchy → mapped to HTTP responses in main.py."""
from __future__ import annotations


class PlatformError(Exception):
    """Base class for all expected, client-safe failures."""
    status_code = 400
    code = "platform_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AuthError(PlatformError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(PlatformError):
    status_code = 403
    code = "forbidden"


class EntitlementError(ForbiddenError):
    """Tenant's plan does not include the requested feature."""
    code = "feature_not_entitled"


class InsufficientCreditsError(PlatformError):
    status_code = 402
    code = "insufficient_credits"


class ProviderNotFoundError(PlatformError):
    status_code = 422
    code = "no_provider_for_modality"


class NotFoundError(PlatformError):
    status_code = 404
    code = "not_found"
