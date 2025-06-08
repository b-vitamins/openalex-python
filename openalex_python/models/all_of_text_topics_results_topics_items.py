"""Model for topic search results with a relevance score."""
from __future__ import annotations

from typing import Any

from .topic import Topic


class AllOfTextTopicsResultsTopicsItems(Topic):
    """Topic item returned from a text search."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        """Initialize the topic item."""
        super().__init__(**kwargs)
        self.score: float | None = score
