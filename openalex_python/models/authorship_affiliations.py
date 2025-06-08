"""Affiliation details for an authorship record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AuthorshipAffiliations:
    """Stores raw affiliation string and related institution IDs."""

    raw_affiliation_string: str | None = None
    institution_ids: list[str] | None = None

    def __post_init__(self) -> None:
        """Normalize the institution ID list."""
        self.institution_ids = list(self.institution_ids or [])
