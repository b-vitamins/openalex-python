"""Representation of an author in OpenAlex."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .author_affiliations import AuthorAffiliations
from .author_ids import AuthorIds
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .dehydrated_institution import DehydratedInstitution
from .summary_stats import SummaryStats


@dataclass(slots=True)
class Author:
    """Core information about an author."""

    id: str
    display_name: str
    orcid: str | None = None
    display_name_alternatives: Iterable[str] | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    affiliations: Iterable[AuthorAffiliations] | None = None
    last_known_institutions: Iterable[DehydratedInstitution] | None = None
    x_concepts: Iterable[DehydratedConcept] | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: AuthorIds | None = None

    def __post_init__(self) -> None:
        """Ensure alternative names are stored as a list."""
        if self.display_name_alternatives is not None:
            self.display_name_alternatives = list(self.display_name_alternatives)
        if self.affiliations is not None:
            self.affiliations = list(self.affiliations)
        if self.last_known_institutions is not None:
            self.last_known_institutions = list(self.last_known_institutions)
        if self.x_concepts is not None:
            self.x_concepts = list(self.x_concepts)
