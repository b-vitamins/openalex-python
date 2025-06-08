"""Compact representation of a funder."""
from __future__ import annotations


class DehydratedFunder:
    """Basic funder details."""

    def __init__(self, *, id: str, display_name: str) -> None:
        self.id = id
        self.display_name = display_name
