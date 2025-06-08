"""Model of an OpenAlex concept."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .concept_ids import ConceptIds
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .international_names import InternationalNames
from .summary_stats import SummaryStats


@dataclass(slots=True)
class Concept:
    """Detailed information about a research concept."""

    id: str
    display_name: str
    wikidata: str | None = None
    level: int | None = None
    description: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    ancestors: Iterable[DehydratedConcept] | None = None
    related_concepts: Iterable[DehydratedConcept] | None = None
    international: InternationalNames | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: ConceptIds | None = None

    def __post_init__(self) -> None:
        """Convert iterables to lists."""
        if self.ancestors is not None:
            self.ancestors = list(self.ancestors)
        if self.related_concepts is not None:
            self.related_concepts = list(self.related_concepts)

