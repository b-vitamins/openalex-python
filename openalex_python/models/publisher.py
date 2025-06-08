"""Full representation of a publisher."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .counts_by_year import CountsByYear
from .publisher_ids import PublisherIds
from .role import Role
from .summary_stats import SummaryStats


@dataclass(slots=True)
class Publisher:
    """Detailed publisher metadata."""

    id: str
    display_name: str
    alternate_titles: list[str] | None = None
    country_codes: list[str] | None = None
    hierarchy_level: int | None = None
    parent_publisher: str | None = None
    lineage: list[str] | None = None
    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    sources_api_url: str | None = None
    roles: list[Role] | None = None
    counts_by_year: CountsByYear | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: PublisherIds | None = None

    def __post_init__(self) -> None:
        """Normalize iterable attributes to lists."""
        self.alternate_titles = (
            list(self.alternate_titles) if self.alternate_titles is not None else None
        )
        self.country_codes = (
            list(self.country_codes) if self.country_codes is not None else None
        )
        self.lineage = list(self.lineage) if self.lineage is not None else None
        self.roles = list(self.roles) if self.roles is not None else None
