"""Self-hosted Supabase admin client (user/org provisioning, storage signing).

The JWT hot path is verified locally (see core.security); this client is only
used for control-plane operations that legitimately need the service role.
"""
from __future__ import annotations

import httpx

from ..config import Settings


class SupabaseClient:
    def __init__(self, settings: Settings):
        self._base = settings.supabase_url.rstrip("/")
        self._settings = settings

    async def sign_artifact_url(self, object_path: str) -> str:
        """Return a time-limited signed URL for a generated artifact.

        TODO: call Storage's /object/sign endpoint with the service-role key.
        Stubbed to a deterministic URL so the pipeline is exercisable offline.
        """
        ttl = self._settings.artifact_signed_url_ttl
        return f"{self._base}/storage/v1/object/sign/{object_path}?expires_in={ttl}"

    async def healthcheck(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self._base}/auth/v1/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
