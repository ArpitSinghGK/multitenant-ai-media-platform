"""Redis accessor — shared by Celery, rate limiting and concurrency counters."""
from __future__ import annotations

import redis

from ..config import Settings

_pool: redis.ConnectionPool | None = None


def get_redis(settings: Settings) -> redis.Redis:
    """Return a Redis client backed by a shared connection pool."""
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(settings.redis_url)
    return redis.Redis(connection_pool=_pool)
