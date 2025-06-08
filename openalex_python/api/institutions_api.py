"""Client for institution endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class InstitutionsApi(BaseApi):
    """Access institution endpoints."""

    def institutions_get(self, **params: Any) -> Any:
        """Return a list of institutions."""
        return self._get("/institutions", **params)

    def institutions_id_get(self, id: str, **params: Any) -> Any:
        """Return a single institution."""
        return self._get(f"/institutions/{id}", **params)

    def institutions_random_get(self, **params: Any) -> Any:
        """Return a random institution."""
        return self._get("/institutions/random", **params)


__all__ = ["InstitutionsApi"]
