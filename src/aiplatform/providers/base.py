"""The Adapter contract every AI provider must satisfy.

This is the seam that keeps the platform provider-independent. The Control Plane
and engines only ever see `ProviderAdapter`; swapping AudioCraft for a future
model is a registry change, not a business-logic change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain.models import GenerationRequest, Modality, ProviderResult


class ProviderAdapter(ABC):
    """Wraps one open-source or commercial model behind a uniform interface."""

    #: Stable identifier used in the registry, entitlements and job records.
    name: str = "base"

    #: Which modalities this adapter can serve.
    supported_modalities: frozenset[Modality] = frozenset()

    #: Relative credit cost multiplier (1 = baseline). GPU-heavy models cost more.
    cost_weight: float = 1.0

    def supports(self, modality: Modality) -> bool:
        return modality in self.supported_modalities

    @abstractmethod
    def build_payload(self, request: GenerationRequest) -> dict:
        """Translate the neutral request into this provider's native payload."""

    @abstractmethod
    async def invoke(self, request: GenerationRequest) -> ProviderResult:
        """Run inference (typically by dispatching to a RunPod GPU worker) and
        return a normalized result. Implementations must not leak provider-
        specific exceptions — wrap them in a PlatformError."""
