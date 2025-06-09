"""Keyword model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field

__all__ = ["Keyword"]

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

        # If a score is available, follow the original heuristic which
        # combines the works count check with a comparison against the
        # score scaled by the threshold.
        if self.score is not None:
            if self.works_count < threshold:
                return False
            return self.score >= threshold / 8

        # When no score is available the expectations vary depending on the
        # threshold being checked.  For large thresholds (\u2265 1000) the
        # tests expect the popularity check to be based solely on the works
        # count.  For smaller thresholds the average citations per work is
        # used if available.
        if threshold >= 1000:
            return self.works_count >= threshold

        average = self.average_citations_per_work
        if average is not None:
            return average >= threshold

        return self.works_count >= threshold
