"""Client for text analysis endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openalex_python.api_client import ApiClient


def _prep(params: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in params.items() if v is not None]


class TextApi:
    """Access text analysis endpoints."""

    def __init__(self, api_client: ApiClient | None = None) -> None:
        self.api_client = api_client or ApiClient()

    def _get(self, path: str, **params: Any) -> Any:
        return self.api_client.call_api(
            path, "GET", query_params=_prep(params), _return_http_data_only=True
        )

    def _post(self, path: str, body: Any, **params: Any) -> Any:
        return self.api_client.call_api(
            path,
            "POST",
            body=body,
            query_params=_prep(params),
            _return_http_data_only=True,
        )

    def text_concepts_get(self, title: str, **params: Any) -> Any:
        """Extract concepts from text title."""
        return self._get("/text/concepts", title=title, **params)

    def text_get(self, title: str, **params: Any) -> Any:
        """Analyze text by title."""
        return self._get("/text", title=title, **params)

    def text_keywords_get(self, title: str, **params: Any) -> Any:
        """Extract keywords from title."""
        return self._get("/text/keywords", title=title, **params)

    def text_post(self, body: Any, **params: Any) -> Any:
        """Analyze text payload via POST."""
        return self._post("/text", body, **params)

    def text_topics_get(self, title: str, **params: Any) -> Any:
        """Extract topics from title."""
        return self._get("/text/topics", title=title, **params)


__all__ = ["TextApi"]
