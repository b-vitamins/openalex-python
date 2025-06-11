"""Cache manager for coordinating caching strategies."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

from structlog import get_logger

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

        if config.cache_enabled:
            self._cache = SmartMemoryCache(
                maxsize=config.cache_maxsize,
                ttl=config.cache_ttl,
            )

    @property
    def enabled(self) -> bool:
        return self._cache is not None

    def get_or_fetch(
        self,
        endpoint: str,
        fetch_func: Callable[[], T],
        entity_id: str | None = None,
        params: dict[str, Any] | None = None,
        ttl: int | None = None,
    ) -> T:
        if not self.enabled:
            return fetch_func()

        assert self._cache is not None

        cache_key = CacheKeyBuilder.build_key(endpoint, entity_id, params)

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

    def _get_ttl_for_endpoint(self, endpoint: str) -> int:
        ttl_map = {
            "works": 3600,
            "authors": 7200,
            "institutions": 14400,
            "sources": 86400,
            "topics": 86400,
            "publishers": 86400,
            "funders": 86400,
            "concepts": 86400,
        }

        base_endpoint = endpoint.split("/")[0]
        return ttl_map.get(base_endpoint, self.config.cache_ttl)


_cache_manager: CacheManager | None = None


def get_cache_manager(config: OpenAlexConfig) -> CacheManager:
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(config)

    return _cache_manager


def clear_cache() -> None:
    if _cache_manager is not None:
        _cache_manager.clear()

