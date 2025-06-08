"""Container for a page of keywords."""
from __future__ import annotations

from dataclasses import dataclass

from .group_by_result import GroupByResult
from .keyword import Keyword
from .meta import Meta


@dataclass(slots=True)
class KeywordsList:
    """Keywords returned from the API."""

    meta: Meta
    results: list[Keyword]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results is always a list."""
        self.results = list(self.results)
