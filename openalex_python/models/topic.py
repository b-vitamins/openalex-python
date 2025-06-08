"""Model representing a research topic."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .common import GroupByResult, Meta


@dataclass(slots=True)
class Topic:
    """High level description of an OpenAlex topic."""

    id: str
    display_name: str
    description: str | None = None
    keywords: Iterable[str] | None = None
    subfield: TopicLevel | None = None
    field: TopicLevel | None = None
    domain: TopicLevel | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: TopicIds | None = None

    def __post_init__(self) -> None:
        """Convert iterable keywords to a list."""
        if self.keywords is not None:
            self.keywords = list(self.keywords)


@dataclass(slots=True)
class TopicLevel:
    """Represents one level in the topic hierarchy."""

    id: str
    display_name: str


@dataclass(slots=True)
class TopicIds:
    """Various IDs associated with a topic."""

    openalex: str
    wikipedia: str | None = None


class DehydratedTopic:
    """Basic topic details."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        score: float | None = None,
        subfield: TopicLevel | None = None,
        field: TopicLevel | None = None,
        domain: TopicLevel | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.score = score
        self.subfield = subfield
        self.field = field
        self.domain = domain


@dataclass(slots=True)
class TopicsList:
    """Container for topics and related metadata."""

    meta: Meta
    results: Iterable[Topic]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
