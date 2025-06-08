"""A list of topics returned from the API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .group_by_result import GroupByResult
from .meta import Meta
from .topic import Topic


@dataclass(slots=True)
class TopicsList:
    """Container for topics and related metadata."""

    meta: Meta
    results: Iterable[Topic]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results are stored as a list."""
        self.results = list(self.results)
