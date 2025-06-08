"""Citation percentile information for a work."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkCitationNormalizedPercentile:
    """Citation percentile scores."""

    value: float | None = None
    is_in_top_1_percent: bool | None = None
    is_in_top_10_percent: bool | None = None
