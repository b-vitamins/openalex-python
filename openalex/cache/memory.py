"""In-memory cache implementation."""

from __future__ import annotations

import threading
import time
from typing import Any

from structlog import get_logger

__all__ = [
    "MemoryCache",
    "SmartMemoryCache",
]

from .base import BaseCache, CacheEntry

logger = get_logger(__name__)


class MemoryCache(BaseCache):
    """Thread-safe in-memory cache implementation."""

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize memory cache with maximum size limit."""
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                logger.debug("cache_miss", key=key)
                return None
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                logger.debug("cache_expired", key=key)
                return None
            entry.increment_hits()
            self._hits += 1
            logger.debug("cache_hit", key=key, hits=entry.hit_count)
            return entry.data

    def set(self, key: str, value: Any, ttl: float) -> None:
        """Set a value in the cache with TTL in seconds."""
        with self._lock:
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            self._cache[key] = CacheEntry.create(value, ttl)
            logger.debug("cache_set", key=key, ttl=ttl)

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("cache_delete", key=key)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            logger.info("cache_cleared")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
            }

    def _evict_oldest(self) -> None:
        """Evict the oldest entry when cache is full."""
        if not self._cache:
            return
        oldest_key = min(
            self._cache.keys(), key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        self._evictions += 1
        logger.debug("cache_evicted", key=oldest_key)


class SmartMemoryCache(MemoryCache):
    """Memory cache with adaptive TTL based on hit patterns."""

    def __init__(
        self,
        max_size: int = 1000,
        base_ttl: float = 300.0,
        ttl_multiplier: float = 1.5,
        max_ttl: float = 3600.0,
    ) -> None:
        """Initialize smart cache with adaptive TTL."""
        super().__init__(max_size)
        self._base_ttl = base_ttl
        self._ttl_multiplier = ttl_multiplier
        self._max_ttl = max_ttl
        self._key_ttls: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        """Get value and potentially extend TTL based on access patterns."""
        result = super().get(key)
        if result is not None:
            # Extend TTL for frequently accessed items
            with self._lock:
                entry = self._cache.get(key)
                if entry and entry.hit_count > 2:
                    current_ttl = self._key_ttls.get(key, self._base_ttl)
                    new_ttl = min(
                        current_ttl * self._ttl_multiplier, self._max_ttl
                    )
                    self._key_ttls[key] = new_ttl
                    entry.expires_at = time.time() + new_ttl
                    logger.debug("cache_ttl_extended", key=key, new_ttl=new_ttl)
        return result

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value with adaptive TTL."""
        if ttl is None:
            ttl = self._key_ttls.get(key, self._base_ttl)
        super().set(key, value, ttl)
        self._key_ttls[key] = ttl

    def clear(self) -> None:
        """Clear cache and TTL history."""
        super().clear()
        self._key_ttls.clear()

    def stats(self) -> dict[str, Any]:
        """Get extended statistics including TTL info."""
        stats = super().stats()
        with self._lock:
            avg_ttl = (
                sum(self._key_ttls.values()) / len(self._key_ttls)
                if self._key_ttls
                else self._base_ttl
            )
            stats.update(
                {
                    "avg_ttl": avg_ttl,
                    "adaptive_keys": len(self._key_ttls),
                }
            )
        return stats
