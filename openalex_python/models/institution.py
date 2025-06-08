"""Full representation of an institution."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .concept import DehydratedConcept
from .common import (
    CountsByYear,
    Geo,
    GroupByResult,
    InternationalNames,
    Meta,
    Role,
    SummaryStats,
)


@dataclass(slots=True)
class Institution:
    """Detailed institution metadata."""

    id: str
    display_name: str
    ror: str | None = None
    display_name_alternatives: Iterable[str] | None = None
    display_name_acronyms: Iterable[str] | None = None
    country_code: str | None = None
    type: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    geo: Geo | None = None
    associated_institutions: list[AssociatedInstitution] | None = None
    repositories: list[Repository] | None = None
    lineage: list[str] | None = None
    is_super_system: bool | None = None
    international: InternationalNames | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    roles: list[Role] | None = None
    x_concepts: list[DehydratedConcept] | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: InstitutionIds | None = None

    def __post_init__(self) -> None:
        """Normalize iterable attributes to lists."""
        self.display_name_alternatives = (
            list(self.display_name_alternatives)
            if self.display_name_alternatives is not None
            else None
        )
        self.display_name_acronyms = (
            list(self.display_name_acronyms)
            if self.display_name_acronyms is not None
            else None
        )
        self.associated_institutions = (
            list(self.associated_institutions)
            if self.associated_institutions is not None
            else None
        )
        self.repositories = (
            list(self.repositories) if self.repositories is not None else None
        )
        self.lineage = list(self.lineage) if self.lineage is not None else None
        self.roles = list(self.roles) if self.roles is not None else None
        self.x_concepts = list(self.x_concepts) if self.x_concepts is not None else None


@dataclass(slots=True)
class Repository:
    """Institutional or subject repository details."""

    id: str | None = None
    display_name: str | None = None
    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] | None = None

    def __post_init__(self) -> None:
        self.host_organization_lineage = (
            list(self.host_organization_lineage)
            if self.host_organization_lineage is not None
            else None
        )


@dataclass(slots=True)
class AssociatedInstitution:
    """Institution linked with an author."""

    id: str
    display_name: str
    relationship: str
    ror: str | None = None
    country_code: str | None = None
    type: str | None = None


class DehydratedInstitution:
    """Minimal institution record."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        ror: str | None = None,
        country_code: str | None = None,
        type: str | None = None,
        lineage: Iterable[str] | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.ror = ror
        self.country_code = country_code
        self.type = type
        self.lineage = list(lineage) if lineage is not None else None


@dataclass(slots=True)
class InstitutionIds:
    """Collection of identifier strings."""

    openalex: str
    ror: str | None = None
    grid: str | None = None
    wikipedia: str | None = None
    wikidata: str | None = None
    mag: int | None = None


@dataclass(slots=True)
class InstitutionsList:
    """Institutions returned from the API."""

    meta: Meta
    results: list[Institution]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
