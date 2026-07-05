"""Music engine — text-to-music (AudioCraft / Amphion via the registry)."""
from __future__ import annotations

from ..domain.models import GenerationRequest, Modality
from .base import Engine


class MusicEngine(Engine):
    modality = Modality.MUSIC

    def preprocess(self, request: GenerationRequest) -> GenerationRequest:
        # Clamp duration to protect GPU minutes; providers may narrow further.
        duration = int(request.params.get("duration_s", 15))
        request.params["duration_s"] = max(1, min(duration, 120))
        return request
