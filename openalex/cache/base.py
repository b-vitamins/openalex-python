"""Base cache interface and implementations."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar
from urllib.parse import urlencode

import xxhash
from structlog import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

__all__ = [
    "BaseCache",
    "CacheEntry",
    "CacheKeyBuilder",
]


class CacheKeyBuilder:
    """Build cache keys from request parameters."""

    @staticmethod
    def build_key(
        endpoint: str,
        entity_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Build a cache key from request parameters."""
        parts = [endpoint]

        if entity_id:
            parts.append(entity_id)

        if params:
            sorted_params = sorted(params.items())
            param_str = urlencode(sorted_params)
            parts.append(xxhash.xxh64(param_str).hexdigest())

        return ":".join(parts)


@dataclass(slots=True)
class CacheEntry:
    """A cache entry with metadata."""

    data: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)
    hit_count: int = 0

    @classmethod
    def create(cls, data: Any, ttl: float) -> CacheEntry:
        now = time.time()
        return cls(data=data, expires_at=now + ttl, created_at=now)

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
    def set(self, key: str, value: Any, ttl: float) -> None:
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
