"""Provider registry: model-agnostic resolution, cheapest-first, honored pins."""
import pytest

from aiplatform.core.errors import ProviderNotFoundError
from aiplatform.domain.models import Modality
from aiplatform.providers.registry import build_default_registry


@pytest.fixture
def registry():
    # RunPodClient is never called during resolution, so None is a safe stand-in.
    return build_default_registry(runpod=None)


def test_resolve_picks_cheapest_capable_provider(registry):
    # For voice: openvoice(1.5) < rvc(2.0) < amphion(2.5) → openvoice wins.
    assert registry.resolve(Modality.VOICE).name == "openvoice"


def test_resolve_honors_a_valid_pin(registry):
    adapter = registry.resolve(Modality.VOICE, preferred="rvc")
    assert adapter.name == "rvc"


def test_pin_that_cannot_serve_modality_is_rejected(registry):
    # AudioCraft does music, not video.
    with pytest.raises(ProviderNotFoundError):
        registry.resolve(Modality.VIDEO, preferred="audiocraft")


def test_every_modality_has_at_least_one_provider(registry):
    for modality in Modality:
        if modality is Modality.LYRICS:
            continue  # lyrics is served in-process, not by a GPU adapter
        assert registry.for_modality(modality), f"no provider for {modality}"
