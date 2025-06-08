"""Client for work endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class WorksApi:
    """Access work endpoints."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def works_get(self, **params: Any) -> Any:
        """Return a list of works."""
        return self.api_client.call_api(
            "/works", "GET", query_params=_prep(params), _return_http_data_only=True
        )

    def works_id_get(self, id: str, **params: Any) -> Any:
        """Return a single work."""
        return self.api_client.call_api(
            f"/works/{id}",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def works_random_get(self, **params: Any) -> Any:
        """Return a random work."""
        return self.api_client.call_api(
            "/works/random",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )


__all__ = ["WorksApi"]
