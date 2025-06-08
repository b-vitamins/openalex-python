"""Container for a set of concept records."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .concept import Concept
from .group_by_result import GroupByResult
from .meta import Meta


@dataclass(slots=True)
class ConceptsList:
    """A list of concepts returned with metadata."""

    meta: Meta
    results: Iterable[Concept]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Normalize results to a list."""
        self.results = list(self.results)

