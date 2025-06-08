"""Endpoints for the autocomplete service."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class AutocompleteApi:
    """Autocomplete API."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def _get(self, path: str, **params: Any) -> Any:
        return self.api_client.call_api(
            path, "GET", query_params=_prep(params), _return_http_data_only=True
        )

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
