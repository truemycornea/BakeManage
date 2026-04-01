# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
from __future__ import annotations

import json
import time
from typing import Any, Optional

import redis

from .config import settings


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def set(self, key: str, value: Any, ex: int | None = None) -> None:
        ttl = ex or settings.cache_ttl_seconds
        self._store[key] = (value, time.time() + ttl)

    def get(self, key: str) -> Any | None:
        value = self._store.get(key)
        if not value:
            return None
        payload, expiry = value
        if expiry < time.time():
            self._store.pop(key, None)
            return None
        return payload

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


def get_cache_client() -> redis.Redis | InMemoryCache:
    try:
        client: redis.Redis = redis.Redis.from_url(settings.celery_broker_url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return InMemoryCache()


def cache_inventory_snapshot(key: str, snapshot: dict[str, Any], ttl: Optional[int] = None) -> None:
    client = get_cache_client()
    serialized = json.dumps(snapshot)
    if hasattr(client, "set"):
        client.set(key, serialized, ex=ttl or settings.cache_ttl_seconds)  # type: ignore[arg-type]


def read_cached_snapshot(key: str) -> dict[str, Any] | None:
    client = get_cache_client()
    raw: Any | None = None
    if hasattr(client, "get"):
        raw = client.get(key)  # type: ignore[arg-type]
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


def clear_namespace(prefix: str) -> None:
    client = get_cache_client()
    if isinstance(client, InMemoryCache):
        keys = [k for k in list(client._store.keys()) if k.startswith(prefix)]  # type: ignore[attr-defined]
        for key in keys:
            client.delete(key)
        return
    try:
        pattern = f"{prefix}*"
        for key in client.scan_iter(match=pattern):  # type: ignore[call-arg]
            client.delete(key)
    except Exception:
        return
