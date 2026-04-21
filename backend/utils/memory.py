"""
Simple memory store — persists decisions to data/memory.json.
Keeps the last MAX_ENTRIES records in RAM and on disk.
"""

import os
import json
import time
from threading import Lock
from utils.logger import get_logger

logger     = get_logger("memory")
_LOCK      = Lock()
MAX_ENTRIES = int(os.getenv("MAX_MEMORY_ENTRIES", "200"))
DATA_DIR    = os.getenv("DATA_DIR", "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")


def _load() -> list:
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(entries: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# In-memory cache (loaded once at import time)
_store: list = _load()


def add_entry(query: str, result: dict, request_id: str = "?") -> None:
    global _store
    entry = {
        "id":          request_id,
        "timestamp":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query":       query,
        "decision":    result.get("decision", "")[:200],
        "confidence":  result.get("confidence", ""),
        "iterations":  result.get("_meta", {}).get("iterations", 1),
        "pipeline_ms": result.get("_meta", {}).get("pipeline_ms", 0),
    }
    with _LOCK:
        _store.append(entry)
        if len(_store) > MAX_ENTRIES:
            _store = _store[-MAX_ENTRIES:]
        _save(_store)
    logger.debug("[%s] Memory stored (total=%d)", request_id, len(_store))


def get_all() -> list:
    with _LOCK:
        return list(reversed(_store))


def clear_all() -> None:
    global _store
    with _LOCK:
        _store = []
        _save(_store)
    logger.info("Memory store cleared")


def count() -> int:
    return len(_store)
