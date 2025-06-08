"""Metadata about API responses."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Meta:
    """Pagination and performance information."""

    count: int
    db_response_time_ms: int
    page: int
    per_page: int
    groups_count: int | None = None
    next_cursor: str | None = None
