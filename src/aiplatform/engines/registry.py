"""Modality → Engine lookup for the AI Plane."""
from __future__ import annotations

from ..core.errors import ProviderNotFoundError
from ..domain.models import Modality
from .base import Engine
from .lyrics import LyricsEngine
from .music import MusicEngine
from .video import VideoEngine
from .voice import VoiceEngine

_ENGINES: dict[Modality, Engine] = {
    Modality.LYRICS: LyricsEngine(),
    Modality.MUSIC: MusicEngine(),
    Modality.VOICE: VoiceEngine(),
    Modality.VIDEO: VideoEngine(),
}


def get_engine(modality: Modality) -> Engine:
    engine = _ENGINES.get(modality)
    if engine is None:
        raise ProviderNotFoundError(f"no engine for modality {modality.value}")
    return engine
