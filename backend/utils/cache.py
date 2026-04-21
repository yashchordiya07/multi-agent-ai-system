"""
SHA-256 keyed in-memory cache for repeated queries.
TTL defaults to 5 minutes; evicts oldest entry when full.
"""

import hashlib
import time
from threading import Lock
from utils.logger import get_logger

logger   = get_logger("cache")
_LOCK    = Lock()
_STORE: dict[str, dict] = {}
TTL      = 300   # seconds
MAX_SIZE = 100


def _key(query: str) -> str:
    normalized = " ".join(query.strip().lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:20]


def get(query: str) -> dict | None:
    k = _key(query)
    with _LOCK:
        entry = _STORE.get(k)
        if entry is None:
            return None
        if time.time() > entry["exp"]:
            del _STORE[k]
            return None
        logger.debug("Cache hit  key=%s", k)
        return entry["data"]


def set(query: str, data: dict) -> None:
    k = _key(query)
    with _LOCK:
        if len(_STORE) >= MAX_SIZE:
            oldest = min(_STORE, key=lambda x: _STORE[x]["ts"])
            del _STORE[oldest]
        _STORE[k] = {"data": data, "ts": time.time(), "exp": time.time() + TTL}
    logger.debug("Cache set  key=%s", k)


def stats() -> dict:
    now = time.time()
    with _LOCK:
        active  = sum(1 for v in _STORE.values() if v["exp"] > now)
        expired = len(_STORE) - active
    return {"active": active, "expired": expired, "max_size": MAX_SIZE, "ttl_seconds": TTL}


def clear() -> None:
    with _LOCK:
        _STORE.clear()
