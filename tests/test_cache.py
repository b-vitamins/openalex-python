"""Test caching functionality."""

import time
from unittest.mock import Mock

from openalex.cache import CacheKeyBuilder, MemoryCache, SmartMemoryCache
from openalex.cache.manager import CacheManager
from openalex.config import OpenAlexConfig


class TestCacheKeyBuilder:
    """Test cache key building."""

    def test_simple_key(self):
        key = CacheKeyBuilder.build_key("works")
        assert key.startswith("openalex:")
        assert len(key) == 25

    def test_key_with_entity_id(self):
        key1 = CacheKeyBuilder.build_key("works", "W1234")
        key2 = CacheKeyBuilder.build_key("works", "W5678")
        assert key1 != key2

    def test_key_with_params(self):
        params1 = {"filter": "is_oa:true", "page": 1}
        params2 = {"page": 1, "filter": "is_oa:true"}

        key1 = CacheKeyBuilder.build_key("works", params=params1)
        key2 = CacheKeyBuilder.build_key("works", params=params2)

        assert key1 == key2


class TestMemoryCache:
    """Test memory cache implementation."""

    def test_basic_operations(self):
        cache = MemoryCache(maxsize=10, ttl=60)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        assert cache.get("nonexistent") is None

        cache.delete("key1")
        assert cache.get("key1") is None

    def test_ttl_expiration(self):
        cache = MemoryCache(maxsize=10, ttl=1)

        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_eviction(self):
        cache = MemoryCache(maxsize=3, ttl=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.set("key4", "value4")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key4") == "value4"

    def test_stats(self):
        cache = MemoryCache(maxsize=10, ttl=60)

        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert stats["size"] == 1


class TestSmartMemoryCache:
    """Test smart memory cache with usage-based eviction."""

    def test_smart_eviction(self):
        cache = SmartMemoryCache(maxsize=3, ttl=60)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        for _ in range(5):
            cache.get("key2")

        cache.set("key4", "value4")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestCacheManager:
    """Test cache manager."""

    def test_get_or_fetch_hit(self):
        config = OpenAlexConfig(cache_enabled=True)
        manager = CacheManager(config)

        fetch_func = Mock(return_value="fetched_data")
        result1 = manager.get_or_fetch("works", fetch_func, entity_id="W123")
        result2 = manager.get_or_fetch("works", fetch_func, entity_id="W123")

        assert result1 == "fetched_data"
        assert result2 == "fetched_data"
        assert fetch_func.call_count == 1

    def test_get_or_fetch_miss(self):
        config = OpenAlexConfig(cache_enabled=True)
        manager = CacheManager(config)

        fetch_func = Mock(return_value="fetched_data")
        result = manager.get_or_fetch("works", fetch_func, entity_id="W456")

        assert result == "fetched_data"
        assert fetch_func.call_count == 1

    def test_disabled_cache(self):
        config = OpenAlexConfig(cache_enabled=False)
        manager = CacheManager(config)

        fetch_func = Mock(return_value="fetched_data")

        manager.get_or_fetch("works", fetch_func, entity_id="W789")
        manager.get_or_fetch("works", fetch_func, entity_id="W789")

        assert fetch_func.call_count == 2
