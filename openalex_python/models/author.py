"""Representation of an author in OpenAlex."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .concept import DehydratedConcept
from .institution import DehydratedInstitution
from .common import (
    CountsByYear,
    GroupByResult,
    Meta,
    SummaryStats,
)


@dataclass(slots=True)
class Author:
    """Core information about an author."""

    id: str
    display_name: str
    orcid: str | None = None
    display_name_alternatives: Iterable[str] | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    affiliations: Iterable[AuthorAffiliations] | None = None
    last_known_institutions: Iterable[DehydratedInstitution] | None = None
    x_concepts: Iterable[DehydratedConcept] | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: AuthorIds | None = None

    def __post_init__(self) -> None:
        """Ensure alternative names are stored as a list."""
        if self.display_name_alternatives is not None:
            self.display_name_alternatives = list(self.display_name_alternatives)
        if self.affiliations is not None:
            self.affiliations = list(self.affiliations)
        if self.last_known_institutions is not None:
            self.last_known_institutions = list(self.last_known_institutions)
        if self.x_concepts is not None:
            self.x_concepts = list(self.x_concepts)


@dataclass(slots=True)
class AuthorAffiliations:
    """Institutions an author has been affiliated with."""

    institution: DehydratedInstitution
    years: list[int] | None = None

    def __post_init__(self) -> None:
        self.years = list(self.years or [])


@dataclass(slots=True)
class AuthorIds:
    """Various IDs pointing to author profiles in external systems."""

    openalex: str
    orcid: str | None = None
    scopus: str | None = None
    twitter: str | None = None
    wikipedia: str | None = None


@dataclass(slots=True)
class AuthorshipAffiliations:
    """Stores raw affiliation string and related institution IDs."""

    raw_affiliation_string: str | None = None
    institution_ids: list[str] | None = None

    def __post_init__(self) -> None:
        self.institution_ids = list(self.institution_ids or [])


class DehydratedAuthor:
    """Lightweight author record."""

    def __init__(self, *, id: str, display_name: str, orcid: str | None = None) -> None:
        self.id = id
        self.display_name = display_name
        self.orcid = orcid


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
        self.institutions = list(self.institutions)
        self.countries = list(self.countries)
        self.raw_affiliation_strings = list(self.raw_affiliation_strings or [])
        self.affiliations = list(self.affiliations or [])


@dataclass(slots=True)
class AuthorsList:
    """A collection of authors with associated metadata."""

    meta: Meta
    results: list[Author] | Iterable[Author]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
