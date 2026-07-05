"""Amphion adapter — text-to-audio / singing-voice synthesis on a GPU worker."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .runpod_adapter import RunPodProviderAdapter


class AmphionAdapter(RunPodProviderAdapter):
    name = "amphion"
    supported_modalities = frozenset({Modality.MUSIC, Modality.VOICE})
    cost_weight = 2.5
    endpoint_setting = "runpod_endpoint_amphion"

    def build_payload(self, request: GenerationRequest) -> dict:
        return {
            "input": {
                "text": request.prompt,
                "task": request.params.get("task", "tts"),
                "speaker": request.params.get("speaker"),
            }
        }
