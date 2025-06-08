"""List of publishers returned by the API."""
from __future__ import annotations

from dataclasses import dataclass

from .group_by_result import GroupByResult
from .meta import Meta
from .publisher import Publisher


@dataclass(slots=True)
class PublishersList:
    """Container for a page of publishers."""

    meta: Meta
    results: list[Publisher]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results is always a list."""
        self.results = list(self.results)
