"""Model representing a list of authors returned from the API."""

from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from .author import Author
from .group_by_result import GroupByResult
from .meta import Meta
@dataclass(slots=True)
    """A collection of authors with associated metadata."""

    meta: Meta
    results: list[Author] | Iterable[Author]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Convert results iterable to a list."""
        self.results = list(self.results)
