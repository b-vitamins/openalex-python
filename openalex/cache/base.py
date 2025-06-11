"""Base cache interface and implementations."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import xxhash
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheKeyBuilder:
    """Build cache keys from request parameters."""

    @staticmethod
    def build_key(
        endpoint: str,
        entity_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Build a cache key from request parameters."""
        key_parts = [endpoint]

        if entity_id:
            key_parts.append(entity_id)

        if params:
            sorted_params = sorted(params.items())
            params_str = json.dumps(sorted_params, sort_keys=True)
            key_parts.append(params_str)

        key_str = "|".join(key_parts)
        return f"openalex:{xxhash.xxh64(key_str).hexdigest()}"


class CacheEntry:
    """A cache entry with metadata."""

    def __init__(self, data: Any, ttl: int) -> None:
        self.data = data
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
        self.hit_count = 0

    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at

    def increment_hits(self) -> None:
        """Increment hit counter."""
        self.hit_count += 1


class BaseCache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set a value in the cache with TTL in seconds."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""

