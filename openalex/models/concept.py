"""Concept model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field

__all__ = [
    "Concept",
    "ConceptAncestor",
    "ConceptIds",
    "RelatedConcept",
]

from .base import (
    CountsByYear,
    InternationalNames,
    OpenAlexBase,
    OpenAlexEntity,
    SummaryStats,
)


class ConceptIds(OpenAlexBase):
    """External identifiers for a concept."""

    openalex: str | None = None
    wikidata: str | None = None
    wikipedia: str | None = None
    umls_cui: list[str] | None = None
    umls_aui: list[str] | None = None
    mag: str | None = None


class ConceptAncestor(OpenAlexEntity):
    """Concept ancestor in hierarchy."""

    level: int | None = None
    wikidata: str | None = None


class RelatedConcept(ConceptAncestor):
    """Related concept with similarity score."""

    score: float | None = Field(None, ge=0)


class Concept(OpenAlexEntity):
    """Full concept model."""

    wikidata: str | None = None
    level: int | None = Field(0, ge=0, le=5, description="Hierarchy level")

    description: str | None = None

    image_url: str | None = None
    image_thumbnail_url: str | None = None

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    ancestors: list[ConceptAncestor] = Field(
        default_factory=lambda: [], description="Parent concepts in hierarchy"
    )

    related_concepts: list[RelatedConcept] = Field(
        default_factory=lambda: [], description="Similar concepts"
    )

    international: InternationalNames | None = None

    counts_by_year: list[CountsByYear] = Field(
        default_factory=lambda: [],
        description="Yearly publication and citation counts",
    )

    works_api_url: str | None = Field(
        None, description="API URL for concept's works"
    )

    ids: ConceptIds | None = None

    @property
    def is_top_level(self) -> bool:
        """Check if concept is at top level."""
        return self.level == 0

    @property
    def parent_concept(self) -> ConceptAncestor | None:
        """Get immediate parent concept."""
        if not self.ancestors or self.level is None:
            return None

        # Parent is ancestor at level - 1
        for ancestor in self.ancestors:
            if ancestor.level == self.level - 1:
                return ancestor

        return None

    def ancestor_names(self) -> list[str]:
        """Get names of all ancestors."""
        return [a.display_name for a in self.ancestors if a.display_name]

    def works_in_year(self, year: int) -> int:
        """Return number of works published in a specific year."""
        return next(
            (
                year_data.works_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a specific year."""
        return next(
            (
                year_data.cited_by_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def active_years(self) -> list[int]:
        """Return list of years with publication activity."""
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
