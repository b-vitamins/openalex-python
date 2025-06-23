"""Base classes and utilities for test isolation."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

from openalex.cache.manager import CacheManager, clear_cache, _cache_managers
from openalex.cache.memory import MemoryCache
from openalex.config import OpenAlexConfig


class IsolatedTestCase:
    """Base class for tests that need complete isolation from global state."""

    def setup_method(self) -> None:
        self._store_original_functions()
        self._clear_all_global_state()

    def teardown_method(self) -> None:
        self._restore_original_functions()
        self._clear_all_global_state()

    def _clear_all_global_state(self) -> None:
        """Clear caches and connection pools."""
        from openalex.api import _connection_pool
        from openalex.metrics.utils import _metrics_collectors

        clear_cache()
        _cache_managers.clear()
        _connection_pool.clear()
        _metrics_collectors.clear()

    def _store_original_functions(self) -> None:
        import openalex.cache.manager
        import openalex.templates

        self._originals = {
            "cache_get_cache_manager": openalex.cache.manager.get_cache_manager,
            "templates_get_cache_manager": openalex.templates.get_cache_manager,
        }

    def _restore_original_functions(self) -> None:
        import openalex.cache.manager
        import openalex.templates

        openalex.cache.manager.get_cache_manager = self._originals[
            "cache_get_cache_manager"
        ]
        openalex.templates.get_cache_manager = self._originals[
            "templates_get_cache_manager"
        ]


class CachePatchingTestCase:
    """Base class for tests that need to patch cache behavior."""

    @contextmanager
    def patch_cache_manager(
        self,
        cache: MemoryCache | None = None,
        cache_enabled: bool = True,
    ) -> Generator[CacheManager, None, None]:
        import openalex.cache.manager
        import openalex.templates

        original_cache_get = openalex.cache.manager.get_cache_manager
        original_templates_get = openalex.templates.get_cache_manager

        config = OpenAlexConfig(cache_enabled=cache_enabled)
        manager = CacheManager(config)
        if cache and cache_enabled:
            manager._cache = cache

        try:
            openalex.cache.manager.get_cache_manager = lambda cfg: manager
            openalex.templates.get_cache_manager = lambda cfg: manager
            yield manager
        finally:
            openalex.cache.manager.get_cache_manager = original_cache_get
            openalex.templates.get_cache_manager = original_templates_get

    @contextmanager
    def isolated_cache(self) -> Generator[MemoryCache, None, None]:
        cache = MemoryCache(max_size=100)
        yield cache


__all__ = ["CachePatchingTestCase", "IsolatedTestCase"]
