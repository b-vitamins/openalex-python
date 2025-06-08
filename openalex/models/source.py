"""Source model for OpenAlex API."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import Field, HttpUrl

from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, SummaryStats

if TYPE_CHECKING:
    from .work import DehydratedConcept


class SourceType(str, Enum):
    """Types of sources."""

    JOURNAL = "journal"
    REPOSITORY = "repository"
    CONFERENCE = "conference"
    EBOOK_PLATFORM = "ebook-platform"
    BOOK_SERIES = "book-series"
    OTHER = "other"


class APCPrice(OpenAlexBase):
    """Article Processing Charge price."""

    price: int | None = None
    currency: str | None = None


class Society(OpenAlexEntity):
    """Society affiliation."""

    url: HttpUrl | None = None
    organization: str | None = None


class SourceIds(OpenAlexBase):
    """External identifiers for a source."""

    openalex: str | None = None
    issn_l: str | None = None
    issn: list[str] | None = None
    mag: int | None = None
    fatcat: str | None = None
    wikidata: HttpUrl | None = None


class Source(OpenAlexEntity):
    """Full source model."""

    issn_l: str | None = Field(None, description="Linking ISSN")
    issn: list[str] = Field(default_factory=list, description="All ISSNs")

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
    is_core: bool | None = Field(None, description="Is CORE source")

    type: SourceType | None = None

    homepage_url: HttpUrl | None = None

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

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list,
        description="Yearly publication and citation counts",
    )

    works_api_url: HttpUrl | None = Field(
        None, description="API URL for source's works"
    )

    ids: SourceIds | None = None

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
    def has_apc(self) -> bool:
        """Check if source has article processing charges."""
        return bool(self.apc_prices) or self.apc_usd is not None

    def get_apc_in_currency(self, currency: str) -> int | None:
        """Get APC in specific currency if available."""
        for price in self.apc_prices:
            if price.currency and price.currency.upper() == currency.upper():
                return price.price
        return None

    def all_issns(self) -> list[str]:
        """Get all ISSNs including linking ISSN."""
        issns = self.issn.copy() if self.issn else []
        if self.issn_l and self.issn_l not in issns:
            issns.insert(0, self.issn_l)
        return issns


from .work import DehydratedConcept  # noqa: E402,TC001

Source.model_rebuild()
