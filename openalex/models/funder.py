"""Funder model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field, HttpUrl

from .base import CountsByYear, OpenAlexEntity, Role, SummaryStats


class FunderIds(OpenAlexEntity):
    """External identifiers for a funder."""

    openalex: str | None = None
    ror: HttpUrl | None = None
    wikidata: HttpUrl | None = None
    crossref: str | None = None
    doi: HttpUrl | None = None


class Funder(OpenAlexEntity):
    """Full funder model."""

    alternate_titles: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    country_code: str | None = Field(None, description="Country code")

    description: str | None = None

    homepage_url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    image_thumbnail_url: HttpUrl | None = None

    grants_count: int = Field(0, description="Number of grants")
    works_count: int = Field(0, description="Number of funded works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    roles: list[Role] = Field(
        default_factory=list, description="Roles in funding ecosystem"
    )

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list, description="Yearly grant and citation counts"
    )

    ids: FunderIds | None = None

    @property
    def funding_per_work(self) -> float | None:
        """Calculate average grants per work."""
        if self.works_count > 0:
            return self.grants_count / self.works_count
        return None

    def is_government_funder(self) -> bool:
        """Check if funder is government-based."""
        gov_keywords = [
            "national",
            "federal",
            "ministry",
            "department",
            "agency",
        ]
        name_lower = self.display_name.lower()
        return any(keyword in name_lower for keyword in gov_keywords)
