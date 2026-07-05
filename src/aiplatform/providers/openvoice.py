"""OpenVoice adapter — instant voice cloning / TTS on a GPU worker."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .runpod_adapter import RunPodProviderAdapter


class OpenVoiceAdapter(RunPodProviderAdapter):
    name = "openvoice"
    supported_modalities = frozenset({Modality.VOICE})
    cost_weight = 1.5
    endpoint_setting = "runpod_endpoint_openvoice"

    def build_payload(self, request: GenerationRequest) -> dict:
        return {
            "input": {
                "text": request.prompt,
                "reference_audio": request.params.get("reference_audio_url"),
                "language": request.params.get("language", "en"),
            }
        }
