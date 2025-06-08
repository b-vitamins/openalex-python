"""Container for a set of concept records."""
from __future__ import annotations

from collections.abc import Iterable

from .concept import Concept
from .group_by_result import GroupByResult
from .meta import Meta


class ConceptsList:
    """A list of concepts returned with metadata."""

    def __init__(
        self,
        *,
        meta: Meta,
        results: Iterable[Concept],
        group_by: GroupByResult | None = None,
    ) -> None:
        self.meta = meta
        self.results = list(results)
        self.group_by = group_by

