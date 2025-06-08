"""Client for topic endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class TopicsApi:
    """Access topic endpoints."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def topics_get(self, **params: Any) -> Any:
        """Return a list of topics."""
        return self.api_client.call_api(
            "/topics", "GET", query_params=_prep(params), _return_http_data_only=True
        )

    def topics_id_get(self, id: str, **params: Any) -> Any:
        """Return a single topic."""
        return self.api_client.call_api(
            f"/topics/{id}",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def topics_random_get(self, **params: Any) -> Any:
        """Return a random topic."""
        return self.api_client.call_api(
            "/topics/random",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )


__all__ = ["TopicsApi"]
