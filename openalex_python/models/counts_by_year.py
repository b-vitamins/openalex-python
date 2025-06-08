"""Sequence of yearly statistics for a work or concept."""
from __future__ import annotations

from collections.abc import Iterable

from .counts_by_year_inner import CountsByYearInner


class CountsByYear:
    """Container for yearly count data."""

    def __init__(self, results: Iterable[CountsByYearInner]) -> None:
        self.results = list(results)

