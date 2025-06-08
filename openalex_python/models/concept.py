"""Model of an OpenAlex concept."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .common import (
    CountsByYear,
    GroupByResult,
    InternationalNames,
    Meta,
    SummaryStats,
)


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


class DehydratedConcept:
    """Core information about a concept."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        level: int | None = None,
        score: float | None = None,
        wikidata: str | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.level = level
        self.score = score
        self.wikidata = wikidata


@dataclass(slots=True)
class ConceptIds:
    """Different identifier schemes used for a concept."""

    openalex: str
    wikidata: str | None = None
    wikipedia: str | None = None
    umls_cui: Iterable[str] | None = None
    umls_aui: Iterable[str] | None = None
    mag: int | None = None

    def __post_init__(self) -> None:
        if self.umls_cui is not None:
            self.umls_cui = list(self.umls_cui)
        if self.umls_aui is not None:
            self.umls_aui = list(self.umls_aui)


@dataclass(slots=True)
class ConceptsList:
    """A list of concepts returned with metadata."""

    meta: Meta
    results: Iterable[Concept]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)

