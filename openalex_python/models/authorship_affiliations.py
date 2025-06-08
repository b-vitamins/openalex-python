"""Affiliation details for an authorship record."""
from __future__ import annotations

from collections.abc import Iterable


class AuthorshipAffiliations:
    """Stores raw affiliation string and related institution IDs."""

    def __init__(
        self,
        *,
        raw_affiliation_string: str | None = None,
        institution_ids: Iterable[str] | None = None,
    ) -> None:
        self.raw_affiliation_string = raw_affiliation_string
        self.institution_ids = list(institution_ids) if institution_ids else []
