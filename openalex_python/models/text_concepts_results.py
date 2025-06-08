"""Concept extraction results from text."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .all_of_text_concepts_results_concepts_items import (
    AllOfTextConceptsResultsConceptsItems,
)
from .text_concepts_results_meta import TextConceptsResultsMeta


@dataclass(slots=True)
class TextConceptsResults:
    """Concepts identified in a text body."""

    meta: TextConceptsResultsMeta | None = None
    concepts: Iterable[AllOfTextConceptsResultsConceptsItems] | None = None

    def __post_init__(self) -> None:
        """Normalize concepts list."""
        if self.concepts is not None:
            self.concepts = list(self.concepts)
