"""Client for topic endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class TopicsApi(BaseApi):
    """Access topic endpoints."""

    def topics_get(self, **params: Any) -> Any:
        """Return a list of topics."""
        return self._get("/topics", **params)

    def topics_id_get(self, id: str, **params: Any) -> Any:
        """Return a single topic."""
        return self._get(f"/topics/{id}", **params)

    def topics_random_get(self, **params: Any) -> Any:
        """Return a random topic."""
        return self._get("/topics/random", **params)


__all__ = ["TopicsApi"]
