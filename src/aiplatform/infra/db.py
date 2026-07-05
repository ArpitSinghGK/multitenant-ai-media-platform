"""Postgres engine/session factory (Control Plane state of record).

SQLAlchemy 2.x style. Repositories depend on a Session, not on this module's
globals, so they stay unit-testable with in-memory fakes.
"""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import Settings

_engine = None
_SessionLocal: sessionmaker | None = None


def init_engine(settings: Settings) -> None:
    """Create the process-wide engine + session factory once at startup."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def session_scope() -> Iterator[Session]:
    """FastAPI dependency: yield a session and guarantee close."""
    if _SessionLocal is None:
        raise RuntimeError("db.init_engine() was not called at startup")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
