"""Client for text analysis endpoints."""

from __future__ import annotations

from typing import Any

from .base import BaseApi


class TextApi(BaseApi):
    """Access text analysis endpoints."""

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
