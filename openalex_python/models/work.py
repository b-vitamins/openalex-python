"""Representation of an individual work (publication)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .author import Authorship
from .concept import DehydratedConcept
from .topic import DehydratedTopic
from .common import CountsByYear, GroupByResult, Meta
from .source import DehydratedSource


@dataclass(slots=True)
class Work:
    """Detailed metadata about a scholarly work."""

    id: str
    doi: str | None = None
    title: str | None = None
    display_name: str | None = None
    publication_year: int | None = None
    publication_date: date | None = None
    type: str | None = None
    type_crossref: str | None = None
    indexed_in: Iterable[str] | None = None
    open_access: OpenAccess | None = None
    authorships: Iterable[Authorship] | None = None
    corresponding_author_ids: Iterable[str] | None = None
    corresponding_institution_ids: Iterable[str] | None = None
    countries_distinct_count: int | None = None
    institutions_distinct_count: int | None = None
    cited_by_count: int | None = None
    citation_normalized_percentile: WorkCitationNormalizedPercentile | None = None
    biblio: Biblio | None = None
    is_retracted: bool | None = None
    is_paratext: bool | None = None
    primary_location: Location | None = None
    best_oa_location: Location | None = None
    locations: Iterable[Location] | None = None
    locations_count: int | None = None
    mesh: Iterable[MeshTag] | None = None
    keywords: Iterable[KeywordTag] | None = None
    concepts: Iterable[DehydratedConcept] | None = None
    primary_topic: DehydratedTopic | None = None
    topics: Iterable[DehydratedTopic] | None = None
    grants: Iterable[Grant] | None = None
    apc_list: APC | None = None
    apc_paid: APC | None = None
    fwci: float | None = None
    has_fulltext: bool | None = None
    fulltext_origin: str | None = None
    cited_by_api_url: str | None = None
    counts_by_year: CountsByYear | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    abstract_inverted_index: dict[str, list[int]] | None = None
    language: str | None = None
    license: str | None = None
    referenced_works: Iterable[str] | None = None
    related_works: Iterable[str] | None = None
    sustainable_development_goals: Iterable[SustainableDevelopmentGoal] | None = None
    ids: WorkIds | None = None

    def __post_init__(self) -> None:
        """Ensure all iterable fields are lists."""
        self.indexed_in = list(self.indexed_in) if self.indexed_in is not None else None
        self.authorships = (
            list(self.authorships) if self.authorships is not None else None
        )
        self.corresponding_author_ids = (
            list(self.corresponding_author_ids)
            if self.corresponding_author_ids is not None
            else None
        )
        self.corresponding_institution_ids = (
            list(self.corresponding_institution_ids)
            if self.corresponding_institution_ids is not None
            else None
        )
        self.locations = list(self.locations) if self.locations is not None else None
        self.mesh = list(self.mesh) if self.mesh is not None else None
        self.keywords = list(self.keywords) if self.keywords is not None else None
        self.concepts = list(self.concepts) if self.concepts is not None else None
        self.topics = list(self.topics) if self.topics is not None else None
        self.grants = list(self.grants) if self.grants is not None else None
        self.referenced_works = (
            list(self.referenced_works) if self.referenced_works is not None else None
        )
        self.related_works = (
            list(self.related_works) if self.related_works is not None else None
        )
        self.sustainable_development_goals = (
            list(self.sustainable_development_goals)
            if self.sustainable_development_goals is not None
            else None
        )


@dataclass(slots=True)
class APC:
    """Article processing charge details."""

    value: int | None = None
    currency: str | None = None


@dataclass(slots=True)
class Biblio:
    """Container for bibliographic fields."""

    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None


@dataclass(slots=True)
class Location:
    """Details about where a work can be found."""

    is_oa: bool | None = None
    landing_page_url: str | None = None
    pdf_url: str | None = None
    source: DehydratedSource | None = None
    license: str | None = None
    license_id: str | None = None
    version: str | None = None
    is_accepted: bool | None = None
    is_published: bool | None = None


@dataclass(slots=True)
class MeshTag:
    """MeSH descriptor and qualifier."""

    descriptor_ui: str
    descriptor_name: str
    is_major_topic: bool
    qualifier_ui: str | None = None
    qualifier_name: str | None = None


@dataclass(slots=True)
class KeywordTag:
    """Keyword with relevance score."""

    id: str
    display_name: str
    score: float


@dataclass(slots=True)
class Grant:
    """Funding grant metadata."""

    funder: str
    funder_display_name: str | None = None
    award_id: str | None = None


@dataclass(slots=True)
class OpenAccess:
    """Details about a work's OA status."""

    is_oa: bool
    oa_status: str
    oa_url: str | None = None
    any_repository_has_fulltext: bool | None = None


@dataclass(slots=True)
class SustainableDevelopmentGoal:
    """SDG tag for a work."""

    id: int
    description: str | None = None


@dataclass(slots=True)
class WorkCitationNormalizedPercentile:
    """Citation percentile scores."""

    value: float | None = None
    is_in_top_1_percent: bool | None = None
    is_in_top_10_percent: bool | None = None


@dataclass(slots=True)
class WorkIds:
    """Various IDs referencing a work."""

    openalex: str
    doi: str | None = None
    mag: int | None = None
    pmid: str | None = None
    pmcid: str | None = None


@dataclass(slots=True)
class WorksList:
    """Container for a collection of works."""

    meta: Meta
    results: Iterable[Work]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
