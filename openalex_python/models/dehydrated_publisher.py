"""Minimal representation of a publisher."""
from __future__ import annotations


class DehydratedPublisher:
    """Basic publisher data."""

    def __init__(self, *, id: str, display_name: str) -> None:
        self.id = id
        self.display_name = display_name
