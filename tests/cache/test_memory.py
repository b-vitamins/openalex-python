"""Tests for memory cache implementations."""

import time
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from openalex.cache.memory import MemoryCache, SmartMemoryCache


class TestMemoryCache:
    """Test MemoryCache implementation."""

    def test_basic_operations(self):
        """Test basic cache operations."""
        cache = MemoryCache(max_size=10)

        # Test set and get
        cache.set("key1", "value1", ttl=1.0)
        assert cache.get("key1") == "value1"

        # Test missing key
        assert cache.get("missing") is None

        # Test delete
        cache.delete("key1")
        assert cache.get("key1") is None

        # Test clear
        cache.set("key2", "value2", ttl=1.0)
        cache.set("key3", "value3", ttl=1.0)
        cache.clear()
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = MemoryCache()

        # Set with short TTL
        cache.set("expires", "value", ttl=0.1)
        assert cache.get("expires") == "value"

        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("expires") is None

    def test_max_size_eviction(self):
        """Test eviction when max size is reached."""
        cache = MemoryCache(max_size=3)

        # Fill cache
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        cache.set("key3", "value3", ttl=60)

        # Add one more - should evict oldest
        cache.set("key4", "value4", ttl=60)

        # key1 should be evicted (oldest)
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_statistics(self):
        """Test cache statistics."""
        cache = MemoryCache()

        # Initial stats
        stats = cache.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0

        # Add some data
        cache.set("key1", "value1", ttl=60)
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("missing")  # miss

        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2 / 3
        assert stats["size"] == 1

    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        # use a size large enough to avoid eviction during the test
        cache = MemoryCache(max_size=1000)
        errors = []

        def worker(thread_id: int) -> None:
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    cache.set(key, f"value_{i}", ttl=60)
                    value = cache.get(key)
                    assert value == f"value_{i}"
            except Exception as e:  # pragma: no cover - unexpected
                errors.append(e)

        # Run multiple threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for future in futures:
                future.result()

        assert len(errors) == 0
        assert cache.stats()["size"] <= 1000  # Max size respected


class TestSmartMemoryCache:
    """Test SmartMemoryCache implementation."""

    def test_adaptive_ttl(self):
        """Test adaptive TTL extension."""
        cache = SmartMemoryCache(base_ttl=1.0, ttl_multiplier=2.0, max_ttl=10.0)

        # Set initial value
        cache.set("popular", "value")

        # Access multiple times to trigger TTL extension
        for _ in range(5):
            assert cache.get("popular") == "value"

        # Check that item hasn't expired after base TTL
        time.sleep(1.5)
        assert cache.get("popular") == "value"

        # Check extended stats
        stats = cache.stats()
        assert stats["adaptive_keys"] == 1
        assert stats["avg_ttl"] > 1.0

    def test_max_ttl_limit(self):
        """Test that TTL doesn't exceed max_ttl."""
        cache = SmartMemoryCache(base_ttl=1.0, ttl_multiplier=10.0, max_ttl=5.0)

        cache.set("key", "value")

        # Access many times
        for _ in range(20):
            cache.get("key")

        # TTL should be capped at max_ttl
        assert cache._key_ttls["key"] <= 5.0

    def test_inheritance_from_memory_cache(self):
        """Test that SmartMemoryCache inherits MemoryCache functionality."""
        cache = SmartMemoryCache()

        # Test basic operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.delete("key1")
        assert cache.get("key1") is None

        # Test clear
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key2") is None
        assert len(cache._key_ttls) == 0
