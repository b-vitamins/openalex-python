"""Client for the OpenAlex authors endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class AuthorsApi(BaseApi):
    """Access authors-related API endpoints."""

    def authors_get(self, **params: Any) -> Any:
        """Return a list of authors."""
        return self._get("/authors", **params)

    def authors_id_get(self, id: str, **params: Any) -> Any:
        """Return a single author."""
        return self._get(f"/authors/{id}", **params)

    def authors_random_get(self, **params: Any) -> Any:
        """Return a random author."""
        return self._get("/authors/random", **params)

    def people_get(self, **params: Any) -> Any:
        """Alias for :meth:`authors_get`."""
        return self.authors_get(**params)

    def people_id_get(self, id: str, **params: Any) -> Any:
        """Alias for :meth:`authors_id_get`."""
        return self.authors_id_get(id, **params)


__all__ = ["AuthorsApi"]
