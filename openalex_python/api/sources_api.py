"""Client for source endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class SourcesApi(BaseApi):
    """Access source endpoints."""

    def sources_get(self, **params: Any) -> Any:
        """Return a list of sources."""
        return self._get("/sources", **params)

    def sources_id_get(self, id: str, **params: Any) -> Any:
        """Return a single source."""
        return self._get(f"/sources/{id}", **params)

    def sources_random_get(self, **params: Any) -> Any:
        """Return a random source."""
        return self._get("/sources/random", **params)


__all__ = ["SourcesApi"]
