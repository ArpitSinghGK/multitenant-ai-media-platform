"""Provider registry — the model-agnostic routing table.

Given a modality (and optionally a pinned provider name), it resolves a concrete
adapter. Selection policy lives here so the rest of the platform never hard-codes
a provider. Add a future model by registering it; no caller changes.
"""
from __future__ import annotations

from ..core.errors import ProviderNotFoundError
from ..domain.models import Modality
from ..infra.runpod_client import RunPodClient
from .amphion import AmphionAdapter
from .audiocraft import AudioCraftAdapter
from .base import ProviderAdapter
from .comfyui import ComfyUIAdapter
from .openvoice import OpenVoiceAdapter
from .rvc import RVCAdapter


class ProviderRegistry:
    def __init__(self, adapters: list[ProviderAdapter]):
        self._by_name: dict[str, ProviderAdapter] = {a.name: a for a in adapters}

    def get(self, name: str) -> ProviderAdapter:
        adapter = self._by_name.get(name)
        if adapter is None:
            raise ProviderNotFoundError(f"unknown provider '{name}'")
        return adapter

    def for_modality(self, modality: Modality) -> list[ProviderAdapter]:
        """All adapters that can serve a modality, cheapest first."""
        candidates = [a for a in self._by_name.values() if a.supports(modality)]
        return sorted(candidates, key=lambda a: a.cost_weight)

    def resolve(self, modality: Modality, preferred: str | None = None) -> ProviderAdapter:
        """Pick an adapter for a request.

        A caller may pin `preferred`; if it can serve the modality we honor it,
        otherwise we fall back to the cheapest capable provider. This is the
        single place routing policy is decided.
        """
        if preferred:
            adapter = self.get(preferred)
            if not adapter.supports(modality):
                raise ProviderNotFoundError(
                    f"provider '{preferred}' cannot serve {modality.value}"
                )
            return adapter

        candidates = self.for_modality(modality)
        if not candidates:
            raise ProviderNotFoundError(f"no provider registered for {modality.value}")
        return candidates[0]


def build_default_registry(runpod: RunPodClient) -> ProviderRegistry:
    """Wire the open-source provider fleet. Extend here as models are added."""
    return ProviderRegistry(
        [
            AudioCraftAdapter(runpod),
            AmphionAdapter(runpod),
            OpenVoiceAdapter(runpod),
            RVCAdapter(runpod),
            ComfyUIAdapter(runpod),
        ]
    )
