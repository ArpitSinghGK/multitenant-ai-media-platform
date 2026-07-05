"""AI Plane engines — modality-specific orchestration around a provider adapter.

An engine owns the *domain* concerns of a modality (validation, pre/post
processing, safety hooks) while delegating raw inference to whatever adapter the
registry resolved. Keeping this separate from providers means a new provider is
adoptable without touching modality logic, and vice-versa.
"""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality, ProviderResult
from ..providers.base import ProviderAdapter


class Engine:
    modality: Modality

    def preprocess(self, request: GenerationRequest) -> GenerationRequest:
        """Hook for modality-specific normalization. Default: passthrough."""
        return request

    def postprocess(self, result: ProviderResult) -> ProviderResult:
        """Hook for modality-specific finalization. Default: passthrough."""
        return result

    async def run(self, adapter: ProviderAdapter, request: GenerationRequest) -> ProviderResult:
        prepared = self.preprocess(request)
        result = await adapter.invoke(prepared)
        return self.postprocess(result)
