"""Single year's work and citation counts."""
from __future__ import annotations


class CountsByYearInner:
    """Counts of works and citations for a particular year."""

    def __init__(
        self,
        *,
        year: int,
        works_count: int | None = None,
        cited_by_count: int | None = None,
    ) -> None:
        self.year = year
        self.works_count = works_count
        self.cited_by_count = cited_by_count
