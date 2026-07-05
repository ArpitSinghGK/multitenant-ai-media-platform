"""Voice engine — TTS + voice conversion (OpenVoice / RVC / Amphion)."""
from __future__ import annotations

from ..domain.models import Modality
from .base import Engine


class VoiceEngine(Engine):
    modality = Modality.VOICE
    # TODO: consent/likeness checks for voice cloning belong here, before invoke.
