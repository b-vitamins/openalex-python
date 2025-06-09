"""Keyword model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field

from .base import CountsByYear, OpenAlexEntity


class Keyword(OpenAlexEntity):
    """Full keyword model."""

    score: float | None = Field(
        None,
        ge=0,
        description="Relevance score of the keyword",
    )
    works_count: int = Field(
        0,
        ge=0,
        description="Number of works with this keyword",
    )
    cited_by_count: int = Field(
        0,
        ge=0,
        description="Total citations",
    )
    counts_by_year: list[CountsByYear] = Field(
        default_factory=list, description="Yearly statistics"
    )
    works_api_url: str | None = Field(
        None, description="API endpoint for works using this keyword"
    )

    @property
    def average_citations_per_work(self) -> float | None:
        """Calculate average citations per work."""
        if self.works_count > 0:
            return self.cited_by_count / self.works_count
        return None

    def is_popular(self, threshold: int = 1000) -> bool:
        """Determine whether this keyword is considered popular."""

        if self.works_count < threshold:
            return False

        if self.score is None:
            return True

        return self.score >= threshold / 8
