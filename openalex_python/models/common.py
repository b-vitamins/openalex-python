"""Common shared data models."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(slots=True)
class CountsByYearInner:
    """Counts of works and citations for a particular year."""

    year: int
    works_count: int | None = None
    cited_by_count: int | None = None


@dataclass(slots=True)
class CountsByYear:
    """Container for yearly count data."""

    results: Iterable[CountsByYearInner]

    def __post_init__(self) -> None:
        self.results = list(self.results)


class ErrorResponse:
    """Represents an error returned by the API."""

    def __init__(self, *, error: str, message: str) -> None:
        self.error = error
        self.message = message


class Geo:
    """Basic geographic metadata."""

    def __init__(
        self,
        *,
        city: str | None = None,
        geonames_city_id: str | None = None,
        region: str | None = None,
        country_code: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        self.city = city
        self.geonames_city_id = geonames_city_id
        self.region = region
        self.country_code = country_code
        self.country = country
        self.latitude = latitude
        self.longitude = longitude


@dataclass(slots=True)
class GroupByResultInner:
    """Item returned from a group-by aggregation."""

    key: str
    key_display_name: str
    count: int


class GroupByResult:
    """Collection of grouped results."""

    def __init__(self, buckets: Iterable[GroupByResultInner] | None = None) -> None:
        self.buckets = list(buckets) if buckets is not None else []


@dataclass(slots=True)
class InternationalNames:
    """Display names keyed by language code."""

    display_name: dict[str, str] | None = None


@dataclass(slots=True)
class Meta:
    """Pagination and performance information."""

    count: int
    db_response_time_ms: int
    page: int
    per_page: int
    groups_count: int | None = None
    next_cursor: str | None = None


@dataclass(slots=True)
class Role:
    """Association role with counts."""

    role: str
    id: str
    works_count: int


@dataclass(slots=True)
class SummaryStats:
    """Basic citation metrics."""

    two_year_mean_citedness: float | None = None
    h_index: int | None = None
    i10_index: int | None = None
