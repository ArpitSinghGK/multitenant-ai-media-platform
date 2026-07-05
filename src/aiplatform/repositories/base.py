"""Repository interfaces + an in-memory implementation.

The interfaces are what services depend on. The in-memory backends let the whole
platform run and be tested without Postgres; a SQLAlchemy implementation drops in
behind the same Protocols for production.
"""
from __future__ import annotations

from typing import Protocol

from ..core.errors import InsufficientCreditsError, NotFoundError
from ..domain.models import Job


class WalletRepository(Protocol):
    def balance(self, org_id: str) -> int: ...
    def hold(self, org_id: str, amount: int) -> None: ...
    def settle(self, org_id: str, hold_amount: int, actual_amount: int) -> None: ...
    def refund(self, org_id: str, amount: int) -> None: ...


class JobRepository(Protocol):
    def create(self, job: Job) -> Job: ...
    def get(self, job_id: str) -> Job: ...
    def update(self, job: Job) -> Job: ...


class InMemoryWalletRepository:
    """Credits ledger kept in a dict. Holds are debited immediately and either
    settled (partial refund of the difference) or fully refunded on failure."""

    def __init__(self, seed: dict[str, int] | None = None):
        self._balances: dict[str, int] = dict(seed or {})

    def balance(self, org_id: str) -> int:
        return self._balances.get(org_id, 0)

    def hold(self, org_id: str, amount: int) -> None:
        current = self._balances.get(org_id, 0)
        if amount > current:
            raise InsufficientCreditsError(
                f"need {amount} credits, wallet has {current}"
            )
        self._balances[org_id] = current - amount

    def settle(self, org_id: str, hold_amount: int, actual_amount: int) -> None:
        # Return any over-held credits to the tenant.
        refund = max(hold_amount - actual_amount, 0)
        if refund:
            self._balances[org_id] = self._balances.get(org_id, 0) + refund

    def refund(self, org_id: str, amount: int) -> None:
        self._balances[org_id] = self._balances.get(org_id, 0) + amount


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        return job

    def update(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job
