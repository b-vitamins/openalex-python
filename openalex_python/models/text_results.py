"""Full text analysis results returned from the API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .all_of_text_results_concepts_items import AllOfTextResultsConceptsItems
from .all_of_text_results_topics_items import AllOfTextResultsTopicsItems
from .text_keyword import TextKeyword
from .text_meta import TextMeta
from .topic import Topic


@dataclass(slots=True)
class TextResults:
    """Container for text keywords, topics, and concepts."""

    meta: TextMeta | None = None
    keywords: Iterable[TextKeyword] | None = None
    primary_topic: Topic | None = None
    topics: Iterable[AllOfTextResultsTopicsItems] | None = None
    concepts: Iterable[AllOfTextResultsConceptsItems] | None = None

    def __post_init__(self) -> None:
        """Normalize iterable fields to lists."""
        if self.keywords is not None:
            self.keywords = list(self.keywords)
        if self.topics is not None:
            self.topics = list(self.topics)
        if self.concepts is not None:
            self.concepts = list(self.concepts)
