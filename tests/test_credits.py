"""Credits engine: pricing math and the hold → settle / refund lifecycle."""
import pytest

from aiplatform.core.errors import InsufficientCreditsError
from aiplatform.domain.models import Modality
from aiplatform.providers.audiocraft import AudioCraftAdapter
from aiplatform.repositories.base import InMemoryWalletRepository
from aiplatform.services.credits import CreditsService


def _service(balance: int) -> tuple[CreditsService, InMemoryWalletRepository]:
    wallet = InMemoryWalletRepository(seed={"org": balance})
    return CreditsService(wallet), wallet


def test_quote_applies_provider_cost_weight():
    svc, _ = _service(0)
    # music base (10) * audiocraft weight (3.0) = 30
    assert svc.quote(Modality.MUSIC, AudioCraftAdapter(client=None)) == 30


def test_hold_debits_and_settle_refunds_overhold():
    svc, wallet = _service(100)
    svc.hold("org", 30)
    assert wallet.balance("org") == 70
    # Actual cost came in under the hold → tenant gets the difference back.
    svc.settle("org", held=30, actual=18)
    assert wallet.balance("org") == 82


def test_failed_job_is_fully_refunded():
    svc, wallet = _service(100)
    svc.hold("org", 40)
    svc.refund("org", 40)
    assert wallet.balance("org") == 100


def test_hold_beyond_balance_is_rejected():
    svc, _ = _service(5)
    with pytest.raises(InsufficientCreditsError):
        svc.hold("org", 30)
