"""Client for keyword endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class KeywordsApi(BaseApi):
    """Access keyword endpoints."""

    def keywords_get(self, **params: Any) -> Any:
        """Return a list of keywords."""
        return self._get("/keywords", **params)

    def keywords_id_get(self, id: str, **params: Any) -> Any:
        """Return a single keyword."""
        return self._get(f"/keywords/{id}", **params)

    def keywords_random_get(self, **params: Any) -> Any:
        """Return a random keyword."""
        return self._get("/keywords/random", **params)


__all__ = ["KeywordsApi"]
