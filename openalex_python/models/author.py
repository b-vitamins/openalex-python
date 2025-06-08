"""Representation of an author in OpenAlex."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

from .author_affiliations import AuthorAffiliations
from .author_ids import AuthorIds
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .dehydrated_institution import DehydratedInstitution
from .summary_stats import SummaryStats


class Author:
    """Core information about an author."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        orcid: str | None = None,
        display_name_alternatives: Iterable[str] | None = None,
        works_count: int | None = None,
        cited_by_count: int | None = None,
        summary_stats: SummaryStats | None = None,
        affiliations: list[AuthorAffiliations] | None = None,
        last_known_institutions: list[DehydratedInstitution] | None = None,
        x_concepts: list[DehydratedConcept] | None = None,
        counts_by_year: CountsByYear | None = None,
        works_api_url: str | None = None,
        updated_date: datetime | None = None,
        created_date: date | None = None,
        ids: AuthorIds | None = None,
    ) -> None:
        self.id = id
        self.orcid = orcid
        self.display_name = display_name
        self.display_name_alternatives = (
            list(display_name_alternatives) if display_name_alternatives else None
        )
        self.works_count = works_count
        self.cited_by_count = cited_by_count
        self.summary_stats = summary_stats
        self.affiliations = affiliations
        self.last_known_institutions = last_known_institutions
        self.x_concepts = x_concepts
        self.counts_by_year = counts_by_year
        self.works_api_url = works_api_url
        self.updated_date = updated_date
        self.created_date = created_date
        self.ids = ids


