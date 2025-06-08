"""Model describing an author's institutional affiliations."""
from __future__ import annotations

from collections.abc import Iterable

from .dehydrated_institution import DehydratedInstitution


class AuthorAffiliations:
    """Institutions an author has been affiliated with."""

    def __init__(
        self,
        *,
        institution: DehydratedInstitution,
        years: Iterable[int] | None = None,
    ) -> None:
        self.institution = institution
        self.years = list(years) if years is not None else []

