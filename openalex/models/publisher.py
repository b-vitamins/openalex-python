"""Publisher model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field, HttpUrl

__all__ = ["Publisher", "PublisherIds"]

from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, Role, SummaryStats


class PublisherIds(OpenAlexBase):
    """External identifiers for a publisher."""

    openalex: str | None = None
    ror: HttpUrl | None = None
    wikidata: HttpUrl | None = None


class Publisher(OpenAlexEntity):
    """Full publisher model."""

    alternate_titles: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    country_codes: list[str] = Field(
        default_factory=list, description="Countries of operation"
    )

    hierarchy_level: int = Field(
        0,
        ge=0,
        description="Level in publisher hierarchy",
    )

    parent_publisher: str | None = Field(
        None, description="Parent publisher ID"
    )

    lineage: list[str] = Field(
        default_factory=list, description="Publisher hierarchy"
    )

    homepage_url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    image_thumbnail_url: HttpUrl | None = None

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    sources_api_url: HttpUrl | None = Field(
        None, description="API URL for publisher's sources"
    )

    roles: list[Role] = Field(
        default_factory=list, description="Roles in publishing ecosystem"
    )

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    ids: PublisherIds | None = None

    @property
    def is_parent_publisher(self) -> bool:
        """Check if this is a parent publisher."""
        return (
            self.hierarchy_level == 0
            if self.hierarchy_level is not None
            else False
        )

    @property
    def countries(self) -> list[str]:
        """Get list of countries (alias for country_codes)."""
        return self.country_codes

    def has_parent(self) -> bool:
        """Check if publisher has a parent."""
        return self.parent_publisher is not None

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
