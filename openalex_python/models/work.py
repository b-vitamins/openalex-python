"""Representation of an individual work (publication)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .apc import APC
from .authorship import Authorship
from .biblio import Biblio
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .dehydrated_topic import DehydratedTopic
from .grant import Grant
from .keyword_tag import KeywordTag
from .location import Location
from .mesh_tag import MeshTag
from .open_access import OpenAccess
from .sustainable_development_goal import SustainableDevelopmentGoal
from .work_citation_normalized_percentile import WorkCitationNormalizedPercentile
from .work_ids import WorkIds


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
