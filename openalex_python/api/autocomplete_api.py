"""Endpoints for the autocomplete service."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class AutocompleteApi(BaseApi):
    """Autocomplete API."""

    def autocomplete_authors_get(self, q: str, **params: Any) -> Any:
        """Autocomplete authors."""
        return self._get("/autocomplete/authors", q=q, **params)

    def autocomplete_concepts_get(self, q: str, **params: Any) -> Any:
        """Autocomplete concepts."""
        return self._get("/autocomplete/concepts", q=q, **params)

    def autocomplete_funders_get(self, q: str, **params: Any) -> Any:
        """Autocomplete funders."""
        return self._get("/autocomplete/funders", q=q, **params)

    def autocomplete_get(self, q: str, **params: Any) -> Any:
        """Autocomplete across all entities."""
        return self._get("/autocomplete", q=q, **params)

    def autocomplete_institutions_get(self, q: str, **params: Any) -> Any:
        """Autocomplete institutions."""
        return self._get("/autocomplete/institutions", q=q, **params)

    def autocomplete_publishers_get(self, q: str, **params: Any) -> Any:
        """Autocomplete publishers."""
        return self._get("/autocomplete/publishers", q=q, **params)

    def autocomplete_sources_get(self, q: str, **params: Any) -> Any:
        """Autocomplete sources."""
        return self._get("/autocomplete/sources", q=q, **params)

    def autocomplete_works_get(self, q: str, **params: Any) -> Any:
        """Autocomplete works."""
        return self._get("/autocomplete/works", q=q, **params)


__all__ = ["AutocompleteApi"]
