"""Bibliographic information about a work."""
from __future__ import annotations


class Biblio:
    """Container for bibliographic fields."""

    def __init__(
        self,
        *,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> None:
        self.volume = volume
        self.issue = issue
        self.first_page = first_page
        self.last_page = last_page

