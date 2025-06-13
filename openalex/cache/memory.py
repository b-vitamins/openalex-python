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

    __slots__ = ("_cache", "_default_ttl", "_lock", "_maxsize", "_stats")

    def __init__(self, maxsize: int = 1000, ttl: int = 3600) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._maxsize = maxsize
        self._default_ttl = ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
        }

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats["misses"] += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                self._stats["evictions"] += 1
                return None

            entry.increment_hits()
            self._stats["hits"] += 1

            logger.debug(
                "cache_hit",
                key=key,
                hit_count=entry.hit_count,
                age_seconds=int(time.time() - entry.created_at),
            )

            return entry.data

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if ttl is None:
            ttl = self._default_ttl

        with self._lock:
            if len(self._cache) >= self._maxsize and key not in self._cache:
                self._evict_oldest()

            self._cache[key] = CacheEntry.create(value, ttl)
            self._stats["sets"] += 1

            logger.debug(
                "cache_set",
                key=key,
                ttl=ttl,
                cache_size=len(self._cache),
            )

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1

    def clear(self) -> None:
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info("cache_cleared", entries_removed=count)

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests if total_requests > 0 else 0
            )

            return {
                **self._stats,
                "size": len(self._cache),
                "maxsize": self._maxsize,
                "hit_rate": hit_rate,
            }

    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )
        del self._cache[oldest_key]
        self._stats["evictions"] += 1


class SmartMemoryCache(MemoryCache):
    """Memory cache with smart eviction based on usage patterns."""

    __slots__ = ()

    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        current_time = time.time()
        age_weight = 1.0
        hit_weight = 10.0

        def eviction_score(key: str) -> float:
            entry = self._cache[key]
            age = current_time - entry.created_at
            return age_weight * age - hit_weight * entry.hit_count

        evict_key = max(self._cache.keys(), key=eviction_score)

        logger.debug(
            "smart_eviction",
            key=evict_key,
            hit_count=self._cache[evict_key].hit_count,
            age=int(current_time - self._cache[evict_key].created_at),
        )

        del self._cache[evict_key]
        self._stats["evictions"] += 1
