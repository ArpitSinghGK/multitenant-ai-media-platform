"""RVC adapter — retrieval-based voice conversion (voice-to-voice) on a GPU worker."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .runpod_adapter import RunPodProviderAdapter


class RVCAdapter(RunPodProviderAdapter):
    name = "rvc"
    supported_modalities = frozenset({Modality.VOICE})
    cost_weight = 2.0
    endpoint_setting = "runpod_endpoint_rvc"

    def build_payload(self, request: GenerationRequest) -> dict:
        return {
            "input": {
                "source_audio": request.params.get("source_audio_url"),
                "model_name": request.params.get("voice_model"),
                "transpose": request.params.get("transpose", 0),
                # `prompt` carries the human-readable label for auditing.
                "label": request.prompt,
            }
        }
