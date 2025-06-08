"""Minimal representation of an author."""
from __future__ import annotations


class DehydratedAuthor:
    """Lightweight author record."""

    def __init__(self, *, id: str, display_name: str, orcid: str | None = None) -> None:
        self.id = id
        self.display_name = display_name
        self.orcid = orcid
