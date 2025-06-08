"""Publisher model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field, HttpUrl

from .base import CountsByYear, OpenAlexEntity, Role, SummaryStats


class PublisherIds(OpenAlexEntity):
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

    hierarchy_level: int | None = Field(
        None, description="Level in publisher hierarchy"
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
