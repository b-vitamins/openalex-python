"""Model for topic results returned directly from a text query."""
from __future__ import annotations

from typing import Any

from .topic import Topic


class AllOfTextResultsTopicsItems(Topic):
    """Topic result with a relevance score."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        """Initialize the result item."""
        super().__init__(**kwargs)
        self.score: float | None = score
