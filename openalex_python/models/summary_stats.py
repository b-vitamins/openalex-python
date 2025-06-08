"""Summary impact statistics for an entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SummaryStats:
    """Basic citation metrics."""

    two_year_mean_citedness: float | None = None
    h_index: int | None = None
    i10_index: int | None = None
