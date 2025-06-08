"""Full representation of an institution."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .associated_institution import AssociatedInstitution
from .counts_by_year import CountsByYear
from .dehydrated_concept import DehydratedConcept
from .geo import Geo
from .institution_ids import InstitutionIds
from .international_names import InternationalNames
from .repository import Repository
from .role import Role
from .summary_stats import SummaryStats


@dataclass(slots=True)
class Institution:
    """Detailed institution metadata."""

    id: str
    display_name: str
    ror: str | None = None
    display_name_alternatives: Iterable[str] | None = None
    display_name_acronyms: Iterable[str] | None = None
    country_code: str | None = None
    type: str | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    geo: Geo | None = None
    associated_institutions: list[AssociatedInstitution] | None = None
    repositories: list[Repository] | None = None
    lineage: list[str] | None = None
    is_super_system: bool | None = None
    international: InternationalNames | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    roles: list[Role] | None = None
    x_concepts: list[DehydratedConcept] | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: InstitutionIds | None = None

    def __post_init__(self) -> None:
        """Normalize iterable attributes to lists."""
        self.display_name_alternatives = (
            list(self.display_name_alternatives)
            if self.display_name_alternatives is not None
            else None
        )
        self.display_name_acronyms = (
            list(self.display_name_acronyms)
            if self.display_name_acronyms is not None
            else None
        )
        self.associated_institutions = (
            list(self.associated_institutions)
            if self.associated_institutions is not None
            else None
        )
        self.repositories = (
            list(self.repositories) if self.repositories is not None else None
        )
        self.lineage = list(self.lineage) if self.lineage is not None else None
        self.roles = list(self.roles) if self.roles is not None else None
        self.x_concepts = list(self.x_concepts) if self.x_concepts is not None else None
