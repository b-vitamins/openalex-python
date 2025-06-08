"""Author model for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field, HttpUrl

from .base import CountsByYear, OpenAlexEntity, SummaryStats

if TYPE_CHECKING:
    from .work import DehydratedConcept, DehydratedInstitution


class AuthorIds(OpenAlexEntity):
    """External identifiers for an author."""

    openalex: str | None = None
    orcid: HttpUrl | None = None
    scopus: str | None = None
    twitter: str | None = None
    wikipedia: HttpUrl | None = None
    mag: int | None = None


class AuthorAffiliation(OpenAlexEntity):
    """Author affiliation information."""

    institution: DehydratedInstitution | None = None
    years: list[int] = Field(default_factory=list)


class Author(OpenAlexEntity):
    """Full author model."""

    orcid: HttpUrl | None = None

    display_name_alternatives: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    affiliations: list[AuthorAffiliation] = Field(
        default_factory=list, description="Institutional affiliations"
    )

    last_known_institutions: list[DehydratedInstitution] = Field(
        default_factory=list, description="Most recent affiliations"
    )

    x_concepts: list[DehydratedConcept] = Field(
        default_factory=list, description="Associated concepts"
    )

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    works_api_url: HttpUrl | None = Field(
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

        max_citations = 0
        for year_data in self.counts_by_year:
            if year_data.cited_by_count > max_citations:
                max_citations = year_data.cited_by_count

        return max_citations

    def works_in_year(self, year: int) -> int:
        """Get number of works published in a specific year."""
        for year_data in self.counts_by_year:
            if year_data.year == year:
                return year_data.works_count
        return 0

    def citations_in_year(self, year: int) -> int:
        """Get number of citations in a specific year."""
        for year_data in self.counts_by_year:
            if year_data.year == year:
                return year_data.cited_by_count
        return 0

    def active_years(self) -> list[int]:
        """Get list of years with publications."""
        return sorted(
            [y.year for y in self.counts_by_year if y.works_count > 0]
        )

    def institution_names(self) -> list[str]:
        """Get list of affiliated institution names."""
        names = []
        for affiliation in self.affiliations:
            if affiliation.institution and affiliation.institution.display_name:
                names.append(affiliation.institution.display_name)
        return list(set(names))  # Remove duplicates

    def concept_names(self) -> list[str]:
        """Get list of associated concept names."""
        return [c.display_name for c in self.x_concepts if c.display_name]
