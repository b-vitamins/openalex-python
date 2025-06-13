"""Funder model for OpenAlex API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from ..constants import (
    GOVERNMENT_KEYWORDS,
    MINUTES_PER_HOUR,
    SECONDS_PER_MINUTE,
)

__all__ = ["Funder", "FunderIds"]

from pydantic import Field, field_validator

from .base import CountsByYear, OpenAlexBase, OpenAlexEntity, Role, SummaryStats


class FunderIds(OpenAlexBase):
    """External identifiers for a funder."""

    openalex: str | None = None
    ror: str | None = None
    wikidata: str | None = None
    crossref: str | None = None
    doi: str | None = None


class Funder(OpenAlexEntity):
    """Full funder model."""

    alternate_titles: list[str] = Field(
        default_factory=list, description="Alternative names"
    )

    country_code: str | None = Field(None, description="Country code")

    description: str | None = None

    homepage_url: str | None = None
    image_url: str | None = None
    image_thumbnail_url: str | None = None

    ror: str | None = None

    grants_count: int = Field(0, ge=0, description="Number of grants")
    works_count: int = Field(0, ge=0, description="Number of funded works")
    cited_by_count: int = Field(0, ge=0, description="Total citations")

    summary_stats: SummaryStats | None = None

    roles: list[Role] = Field(
        default_factory=list, description="Roles in funding ecosystem"
    )

    counts_by_year: list[CountsByYear] = Field(
        default_factory=list, description="Yearly grant and citation counts"
    )

    ids: FunderIds | None = None

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Ensure country code is two uppercase letters."""
        if v is None:
            return None
        if len(v) != 2 or not v.isalpha():
            msg = "Invalid country code"
            raise ValueError(msg)
        return v.upper()

    @field_validator("updated_date", mode="before")
    @classmethod
    def parse_updated_date(cls, v: Any) -> date | Any:
        """Parse updated_date allowing out-of-range seconds."""
        if v is None or isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v).date()
            except ValueError:
                try:
                    date_part, time_part = v.split("T")
                    time_str, *rest = time_part.split(".")
                    hour, minute, second = (int(x) for x in time_str.split(":"))
                    minute += second // SECONDS_PER_MINUTE
                    second %= SECONDS_PER_MINUTE
                    hour += minute // MINUTES_PER_HOUR
                    minute %= MINUTES_PER_HOUR
                    new_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                    if rest:
                        new_time += f".{rest[0]}"
                    fixed = f"{date_part}T{new_time}"
                    return datetime.fromisoformat(fixed).date()
                except ValueError as exc:  # pragma: no cover - defensive
                    msg = "Invalid datetime format"
                    raise ValueError(msg) from exc
        return v

    @property
    def funding_per_work(self) -> float | None:
        """Calculate average grants per work."""
        if self.works_count > 0:
            return self.grants_count / self.works_count
        return None

    def is_government_funder(self) -> bool:
        """Check if funder is government-based."""
        name_lower = self.display_name.lower()
        return any(keyword in name_lower for keyword in GOVERNMENT_KEYWORDS)

    def works_in_year(self, year: int) -> int:
        """Return number of works funded in a specific year."""
        return next(
            (
                year_data.works_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def citations_in_year(self, year: int) -> int:
        """Return citation count for a specific year."""
        return next(
            (
                year_data.cited_by_count
                for year_data in self.counts_by_year
                if year_data.year == year
            ),
            0,
        )

    def active_years(self) -> list[int]:
        """Return list of years with grant activity."""
        return sorted(
            [y.year for y in self.counts_by_year if y.works_count > 0]
        )

    @property
    def h_index(self) -> int | None:
        """Return h-index from summary stats."""
        return self.summary_stats.h_index if self.summary_stats else None

    @property
    def i10_index(self) -> int | None:
        """Return i10-index from summary stats."""
        return self.summary_stats.i10_index if self.summary_stats else None
