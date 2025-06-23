"""Author model for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "Author",
    "AuthorAffiliation",
    "AuthorIds",
    "AuthorTopic",
    "AuthorTopicShare",
]

from pydantic import Field, HttpUrl, TypeAdapter, field_validator

from ..constants import ORCID_URL_PREFIX
from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, SummaryStats

if TYPE_CHECKING:
    from .topic import TopicHierarchy
    from .work import DehydratedConcept, DehydratedInstitution


class AuthorIds(OpenAlexBase):
    """External identifiers for an author."""

    openalex: str | None = None
    orcid: str | None = None
    scopus: str | None = None
    twitter: str | None = None
    wikipedia: HttpUrl | None = None
    mag: int | None = None


class AuthorAffiliation(OpenAlexBase):
    """Author affiliation information."""

    institution: DehydratedInstitution | None = None
    years: list[int] = Field(default_factory=lambda: [])


class AuthorTopic(OpenAlexEntity):
    """Topic statistics for an author."""

    count: int | None = None
    subfield: TopicHierarchy | None = None
    field: TopicHierarchy | None = None
    domain: TopicHierarchy | None = None


class AuthorTopicShare(OpenAlexEntity):
    """Topic share information for an author."""

    value: float | None = None
    subfield: TopicHierarchy | None = None
    field: TopicHierarchy | None = None
    domain: TopicHierarchy | None = None


class Author(OpenAlexEntity):
    """Full author model."""

    orcid: str | None = None

    @field_validator("orcid")
    @classmethod
    def validate_orcid(cls, v: str | None) -> str | None:
        """Validate ORCID format."""
        if v is None:
            return None
        if not v.startswith(ORCID_URL_PREFIX):
            msg = "Invalid ORCID"
            raise ValueError(msg)
        TypeAdapter(HttpUrl).validate_python(v)
        return v

    display_name_alternatives: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    works_count: int = Field(0, ge=0, description="Number of works")
    cited_by_count: int = Field(0, ge=0, description="Total citations")

    summary_stats: SummaryStats | None = None

    affiliations: list[AuthorAffiliation] = Field(
        default_factory=lambda: [], description="Institutional affiliations"
    )

    last_known_institution: DehydratedInstitution | None = None

    last_known_institutions: list[DehydratedInstitution] = Field(
        default_factory=lambda: [], description="Most recent affiliations"
    )

    x_concepts: list[DehydratedConcept] = Field(
        default_factory=lambda: [], description="Associated concepts"
    )

    topics: list[AuthorTopic] = Field(default_factory=lambda: [])
    topic_share: list[AuthorTopicShare] = Field(default_factory=lambda: [])

    counts_by_year: list[CountsByYear] = Field(
        default_factory=lambda: [],
        description="Yearly publication and citation counts",
    )

    works_api_url: str | None = Field(
        None, description="API URL for author's works"
    )

    ids: AuthorIds | None = None

    @property
    def h_index(self) -> int | None:
        """Get h-index from summary stats."""
        return self.summary_stats.h_index if self.summary_stats else None

    @property
    def i10_index(self) -> int | None:
        """Get i10-index from summary stats."""
        return self.summary_stats.i10_index if self.summary_stats else None

    @property
    def most_cited_work_count(self) -> int:
        """Get citation count of most cited work."""
        if not self.counts_by_year:
            return 0

        return max((y.cited_by_count for y in self.counts_by_year), default=0)

    @property
    def two_year_mean_citedness(self) -> float | None:
        """Return the 2-year mean citedness from summary stats."""
        if self.summary_stats is None:
            return None
        return self.summary_stats.two_year_mean_citedness

    def works_in_year(self, year: int) -> int:
        """Get number of works published in a specific year."""
        return next(
            (y.works_count for y in self.counts_by_year if y.year == year), 0
        )

    def citations_in_year(self, year: int) -> int:
        """Get number of citations in a specific year."""
        return next(
            (y.cited_by_count for y in self.counts_by_year if y.year == year), 0
        )

    def active_years(self) -> list[int]:
        """Get list of years with publications."""
        return sorted(
            {y.year for y in self.counts_by_year if y.works_count > 0}
        )

    def institution_names(self) -> list[str]:
        """Get list of affiliated institution names."""
        return list(
            {
                aff.institution.display_name
                for aff in self.affiliations
                if aff.institution and aff.institution.display_name
            }
        )

    def current_institutions(self) -> list[DehydratedInstitution]:
        """Return institutions with the most recent affiliation year."""
        if not self.affiliations:
            return []

        # Determine most recent year across all affiliations
        max_year = max(
            (max(a.years) for a in self.affiliations if a.years), default=None
        )
        if max_year is None:
            return []

        return [
            a.institution
            for a in self.affiliations
            if a.institution and max_year in a.years
        ]

    def concept_names(self) -> list[str]:
        """Get list of associated concept names."""
        return [c.display_name for c in self.x_concepts if c.display_name]


from .topic import TopicHierarchy  # noqa: E402,TC001
from .work import (  # noqa: E402,TC001
    DehydratedConcept,
    DehydratedInstitution,
)

Author.model_rebuild()
AuthorTopic.model_rebuild()
AuthorTopicShare.model_rebuild()
