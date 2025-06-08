"""Model describing how an author contributed to a work."""
from __future__ import annotations
from collections.abc import Iterable
from .authorship_affiliations import AuthorshipAffiliations
from .dehydrated_author import DehydratedAuthor
from .dehydrated_institution import DehydratedInstitution
    """Information about an author's role in a work."""
        *,
        author_position: str,
        author: DehydratedAuthor,
        institutions: Iterable[DehydratedInstitution],
        countries: Iterable[str],
        is_corresponding: bool | None = None,
        raw_author_name: str | None = None,
        raw_affiliation_strings: Iterable[str] | None = None,
        affiliations: Iterable[AuthorshipAffiliations] | None = None,
    ) -> None:
        self.institutions = list(institutions)
        self.countries = list(countries)
        self.is_corresponding = is_corresponding
        self.raw_author_name = raw_author_name
        self.raw_affiliation_strings = (
            list(raw_affiliation_strings) if raw_affiliation_strings else []
        )
        self.affiliations = list(affiliations) if affiliations else []
