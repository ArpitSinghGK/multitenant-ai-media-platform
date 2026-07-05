"""Wallet API — credit balance for the calling organization."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ...domain.models import TenantContext
from ...repositories.base import WalletRepository
from ..deps import _wallet_repo, get_tenant

router = APIRouter(prefix="/v1", tags=["wallet"])


def get_wallet_repo() -> WalletRepository:
    return _wallet_repo()


@router.get("/wallet")
def get_balance(
    ctx: TenantContext = Depends(get_tenant),
    wallet: WalletRepository = Depends(get_wallet_repo),
) -> dict:
    return {"org_id": ctx.org_id, "credits": wallet.balance(ctx.org_id)}
