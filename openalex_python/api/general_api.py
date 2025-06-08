"""Miscellaneous general endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class GeneralApi(BaseApi):
    """Access root endpoint."""

    def root_get(self, **params: Any) -> Any:
        """Return the API root description."""
        return self._get("/", **params)


__all__ = ["GeneralApi"]
