"""Video engine — workflow-driven AI video (ComfyUI)."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .base import Engine


class VideoEngine(Engine):
    modality = Modality.VIDEO

    def preprocess(self, request: GenerationRequest) -> GenerationRequest:
        request.params.setdefault("fps", 12)
        request.params.setdefault("frames", 48)
        return request
