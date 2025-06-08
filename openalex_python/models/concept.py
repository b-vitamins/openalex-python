"""Model of an OpenAlex concept."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

from .concept_ids import ConceptIds
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .international_names import InternationalNames
from .summary_stats import SummaryStats


class Concept:
    """Detailed information about a research concept."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        wikidata: str | None = None,
        level: int | None = None,
        description: str | None = None,
        image_url: str | None = None,
        image_thumbnail_url: str | None = None,
        works_count: int | None = None,
        cited_by_count: int | None = None,
        summary_stats: SummaryStats | None = None,
        ancestors: Iterable[DehydratedConcept] | None = None,
        related_concepts: Iterable[DehydratedConcept] | None = None,
        international: InternationalNames | None = None,
        counts_by_year: CountsByYear | None = None,
        works_api_url: str | None = None,
        updated_date: datetime | None = None,
        created_date: date | None = None,
        ids: ConceptIds | None = None,
    ) -> None:
        self.id = id
        self.wikidata = wikidata
        self.display_name = display_name
        self.level = level
        self.description = description
        self.image_url = image_url
        self.image_thumbnail_url = image_thumbnail_url
        self.works_count = works_count
        self.cited_by_count = cited_by_count
        self.summary_stats = summary_stats
        self.ancestors = list(ancestors) if ancestors is not None else None
        self.related_concepts = (
            list(related_concepts) if related_concepts is not None else None
        )
        self.international = international
        self.counts_by_year = counts_by_year
        self.works_api_url = works_api_url
        self.updated_date = updated_date
        self.created_date = created_date
        self.ids = ids

