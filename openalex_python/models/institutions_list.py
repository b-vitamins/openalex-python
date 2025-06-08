"""Container for a page of institutions."""
from __future__ import annotations

from dataclasses import dataclass

from .group_by_result import GroupByResult
from .institution import Institution
from .meta import Meta


@dataclass(slots=True)
class InstitutionsList:
    """Institutions returned from the API."""

    meta: Meta
    results: list[Institution]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        """Ensure results is always a list."""
        self.results = list(self.results)
