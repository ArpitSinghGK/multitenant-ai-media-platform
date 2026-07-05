"""AudioCraft (MusicGen) adapter — text-to-music on a RunPod GPU worker."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .runpod_adapter import RunPodProviderAdapter


class AudioCraftAdapter(RunPodProviderAdapter):
    name = "audiocraft"
    supported_modalities = frozenset({Modality.MUSIC})
    cost_weight = 3.0  # GPU-heavy diffusion/transformer generation
    endpoint_setting = "runpod_endpoint_audiocraft"

    def build_payload(self, request: GenerationRequest) -> dict:
        return {
            "input": {
                "prompt": request.prompt,
                "duration": request.params.get("duration_s", 15),
                "model": request.params.get("model", "musicgen-medium"),
            }
        }
