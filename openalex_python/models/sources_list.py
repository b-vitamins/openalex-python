"""Container for lists of sources returned by the API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .group_by_result import GroupByResult
from .meta import Meta
from .source import Source


@dataclass(slots=True)
class SourcesList:
    """API response with source records."""

    meta: Meta
    results: Iterable[Source]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results is a list."""
        self.results = list(self.results)
