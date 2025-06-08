"""Institution model for OpenAlex API."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import Field, HttpUrl

from .base import (
    CountsByYear,
    Geo,
    InternationalNames,
    OpenAlexEntity,
    Role,
    SummaryStats,
)

if TYPE_CHECKING:
    from .work import DehydratedConcept


class InstitutionType(str, Enum):
    """Types of institutions."""

    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    COMPANY = "company"
    ARCHIVE = "archive"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    FACILITY = "facility"
    OTHER = "other"


class Repository(OpenAlexEntity):
    """Repository information."""

    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] = Field(default_factory=list)


class AssociatedInstitution(OpenAlexEntity):
    """Associated institution information."""

    relationship: str | None = None
    ror: HttpUrl | None = None
    country_code: str | None = None
    type: InstitutionType | None = None


class InstitutionIds(OpenAlexEntity):
    """External identifiers for an institution."""

    openalex: str | None = None
    ror: HttpUrl | None = None
    grid: str | None = None
    wikipedia: HttpUrl | None = None
    wikidata: HttpUrl | None = None
    mag: int | None = None


class Institution(OpenAlexEntity):
    """Full institution model."""

    ror: HttpUrl | None = None

    display_name_alternatives: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    display_name_acronyms: list[str] = Field(
        default_factory=list, description="Acronyms"
    )

    country_code: str | None = Field(None, description="ISO country code")
    type: InstitutionType | None = None

    homepage_url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    image_thumbnail_url: HttpUrl | None = None

    geo: Geo | None = None

    associated_institutions: list[AssociatedInstitution] = Field(
        default_factory=list, description="Related institutions"
    )

    repositories: list[Repository] = Field(
        default_factory=list, description="Institutional repositories"
    )

    lineage: list[str] = Field(
        default_factory=list, description="Parent institution hierarchy"
    )

    is_super_system: bool = Field(
        False, description="Whether this is a parent of other institutions"
    )

    international: InternationalNames | None = None

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    roles: list[Role] = Field(
        default_factory=list, description="Roles in the research ecosystem"
    )

    x_concepts: list[DehydratedConcept] = Field(
        default_factory=list, description="Associated research concepts"
    )

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    works_api_url: HttpUrl | None = Field(
        None, description="API URL for institution's works"
    )

    ids: InstitutionIds | None = None

    @property
    def is_education(self) -> bool:
        """Check if institution is educational."""
        return self.type == InstitutionType.EDUCATION

    @property
    def is_company(self) -> bool:
        """Check if institution is a company."""
        return self.type == InstitutionType.COMPANY

    @property
    def parent_institution(self) -> str | None:
        """Get immediate parent institution ID."""
        if self.lineage and len(self.lineage) > 1:
            return self.lineage[-2]  # Last item is self
        return None

    @property
    def root_institution(self) -> str | None:
        """Get root institution ID in hierarchy."""
        if self.lineage and len(self.lineage) > 1:
            return self.lineage[0]
        return None

    def repository_count(self) -> int:
        """Get number of repositories."""
        return len(self.repositories)

    def has_location(self) -> bool:
        """Check if geographic location is available."""
        return self.geo is not None and (
            self.geo.latitude is not None or self.geo.city is not None
        )
