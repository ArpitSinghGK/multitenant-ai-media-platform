"""Thin async client for RunPod Serverless endpoints.

Handles auth + transport for GPU dispatch. Kept deliberately small so provider
adapters own their payloads while retry/backoff/polling policy lives in one place.
"""
from __future__ import annotations

import httpx

from ..config import Settings


class RunPodClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self._settings = settings
        self._client = client

    def _endpoint(self, endpoint_setting: str) -> str:
        url = getattr(self._settings, endpoint_setting, "")
        if not url:
            raise RuntimeError(f"RunPod endpoint '{endpoint_setting}' is not configured")
        return url

    async def run(self, endpoint_setting: str, payload: dict) -> dict:
        """Submit a job to a serverless endpoint and return its output.

        TODO: switch to /run + /status polling for long video jobs; /runsync is
        fine for short audio. Left synchronous here to keep the skeleton readable.
        """
        url = self._endpoint(endpoint_setting)
        headers = {"Authorization": f"Bearer {self._settings.runpod_api_key}"}
        client = self._client or httpx.AsyncClient(timeout=600)
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        finally:
            if self._client is None:
                await client.aclose()
