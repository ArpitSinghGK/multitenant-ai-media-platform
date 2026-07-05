"""ComfyUI adapter — graph/workflow-driven AI video generation on a GPU worker."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .runpod_adapter import RunPodProviderAdapter


class ComfyUIAdapter(RunPodProviderAdapter):
    name = "comfyui"
    supported_modalities = frozenset({Modality.VIDEO})
    cost_weight = 6.0  # heaviest: multi-step video diffusion pipelines
    endpoint_setting = "runpod_endpoint_comfyui"

    def build_payload(self, request: GenerationRequest) -> dict:
        return {
            "input": {
                "prompt": request.prompt,
                # A named server-side workflow graph keeps huge JSON off the wire.
                "workflow": request.params.get("workflow", "txt2video_default"),
                "frames": request.params.get("frames", 48),
                "fps": request.params.get("fps", 12),
            }
        }
