"""Client for source endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class SourcesApi:
    """Access source endpoints."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def sources_get(self, **params: Any) -> Any:
        """Return a list of sources."""
        return self.api_client.call_api(
            "/sources", "GET", query_params=_prep(params), _return_http_data_only=True
        )

    def sources_id_get(self, id: str, **params: Any) -> Any:
        """Return a single source."""
        return self.api_client.call_api(
            f"/sources/{id}",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def sources_random_get(self, **params: Any) -> Any:
        """Return a random source."""
        return self.api_client.call_api(
            "/sources/random",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )


__all__ = ["SourcesApi"]
