"""API results for topic extraction from text."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .all_of_text_topics_results_topics_items import AllOfTextTopicsResultsTopicsItems
from .text_topics_results_meta import TextTopicsResultsMeta
from .topic import Topic


@dataclass(slots=True)
class TextTopicsResults:
    """Topics detected in a block of text."""

    meta: TextTopicsResultsMeta | None = None
    primary_topic: Topic | None = None
    topics: Iterable[AllOfTextTopicsResultsTopicsItems] | None = None

    def __post_init__(self) -> None:
        """Convert iterable topics to a list."""
        if self.topics is not None:
            self.topics = list(self.topics)
