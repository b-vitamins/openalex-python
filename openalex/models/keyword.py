"""Keyword model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field

from .base import OpenAlexEntity


class Keyword(OpenAlexEntity):
    """Full keyword model."""

    works_count: int = Field(0, description="Number of works with this keyword")
    cited_by_count: int = Field(0, description="Total citations")

    @property
    def average_citations_per_work(self) -> float | None:
        """Calculate average citations per work."""
        if self.works_count > 0:
            return self.cited_by_count / self.works_count
        return None

    def is_popular(self, threshold: int = 1000) -> bool:
        """Check if keyword is popular based on works count."""
        return self.works_count >= threshold
