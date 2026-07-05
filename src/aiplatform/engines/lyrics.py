"""Lyrics engine.

Lyrics are LLM/text — light enough to run in-process rather than on a GPU worker.
This engine is a natural seam for a future Claude/Anthropic-backed adapter.
"""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality, ProviderResult
from ..providers.base import ProviderAdapter
from .base import Engine


class LyricsEngine(Engine):
    modality = Modality.LYRICS

    def preprocess(self, request: GenerationRequest) -> GenerationRequest:
        # Enforce a house style hint without mutating the caller's prompt semantics.
        request.params.setdefault("style", "modern-pop")
        return request

    async def run(self, adapter: ProviderAdapter, request: GenerationRequest) -> ProviderResult:
        # TODO: wire a text-LLM adapter (e.g. Anthropic Claude) here.
        return await super().run(adapter, request)
