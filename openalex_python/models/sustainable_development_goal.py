"""UN sustainable development goal classification."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SustainableDevelopmentGoal:
    """A predicted SDG association."""

    id: str
    display_name: str
    score: float
