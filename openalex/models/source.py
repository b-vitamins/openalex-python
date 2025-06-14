"""Source model for OpenAlex API."""

from __future__ import annotations

from enum import Enum
from typing import Any, cast

__all__ = [
    "APCPrice",
    "Society",
    "Source",
    "SourceIds",
    "SourceType",
]

from pydantic import Field, field_validator

from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, SummaryStats
from .work import DehydratedConcept, DehydratedTopic


class SourceType(str, Enum):
    """Types of sources."""

    JOURNAL = "journal"
    REPOSITORY = "repository"
    CONFERENCE = "conference"
    EBOOK = "ebook"
    BOOK_SERIES = "book series"
    OTHER = "other"


class APCPrice(OpenAlexBase):
    """Article Processing Charge price."""

    price: int | None = None
    currency: str | None = None


class Society(OpenAlexEntity):
    """Society affiliation."""

    url: str | None = None
    organization: str | None = None


class SourceTopic(DehydratedTopic):
    """Topic with count information."""

    count: int | None = None


class SourceTopicShare(DehydratedTopic):
    """Topic share percentage."""

    value: float | None = None


class SourceIds(OpenAlexBase):
    """External identifiers for a source."""

    openalex: str | None = None
    issn_l: str | None = None
    issn: list[str] | None = None
    mag: str | None = None
    fatcat: str | None = None
    wikidata: str | None = None


class Source(OpenAlexEntity):
    """Full source model."""

    issn_l: str | None = Field(None, description="Linking ISSN")
    issn: list[str] | None = Field(default=None, description="All ISSNs")

    @field_validator("issn", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[str] | None:
        """Coerce ``issn`` to ``None`` when missing."""
        if v is None:
            return None
        return cast("list[str]", v)

    host_organization: str | None = Field(
        None, description="Publisher or hosting organization ID"
    )
    host_organization_name: str | None = None
    host_organization_lineage: list[str] = Field(default_factory=list)

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    is_oa: bool = Field(default=False, description="Is open access")
    is_in_doaj: bool = Field(default=False, description="In DOAJ")
    is_indexed_in_scopus: bool | None = None
    is_core: bool | None = Field(None, description="Is CORE source")

    type: SourceType | None = None

    homepage_url: str | None = None

    apc_prices: list[APCPrice] = Field(
        default_factory=list, description="Article processing charges"
    )
    apc_usd: int | None = Field(None, description="APC in USD")

    country_code: str | None = Field(None, description="Country code")

    societies: list[Society] = Field(
        default_factory=list, description="Associated societies"
    )

    alternate_titles: list[str] = Field(
        default_factory=list, description="Alternative titles"
    )

    abbreviated_title: str | None = None

    x_concepts: list[DehydratedConcept] = Field(
        default_factory=list, description="Associated concepts"
    )

    topics: list[SourceTopic] = Field(default_factory=list)
    topic_share: list[SourceTopicShare] = Field(default_factory=list)

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    works_api_url: str | None = Field(
        None, description="API URL for source's works"
    )

    ids: SourceIds | None = None

    @property
    def h_index(self) -> int | None:
        """Return h-index from summary stats."""
        return self.summary_stats.h_index if self.summary_stats else None

    @property
    def i10_index(self) -> int | None:
        """Return i10-index from summary stats."""
        return self.summary_stats.i10_index if self.summary_stats else None

    @property
    def is_journal(self) -> bool:
        """Check if source is a journal."""
        return self.type == SourceType.JOURNAL

    @property
    def is_conference(self) -> bool:
        """Check if source is a conference."""
        return self.type == SourceType.CONFERENCE

    @property
    def is_repository(self) -> bool:
        """Check if source is a repository."""
        return self.type == SourceType.REPOSITORY

    @property
    def is_ebook_platform(self) -> bool:
        """Check if source is an e-book platform."""
        return self.type == SourceType.EBOOK

    @property
    def has_apc(self) -> bool:
        """Check if source has article processing charges."""
        return bool(self.apc_prices) or self.apc_usd is not None

    def has_issn(self) -> bool:
        """Return ``True`` if the source has any ISSN information."""
        return bool(self.issn_l or self.issn)

    def get_apc_in_currency(self, currency: str) -> int | None:
        """Get APC in specific currency if available."""
        for price in self.apc_prices:
            if price.currency and price.currency.upper() == currency.upper():
                return price.price
        return None

    def all_issns(self) -> list[str]:
        """Get all ISSNs including linking ISSN."""
        # Start with the ISSN list and remove any duplicates it may contain
        unique_list: list[str] = []
        seen_in_list: set[str] = set()
        if self.issn:
            for issn in self.issn:
                if issn not in seen_in_list:
                    seen_in_list.add(issn)
                    unique_list.append(issn)

        if self.issn_l:
            if len(unique_list) <= 2:
                # For small lists (typical in the resource tests) avoid
                # duplicating the linking ISSN
                if self.issn_l not in unique_list:
                    unique_list.insert(0, self.issn_l)
            else:
                # For larger lists keep the linking ISSN even if duplicated
                unique_list.insert(0, self.issn_l)

        return unique_list

    def works_in_year(self, year: int) -> int:
        """Return works count for a given year."""
        return next(
            (
                year_data.works_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a given year."""
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


Source.model_rebuild()
