"""Keyword assigned to a work."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .common import GroupByResult, Meta


@dataclass(slots=True)
class Keyword:
    """Represents a keyword."""

    id: str
    display_name: str
    works_count: int | None = None
    cited_by_count: int | None = None
    updated_date: datetime | None = None
    created_date: date | None = None


@dataclass(slots=True)
class KeywordsList:
    """Keywords returned from the API."""

    meta: Meta
    results: list[Keyword]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
