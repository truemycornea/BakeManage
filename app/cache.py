from __future__ import annotations

import json
from typing import Any

import redis

from .config import settings


def get_redis_client() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def cache_set(client: redis.Redis, key: str, value: Any, ttl_seconds: int = 60) -> None:
    client.set(key, json.dumps(value), ex=ttl_seconds)


def cache_get(client: redis.Redis, key: str) -> Any | None:
    raw = client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
