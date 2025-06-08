"""Model describing an author's institutional affiliations."""

from __future__ import annotations

from dataclasses import dataclass

from .dehydrated_institution import DehydratedInstitution


@dataclass(slots=True)
class AuthorAffiliations:
    """Institutions an author has been affiliated with."""

    institution: DehydratedInstitution
    years: list[int] | None = None

    def __post_init__(self) -> None:
        """Ensure years is always a list."""
        self.years = list(self.years or [])
