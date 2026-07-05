"""Credits engine — pricing + hold/settle lifecycle.

Cost is derived from the modality's base price and the chosen provider's
`cost_weight`, so GPU-heavy models cost more without any per-provider branching
in the business logic.
"""
from __future__ import annotations

import math

from ..domain.models import Modality
from ..providers.base import ProviderAdapter
from ..repositories.base import WalletRepository

# Base credit price per modality (before the provider cost multiplier).
BASE_PRICE: dict[Modality, int] = {
    Modality.LYRICS: 1,
    Modality.MUSIC: 10,
    Modality.VOICE: 6,
    Modality.VIDEO: 40,
}


class CreditsService:
    def __init__(self, wallet: WalletRepository):
        self._wallet = wallet

    def quote(self, modality: Modality, adapter: ProviderAdapter) -> int:
        """Estimated credit cost for a request. Rounded up — never undercharge."""
        base = BASE_PRICE[modality]
        return math.ceil(base * adapter.cost_weight)

    def hold(self, org_id: str, amount: int) -> None:
        """Reserve credits before dispatching to a GPU worker."""
        self._wallet.hold(org_id, amount)

    def settle(self, org_id: str, held: int, actual: int) -> None:
        """Finalize a succeeded job, refunding any over-hold."""
        self._wallet.settle(org_id, held, actual)

    def refund(self, org_id: str, amount: int) -> None:
        """Return the full hold when a job fails — clients never pay for errors."""
        self._wallet.refund(org_id, amount)
