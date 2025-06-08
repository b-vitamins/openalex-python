"""Identifier collection for an author."""
from __future__ import annotations


class AuthorIds:
    """Various IDs pointing to author profiles in external systems."""

    def __init__(
        self,
        *,
        openalex: str,
        orcid: str | None = None,
        scopus: str | None = None,
        twitter: str | None = None,
        wikipedia: str | None = None,
    ) -> None:
        self.openalex = openalex
        self.orcid = orcid
        self.scopus = scopus
        self.twitter = twitter
        self.wikipedia = wikipedia

