"""Sequence of yearly statistics for a work or concept."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .counts_by_year_inner import CountsByYearInner


@dataclass(slots=True)
class CountsByYear:
    """Container for yearly count data."""

    results: Iterable[CountsByYearInner]

    def __post_init__(self) -> None:
        """Normalize results to a list."""
        self.results = list(self.results)

