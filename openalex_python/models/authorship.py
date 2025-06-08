"""Model describing how an author contributed to a work."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .authorship_affiliations import AuthorshipAffiliations
from .dehydrated_author import DehydratedAuthor
from .dehydrated_institution import DehydratedInstitution


@dataclass(slots=True)
class Authorship:
    """Information about an author's role in a work."""

    author_position: str
    author: DehydratedAuthor
    institutions: list[DehydratedInstitution]
    countries: list[str]
    is_corresponding: bool | None = None
    raw_author_name: str | None = None
    raw_affiliation_strings: Iterable[str] | None = None
    affiliations: list[AuthorshipAffiliations] | None = None

    def __post_init__(self) -> None:
        """Convert iterables to lists for consistency."""
        self.institutions = list(self.institutions)
        self.countries = list(self.countries)
        self.raw_affiliation_strings = list(self.raw_affiliation_strings or [])
        self.affiliations = list(self.affiliations or [])
