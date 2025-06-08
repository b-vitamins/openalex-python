"""Model for concept results returned directly from a text query."""
from __future__ import annotations

from typing import Any

from .concept import Concept


class AllOfTextResultsConceptsItems(Concept):
    """Concept result with a relevance score."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        """Initialize the result item."""
        super().__init__(**kwargs)
        self.score: float | None = score
