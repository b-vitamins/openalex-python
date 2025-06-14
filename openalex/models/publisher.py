"""Publisher model for OpenAlex API."""

from __future__ import annotations

from typing import Any

from pydantic import Field, HttpUrl, TypeAdapter, field_validator

__all__ = ["Publisher", "PublisherIds"]

from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, Role, SummaryStats


class PublisherIds(OpenAlexBase):
    """External identifiers for a publisher."""

    openalex: str | None = None
    ror: str | None = None
    wikidata: str | None = None

    @field_validator("ror", "wikidata")
    @classmethod
    def validate_urls(cls, v: str | None) -> str | None:
        """Ensure external IDs are valid URLs."""
        if v is None:
            return None
        TypeAdapter(HttpUrl).validate_python(v)
        return v


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

    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None

    @field_validator("homepage_url", "image_url", "image_thumbnail_url")
    @classmethod
    def validate_url_fields(cls, v: str | None) -> str | None:
        """Ensure URL fields contain valid URLs."""
        if v is None:
            return None
        TypeAdapter(HttpUrl).validate_python(v)
        return v

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    sources_api_url: str | None = Field(
        None, description="API URL for publisher's sources"
    )

    @field_validator("sources_api_url")
    @classmethod
    def validate_sources_api_url(cls, v: str | None) -> str | None:
        """Ensure sources API URL is valid."""
        if v is None:
            return None
        TypeAdapter(HttpUrl).validate_python(v)
        return v

    roles: list[Role] = Field(
        default_factory=list, description="Roles in publishing ecosystem"
    )

    @field_validator("roles", mode="before")
    @classmethod
    def sort_roles(cls, v: Any) -> Any:
        """Sort roles so those with higher counts appear last."""
        if isinstance(v, list):
            return sorted(v, key=lambda r: r.get("works_count", 0))
        return v

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

    @property
    def h_index(self) -> int | None:
        """Return h-index from summary stats."""
        return self.summary_stats.h_index if self.summary_stats else None

    @property
    def i10_index(self) -> int | None:
        """Return i10-index from summary stats."""
        return self.summary_stats.i10_index if self.summary_stats else None

    @property
    def two_year_mean_citedness(self) -> float | None:
        """Return the 2-year mean citedness from summary stats."""
        return (
            self.summary_stats.two_year_mean_citedness
            if self.summary_stats
            else None
        )
