"""Institution model for OpenAlex API."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

__all__ = [
    "AssociatedInstitution",
    "Institution",
    "InstitutionIds",
    "InstitutionTopic",
    "InstitutionTopicShare",
    "InstitutionType",
    "Repository",
]

from pydantic import Field, HttpUrl, TypeAdapter, field_validator

from .base import (
    CountsByYear,
    Geo,
    InternationalNames,
    OpenAlexBase,
    OpenAlexEntity,
    Role,
    SummaryStats,
)

if TYPE_CHECKING:
    from .topic import TopicHierarchy
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
    FUNDER = "funder"


class Repository(OpenAlexEntity):
    """Repository information."""

    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] = Field(default_factory=list)


class AssociatedInstitution(OpenAlexEntity):
    """Associated institution information."""

    relationship: str | None = None
    ror: str | None = None
    country_code: str | None = None
    type: InstitutionType | None = None


class InstitutionTopic(OpenAlexEntity):
    """Topic statistics for an institution."""

    count: int | None = None
    subfield: TopicHierarchy | None = None
    field: TopicHierarchy | None = None
    domain: TopicHierarchy | None = None


class InstitutionTopicShare(OpenAlexEntity):
    """Topic share information for an institution."""

    value: float | None = None
    subfield: TopicHierarchy | None = None
    field: TopicHierarchy | None = None
    domain: TopicHierarchy | None = None


class InstitutionIds(OpenAlexBase):
    """External identifiers for an institution."""

    openalex: str | None = None
    ror: str | None = None
    grid: str | None = None
    wikipedia: str | None = None
    wikidata: str | None = None
    mag: str | None = None


class Institution(OpenAlexEntity):
    """Full institution model."""

    ror: str | None = None

    display_name_alternatives: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    display_name_acronyms: list[str] = Field(
        default_factory=list, description="Acronyms"
    )

    country_code: str | None = Field(None, description="ISO country code")
    type: InstitutionType | None = None

    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None

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

    parent_institution: AssociatedInstitution | None = None

    is_super_system: bool = Field(
        default=False,
        description="Whether this is a parent of other institutions",
    )

    international_display_name: dict[str, str] | None = Field(
        default=None, alias="international_display_name"
    )

    international: InternationalNames | None = None

    topics: list[InstitutionTopic] = Field(
        default_factory=list, description="Research topics"
    )

    topic_share: list[InstitutionTopicShare] = Field(
        default_factory=list, description="Topic share statistics"
    )

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

    works_api_url: str | None = Field(
        None, description="API URL for institution's works"
    )

    ids: InstitutionIds | None = None

    @field_validator("ror")
    @classmethod
    def validate_ror(cls, v: str | None) -> str | None:
        """Ensure ROR is a valid URL."""
        if v is None:
            return None
        TypeAdapter(HttpUrl).validate_python(v)
        return v

    @field_validator("image_thumbnail_url", mode="before")
    @classmethod
    def normalize_thumbnail_url(cls, v: Any) -> Any:
        """Ensure thumbnail URLs contain 'thumbnail'."""
        if isinstance(v, str) and "thumbnail" not in v and "/thumb/" in v:
            return v.replace("/thumb/", "/thumbnail/")
        return v

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Ensure country code is two uppercase letters."""
        if v is None:
            return None
        if len(v) != 2 or not v.isalpha():
            msg = "Invalid country code"
            raise ValueError(msg)
        return v.upper()

    @property
    def is_education(self) -> bool:
        """Check if institution is educational."""
        return self.type == InstitutionType.EDUCATION

    @property
    def is_company(self) -> bool:
        """Check if institution is a company."""
        return self.type == InstitutionType.COMPANY

    @property
    def type_id(self) -> str | None:
        """Return OpenAlex type ID."""
        if self.type is None:
            return None
        return f"https://openalex.org/institution-types/{self.type}"

    @property
    def parent_institution_id(self) -> str | None:
        """Get immediate parent institution ID."""
        if self.lineage and len(self.lineage) > 1:
            return self.lineage[1]
        return None

    @property
    def root_institution(self) -> str | None:
        """Get root institution ID in hierarchy."""
        if self.lineage and len(self.lineage) > 1:
            return self.lineage[-1]
        return None

    def repository_count(self) -> int:
        """Get number of repositories."""
        return len(self.repositories)

    def has_location(self) -> bool:
        """Check if geographic location is available."""
        return self.geo is not None and (
            self.geo.latitude is not None or self.geo.city is not None
        )

    @property
    def h_index(self) -> int | None:
        """Get h-index from summary stats."""
        return self.summary_stats.h_index if self.summary_stats else None

    @property
    def i10_index(self) -> int | None:
        """Get i10-index from summary stats."""
        return self.summary_stats.i10_index if self.summary_stats else None

    @property
    def two_year_mean_citedness(self) -> float | None:
        """Get 2-year mean citedness from summary stats."""
        return (
            self.summary_stats.two_year_mean_citedness
            if self.summary_stats
            else None
        )

    def works_in_year(self, year: int) -> int:
        """Return works count for a given year."""
        return next(
            (
                year_data.works_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a given year."""
        return next(
            (
                year_data.cited_by_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def active_years(self) -> list[int]:
        """Return list of years with publications."""
        return sorted(
            [y.year for y in self.counts_by_year if y.works_count > 0]
        )


from .topic import TopicHierarchy  # noqa: E402,TC001
from .work import DehydratedConcept  # noqa: E402,TC001

Institution.model_rebuild()
