"""Models for the text analysis API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .concept import Concept
from .topic import Topic
from .common import Meta


@dataclass(slots=True)
class TextBody:
    """Input text to be analyzed."""

    title: str
    abstract: str | None = None


class AllOfTextResultsConceptsItems(Concept):
    """Concept result with a relevance score."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = score


class AllOfTextResultsTopicsItems(Topic):
    """Topic result with a relevance score."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = score


class AllOfTextConceptsResultsConceptsItems(Concept):
    """Concept item returned from a text search."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = score


class AllOfTextTopicsResultsTopicsItems(Topic):
    """Topic item returned from a text search."""

    def __init__(self, *, score: float | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.score = score


@dataclass(slots=True)
class TextConceptsResultsMeta:
    """Counts accompanying concept extraction results."""

    concepts_count: int | None = None


@dataclass(slots=True)
class TextConceptsResults:
    """Concepts identified in a text body."""

    meta: TextConceptsResultsMeta | None = None
    concepts: Iterable[AllOfTextConceptsResultsConceptsItems] | None = None

    def __post_init__(self) -> None:
        if self.concepts is not None:
            self.concepts = list(self.concepts)


@dataclass(slots=True)
class TextKeyword:
    """Keyword associated with a work or query."""

    id: str
    display_name: str
    score: float


@dataclass(slots=True)
class TextKeywordsResultsMeta:
    """Counts accompanying keyword results."""

    keywords_count: int | None = None


@dataclass(slots=True)
class TextKeywordsResults:
    """List of keywords with associated metadata."""

    meta: TextKeywordsResultsMeta | None = None
    keywords: Iterable[TextKeyword] | None = None

    def __post_init__(self) -> None:
        if self.keywords is not None:
            self.keywords = list(self.keywords)


@dataclass(slots=True)
class TextMeta:
    """Counts of text entities returned from the API."""

    keywords_count: int | None = None
    topics_count: int | None = None
    concepts_count: int | None = None


@dataclass(slots=True)
class TextResults:
    """Container for text keywords, topics, and concepts."""

    meta: TextMeta | None = None
    keywords: Iterable[TextKeyword] | None = None
    primary_topic: Topic | None = None
    topics: Iterable[AllOfTextResultsTopicsItems] | None = None
    concepts: Iterable[AllOfTextResultsConceptsItems] | None = None

    def __post_init__(self) -> None:
        if self.keywords is not None:
            self.keywords = list(self.keywords)
        if self.topics is not None:
            self.topics = list(self.topics)
        if self.concepts is not None:
            self.concepts = list(self.concepts)


@dataclass(slots=True)
class TextTopicsResultsMeta:
    """Summary information about topics."""

    topics_count: int | None = None


@dataclass(slots=True)
class TextTopicsResults:
    """Topics detected in a block of text."""

    meta: TextTopicsResultsMeta | None = None
    primary_topic: Topic | None = None
    topics: Iterable[AllOfTextTopicsResultsTopicsItems] | None = None

    def __post_init__(self) -> None:
        if self.topics is not None:
            self.topics = list(self.topics)
