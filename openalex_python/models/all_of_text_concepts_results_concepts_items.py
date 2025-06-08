"""Model for concept search results with a relevance score."""
from __future__ import annotations

from typing import Any

from .concept import Concept


class AllOfTextConceptsResultsConceptsItems(Concept):
    """Concept item returned from a text search."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        """Initialize the concept item."""
        super().__init__(**kwargs)
        self.score: float | None = score
