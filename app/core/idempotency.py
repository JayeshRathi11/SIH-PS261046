import time
from typing import Any, Optional
from fastapi import Header


class IdempotencyConflictError(Exception):
    def __init__(self, idempotency_key: str):
        self.idempotency_key = idempotency_key


_IDEMPOTENCY_CACHE: dict[str, dict[str, Any]] = {}
DEFAULT_IDEMPOTENCY_TTL_SECONDS = 60


def clear_idempotency_cache() -> None:
    global _IDEMPOTENCY_CACHE
    _IDEMPOTENCY_CACHE.clear()


def get_idempotency_record(key: str, ttl: int = DEFAULT_IDEMPOTENCY_TTL_SECONDS) -> Optional[dict[str, Any]]:
    now = time.time()
    record = _IDEMPOTENCY_CACHE.get(key)
    if record is None:
        return None
    if (now - record["timestamp"]) > ttl:
        _IDEMPOTENCY_CACHE.pop(key, None)
        return None
    return record


def store_idempotency_record(key: str, response_data: Any) -> None:
    _IDEMPOTENCY_CACHE[key] = {
        "timestamp": time.time(),
        "response_data": response_data,
    }


def check_idempotency(
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
) -> Optional[str]:
    if not x_idempotency_key or not x_idempotency_key.strip():
        return None
    key = x_idempotency_key.strip()
    existing = get_idempotency_record(key)
    if existing is not None:
        raise IdempotencyConflictError(key)
    return key
