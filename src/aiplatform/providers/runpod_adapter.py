"""Shared base for adapters that dispatch to a RunPod Serverless GPU endpoint.

Each concrete provider only differs in its native payload and how it maps the
worker's response — the transport, retries and auth live here once.
"""
from __future__ import annotations

from ..domain.models import GenerationRequest, ProviderResult
from ..infra.runpod_client import RunPodClient
from .base import ProviderAdapter


class RunPodProviderAdapter(ProviderAdapter):
    """A ProviderAdapter backed by a RunPod Serverless endpoint."""

    #: Settings attribute holding this provider's endpoint URL.
    endpoint_setting: str = ""

    def __init__(self, client: RunPodClient):
        self._client = client

    async def invoke(self, request: GenerationRequest) -> ProviderResult:
        payload = self.build_payload(request)
        raw = await self._client.run(self.endpoint_setting, payload)
        return self.parse_result(raw)

    def parse_result(self, raw: dict) -> ProviderResult:
        """Map the worker's JSON to a normalized ProviderResult.

        Default assumes the worker returns {"output": {"artifact_url": ...}};
        override where a provider differs.
        """
        output = raw.get("output", {})
        return ProviderResult(
            provider=self.name,
            artifact_url=output.get("artifact_url", ""),
            duration_ms=int(output.get("duration_ms", 0)),
            meta=output.get("meta", {}),
        )
