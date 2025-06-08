"""Client for work endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class WorksApi(BaseApi):
    """Access work endpoints."""

    def works_get(self, **params: Any) -> Any:
        """Return a list of works."""
        return self._get("/works", **params)

    def works_id_get(self, id: str, **params: Any) -> Any:
        """Return a single work."""
        return self._get(f"/works/{id}", **params)

    def works_random_get(self, **params: Any) -> Any:
        """Return a random work."""
        return self._get("/works/random", **params)


__all__ = ["WorksApi"]
