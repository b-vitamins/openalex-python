"""Client for the OpenAlex authors endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class AuthorsApi:
    """Access authors-related API endpoints."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def authors_get(self, **params: Any) -> Any:
        """Return a list of authors."""
        return self.api_client.call_api(
            "/authors", "GET", query_params=_prep(params), _return_http_data_only=True
        )

    def authors_id_get(self, id: str, **params: Any) -> Any:
        """Return a single author."""
        return self.api_client.call_api(
            f"/authors/{id}",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def authors_random_get(self, **params: Any) -> Any:
        """Return a random author."""
        return self.api_client.call_api(
            "/authors/random",
            "GET",
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def people_get(self, **params: Any) -> Any:
        """Alias for :meth:`authors_get`."""
        return self.authors_get(**params)

    def people_id_get(self, id: str, **params: Any) -> Any:
        """Alias for :meth:`authors_id_get`."""
        return self.authors_id_get(id, **params)


__all__ = ["AuthorsApi"]
