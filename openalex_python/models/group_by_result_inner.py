"""Single bucket of a group-by result."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GroupByResultInner:
    """Item returned from a group-by aggregation."""

    key: str
    key_display_name: str
    count: int
