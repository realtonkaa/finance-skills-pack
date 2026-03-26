"""File-based JSON cache with TTL support."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path.home() / ".finance-skills" / "cache"


def _ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{_cache_key(key)}.json"


def get_cached(key: str, ttl_hours: float = 24.0) -> Optional[Any]:
    """Retrieve cached data if it exists and hasn't expired."""
    path = _cache_path(key)
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            entry = json.load(f)

        age_hours = (time.time() - entry["timestamp"]) / 3600
        if age_hours > ttl_hours:
            return None

        return entry["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def get_stale(key: str) -> Optional[Any]:
    """Retrieve cached data even if expired. Used as fallback."""
    path = _cache_path(key)
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            entry = json.load(f)
        return entry["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def set_cached(key: str, data: Any, ttl_hours: float = 24.0):
    """Store data in cache."""
    _ensure_cache_dir()
    path = _cache_path(key)

    entry = {
        "key": key,
        "timestamp": time.time(),
        "ttl_hours": ttl_hours,
        "data": data,
    }

    with open(path, "w") as f:
        json.dump(entry, f, default=str)


def clear_cache():
    """Remove all cached files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
