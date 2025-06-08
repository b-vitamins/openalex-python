"""Concept model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field, HttpUrl

from .base import CountsByYear, InternationalNames, OpenAlexEntity, SummaryStats


class ConceptIds(OpenAlexEntity):
    """External identifiers for a concept."""

    openalex: str | None = None
    wikidata: HttpUrl | None = None
    wikipedia: HttpUrl | None = None
    umls_cui: list[str] | None = None
    umls_aui: list[str] | None = None
    mag: int | None = None


class ConceptAncestor(OpenAlexEntity):
    """Concept ancestor in hierarchy."""

    level: int | None = None
    wikidata: HttpUrl | None = None


class RelatedConcept(ConceptAncestor):
    """Related concept with similarity score."""

    score: float | None = Field(None, ge=0, le=1)


class Concept(OpenAlexEntity):
    """Full concept model."""

    wikidata: HttpUrl | None = None
    level: int | None = Field(None, ge=0, le=5, description="Hierarchy level")

    description: str | None = None

    image_url: HttpUrl | None = None
    image_thumbnail_url: HttpUrl | None = None

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    ancestors: list[ConceptAncestor] = Field(
        default_factory=list, description="Parent concepts in hierarchy"
    )

    related_concepts: list[RelatedConcept] = Field(
        default_factory=list, description="Similar concepts"
    )

    international: InternationalNames | None = None

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    works_api_url: HttpUrl | None = Field(
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
