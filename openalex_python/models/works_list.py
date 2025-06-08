"""A list of works returned from the API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .group_by_result import GroupByResult
from .meta import Meta
from .work import Work


@dataclass(slots=True)
class WorksList:
    """Container for a collection of works."""

    meta: Meta
    results: Iterable[Work]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results is a list."""
        self.results = list(self.results)
