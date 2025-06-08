"""Client for OpenAlex concepts endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class ConceptsApi(BaseApi):
    """Access concept endpoints."""

    def concepts_get(self, **params: Any) -> Any:
        """Return a list of concepts."""
        return self._get("/concepts", **params)

    def concepts_id_get(self, id: str, **params: Any) -> Any:
        """Return a single concept."""
        return self._get(f"/concepts/{id}", **params)

    def concepts_random_get(self, **params: Any) -> Any:
        """Return a random concept."""
        return self._get("/concepts/random", **params)


__all__ = ["ConceptsApi"]
