"""Full representation of a publication source."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .concept import DehydratedConcept
from .common import CountsByYear, GroupByResult, Meta, SummaryStats


@dataclass(slots=True)
class Source:
    """Journal, conference, or other publication venue."""

    id: str | None = None
    issn_l: str | None = None
    issn: list[str] | None = None
    display_name: str | None = None
    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] | None = None
    works_count: int | None = None
    cited_by_count: int | None = None
    summary_stats: SummaryStats | None = None
    is_oa: bool | None = None
    is_in_doaj: bool | None = None
    is_core: bool | None = None
    type: str | None = None
    homepage_url: str | None = None
    apc_prices: list[SourceApcPrices] | None = None
    apc_usd: int | None = None
    country_code: str | None = None
    societies: list[SourceSocieties] | None = None
    alternate_titles: list[str] | None = None
    abbreviated_title: str | None = None
    x_concepts: list[DehydratedConcept] | None = None
    counts_by_year: CountsByYear | None = None
    works_api_url: str | None = None
    updated_date: datetime | None = None
    created_date: date | None = None
    ids: SourceIds | None = None

    def __post_init__(self) -> None:
        """Normalize iterable attributes to lists."""
        self.issn = list(self.issn) if self.issn is not None else None
        self.host_organization_lineage = (
            list(self.host_organization_lineage)
            if self.host_organization_lineage is not None
            else None
        )
        self.apc_prices = list(self.apc_prices) if self.apc_prices is not None else None
        self.societies = list(self.societies) if self.societies is not None else None
        self.alternate_titles = (
            list(self.alternate_titles) if self.alternate_titles is not None else None
        )
        self.x_concepts = list(self.x_concepts) if self.x_concepts is not None else None


@dataclass(slots=True)
class SourceApcPrices:
    """APC price in a specific currency."""

    price: int | None = None
    currency: str | None = None


@dataclass(slots=True)
class SourceSocieties:
    """Organization membership for a source."""

    url: str | None = None
    organization: str | None = None


@dataclass(slots=True)
class SourceIds:
    """Identifiers used to reference a source across systems."""

    openalex: str
    issn_l: str | None = None
    issn: list[str] | None = None
    mag: int | None = None
    fatcat: str | None = None
    wikidata: str | None = None

    def __post_init__(self) -> None:
        self.issn = list(self.issn) if self.issn is not None else None


class DehydratedSource:
    """Minimal details about a source."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str | None = None,
        issn_l: str | None = None,
        issn: Iterable[str] | None = None,
        is_oa: bool | None = None,
        is_in_doaj: bool | None = None,
        is_core: bool | None = None,
        host_organization: str | None = None,
        host_organization_name: str | None = None,
        host_organization_lineage: Iterable[str] | None = None,
        type: str | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.issn_l = issn_l
        self.issn = list(issn) if issn is not None else None
        self.is_oa = is_oa
        self.is_in_doaj = is_in_doaj
        self.is_core = is_core
        self.host_organization = host_organization
        self.host_organization_name = host_organization_name
        self.host_organization_lineage = (
            list(host_organization_lineage)
            if host_organization_lineage is not None
            else None
        )
        self.type = type


@dataclass(slots=True)
class SourcesList:
    """API response with source records."""

    meta: Meta
    results: Iterable[Source]
    group_by: GroupByResult | None = None

    def __post_init__(self) -> None:
        self.results = list(self.results)
