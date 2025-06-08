from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


class BaseApi:
    """Base class for API wrappers."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    @staticmethod
    def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
        """Filter out ``None`` values from parameters."""
        return [(k, v) for k, v in params.items() if v is not None]

    def _get(self, path: str, **params: Any) -> Any:
        """Perform a GET request and return deserialized data."""
        return self.api_client.call_api(
            path,
            "GET",
            query_params=self._prep(params),
            _return_http_data_only=True,
        )

    def _post(self, path: str, body: Any, **params: Any) -> Any:
        """Perform a POST request and return deserialized data."""
        return self.api_client.call_api(
            path,
            "POST",
            body=body,
            query_params=self._prep(params),
            _return_http_data_only=True,
        )
