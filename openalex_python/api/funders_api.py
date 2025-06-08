"""Client for funder endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class FundersApi(BaseApi):
    """Access funder endpoints."""

    def funders_get(self, **params: Any) -> Any:
        """Return a list of funders."""
        return self._get("/funders", **params)

    def funders_id_get(self, id: str, **params: Any) -> Any:
        """Return a single funder."""
        return self._get(f"/funders/{id}", **params)

    def funders_random_get(self, **params: Any) -> Any:
        """Return a random funder."""
        return self._get("/funders/random", **params)


__all__ = ["FundersApi"]
