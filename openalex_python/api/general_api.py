"""Miscellaneous general endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class GeneralApi:
    """Access root endpoint."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def root_get(self, **params: Any) -> Any:
        """Return the API root description."""
        return self.api_client.call_api(
            "/", "GET", query_params=_prep(params), _return_http_data_only=True
        )


__all__ = ["GeneralApi"]
