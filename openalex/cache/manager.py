"""Cache manager for coordinating caching strategies."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, TypeVar, cast

from structlog import get_logger

__all__ = ["CacheManager", "clear_cache", "get_cache_manager"]

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from ..config import OpenAlexConfig
from .base import BaseCache, CacheKeyBuilder
from .memory import SmartMemoryCache

logger = get_logger(__name__)

T = TypeVar("T")


class CacheManager:
    """Manages caching for OpenAlex API requests."""

    def __init__(self, config: OpenAlexConfig) -> None:
        self.config = config
        self._cache: BaseCache | None = None
        self._locks: dict[str, threading.Lock] = {}

        if config.cache_enabled:
            self._cache = SmartMemoryCache(
                maxsize=config.cache_maxsize,
                ttl=config.cache_ttl,
            )

    @property
    def enabled(self) -> bool:
        return self._cache is not None

    @property
    def cache(self) -> BaseCache | None:
        """Expose the underlying cache object, if enabled."""
        return self._cache

    def get_ttl_for_endpoint(self, endpoint: str) -> float:
        """Public wrapper for ``_get_ttl_for_endpoint``."""
        return self._get_ttl_for_endpoint(endpoint)

    def get_or_fetch(
        self,
        endpoint: str,
        fetch_func: Callable[[], T],
        entity_id: str | None = None,
        params: dict[str, Any] | None = None,
        ttl: float | None = None,
    ) -> T:
        if not self.enabled:
            return fetch_func()

        assert self._cache is not None

        cache_key = CacheKeyBuilder.build_key(endpoint, entity_id, params)

        lock = self._locks.setdefault(cache_key, threading.Lock())
        with lock:
            cached_data = self._cache.get(cache_key)
            if cached_data is not None:
                logger.debug(
                    "cache_hit",
                    endpoint=endpoint,
                    entity_id=entity_id,
                    from_cache=True,
                )
                return cast("T", cached_data)

            logger.debug(
                "cache_miss",
                endpoint=endpoint,
                entity_id=entity_id,
                from_cache=False,
            )

            data = fetch_func()
            cache_ttl = ttl or self._get_ttl_for_endpoint(endpoint)
            self._cache.set(cache_key, data, cache_ttl)
            return data

    def invalidate(
        self,
        endpoint: str,
        entity_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return

        assert self._cache is not None
        cache_key = CacheKeyBuilder.build_key(endpoint, entity_id, params)
        self._cache.delete(cache_key)

    def clear(self) -> None:
        if self.enabled:
            assert self._cache is not None
            self._cache.clear()

    def stats(self) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False}

        assert self._cache is not None
        return {
            "enabled": True,
            **self._cache.stats(),
        }

    def _get_ttl_for_endpoint(self, _endpoint: str) -> float:
        return float(self.config.cache_ttl)


_cache_managers: dict[int, CacheManager] = {}


def get_cache_manager(config: OpenAlexConfig) -> CacheManager:
    """Return a shared :class:`CacheManager` for ``config``."""
    key = id(config)
    manager = _cache_managers.get(key)
    if manager is None:
        manager = CacheManager(config)
        _cache_managers[key] = manager
    return manager


def clear_cache() -> None:
    """Clear all managed caches."""
    for manager in _cache_managers.values():
        manager.clear()
