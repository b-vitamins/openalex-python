"""Client for publisher endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class PublishersApi(BaseApi):
    """Access publisher endpoints."""

    def publishers_get(self, **params: Any) -> Any:
        """Return a list of publishers."""
        return self._get("/publishers", **params)

    def publishers_id_get(self, id: str, **params: Any) -> Any:
        """Return a single publisher."""
        return self._get(f"/publishers/{id}", **params)

    def publishers_random_get(self, **params: Any) -> Any:
        """Return a random publisher."""
        return self._get("/publishers/random", **params)


__all__ = ["PublishersApi"]
