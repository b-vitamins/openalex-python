"""Model describing how an author contributed to a work."""
from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from .authorship_affiliations import AuthorshipAffiliations
from .dehydrated_author import DehydratedAuthor
from .dehydrated_institution import DehydratedInstitution
@dataclass(slots=True)
    """Information about an author's role in a work."""
    author_position: str
    author: DehydratedAuthor
    institutions: Iterable[DehydratedInstitution]
    countries: Iterable[str]
    is_corresponding: bool | None = None
    raw_author_name: str | None = None
    raw_affiliation_strings: Iterable[str] | None = None
    affiliations: Iterable[AuthorshipAffiliations] | None = None

    def __post_init__(self) -> None:
        """Convert iterables to lists for consistency."""
        self.institutions = list(self.institutions)
        self.countries = list(self.countries)
        if self.raw_affiliation_strings:
            self.raw_affiliation_strings = list(self.raw_affiliation_strings)
        else:
            self.raw_affiliation_strings = []
        self.affiliations = list(self.affiliations) if self.affiliations else []
