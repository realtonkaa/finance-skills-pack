"""Tests for caching logic."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from lib.cache import get_cached, set_cached, get_stale, clear_cache, CACHE_DIR


@pytest.fixture(autouse=True)
def use_temp_cache(tmp_path):
    """Use a temp directory for cache during tests."""
    with patch("lib.cache.CACHE_DIR", tmp_path / "cache"):
        yield tmp_path / "cache"


class TestCache:
    def test_set_and_get(self):
        set_cached("test_key", {"price": 100.0})
        result = get_cached("test_key", ttl_hours=1.0)
        assert result == {"price": 100.0}

    def test_get_missing_key(self):
        result = get_cached("nonexistent", ttl_hours=1.0)
        assert result is None

    def test_expired_returns_none(self):
        set_cached("old_key", {"data": "old"})
        # Patch the timestamp to make it expired
        result = get_cached("old_key", ttl_hours=0.0)  # 0 hours = always expired
        assert result is None

    def test_stale_returns_expired_data(self):
        set_cached("stale_key", {"data": "stale"})
        # Even with 0 TTL, get_stale should return it
        result = get_stale("stale_key")
        assert result == {"data": "stale"}

    def test_stale_missing_returns_none(self):
        result = get_stale("nonexistent")
        assert result is None

    def test_clear_cache(self, use_temp_cache):
        set_cached("key1", "data1")
        set_cached("key2", "data2")

        clear_cache()

        assert get_cached("key1", ttl_hours=24.0) is None
        assert get_cached("key2", ttl_hours=24.0) is None

    def test_different_keys_different_data(self):
        set_cached("key_a", {"value": "a"})
        set_cached("key_b", {"value": "b"})

        assert get_cached("key_a", ttl_hours=1.0) == {"value": "a"}
        assert get_cached("key_b", ttl_hours=1.0) == {"value": "b"}

    def test_overwrite_existing_key(self):
        set_cached("overwrite", {"version": 1})
        set_cached("overwrite", {"version": 2})

        result = get_cached("overwrite", ttl_hours=1.0)
        assert result == {"version": 2}
