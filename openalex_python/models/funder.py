"""Representation of a funding organization."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

from .common import CountsByYear, GroupByResult, Meta, Role, SummaryStats


class Funder:
    """Full details for a funder."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        alternate_titles: Iterable[str] | None = None,
        country_code: str | None = None,
        description: str | None = None,
        homepage_url: str | None = None,
        image_url: str | None = None,
        image_thumbnail_url: str | None = None,
        grants_count: int | None = None,
        works_count: int | None = None,
        cited_by_count: int | None = None,
        summary_stats: SummaryStats | None = None,
        roles: Iterable[Role] | None = None,
        counts_by_year: CountsByYear | None = None,
        updated_date: datetime | None = None,
        created_date: date | None = None,
        ids: FunderIds | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.alternate_titles = list(alternate_titles) if alternate_titles else None
        self.country_code = country_code
        self.description = description
        self.homepage_url = homepage_url
        self.image_url = image_url
        self.image_thumbnail_url = image_thumbnail_url
        self.grants_count = grants_count
        self.works_count = works_count
        self.cited_by_count = cited_by_count
        self.summary_stats = summary_stats
        self.roles = list(roles) if roles is not None else None
        self.counts_by_year = counts_by_year
        self.updated_date = updated_date
        self.created_date = created_date
        self.ids = ids


class DehydratedFunder:
    """Basic funder details."""

    def __init__(self, *, id: str, display_name: str) -> None:
        self.id = id
        self.display_name = display_name


class FunderIds:
    """Different identifier schemes used for a funder."""

    def __init__(
        self,
        *,
        openalex: str,
        ror: str | None = None,
        wikidata: str | None = None,
        crossref: str | None = None,
        doi: str | None = None,
    ) -> None:
        self.openalex = openalex
        self.ror = ror
        self.wikidata = wikidata
        self.crossref = crossref
        self.doi = doi


class FundersList:
    """List of funders returned by the API."""

    def __init__(
        self,
        *,
        meta: Meta,
        results: Iterable[Funder],
        group_by: GroupByResult | None = None,
    ) -> None:
        self.meta = meta
        self.results = list(results)
        self.group_by = group_by
