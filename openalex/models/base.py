"""Base models and common types for OpenAlex entities."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    TypeAdapter,
    field_serializer,
    field_validator,
)

from ..constants import FILTER_DEFAULT_PER_PAGE, FIRST_PAGE

__all__ = [
    "AutocompleteResult",
    "CountsByYear",
    "DehydratedEntity",
    "EntityType",
    "Geo",
    "GroupByResult",
    "InternationalNames",
    "ListResult",
    "Meta",
    "OpenAlexBase",
    "OpenAlexEntity",
    "Role",
    "SummaryStats",
]


class EntityType(str, Enum):
    """OpenAlex entity types."""

    AUTHOR = "author"
    CONCEPT = "concept"
    FUNDER = "funder"
    INSTITUTION = "institution"
    KEYWORD = "keyword"
    PUBLISHER = "publisher"
    SOURCE = "source"
    TOPIC = "topic"
    WORK = "work"


class OpenAlexBase(BaseModel):
    """Base model for all OpenAlex entities."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_serializer("*", when_used="json")
    def _serialize(self, v: Any) -> str | Any:
        if isinstance(v, datetime | date | HttpUrl):
            return str(v)
        return v


class OpenAlexEntity(OpenAlexBase):
    """Base model for OpenAlex entities with common fields."""

    id: str = Field(..., description="OpenAlex ID")
    display_name: str = Field(..., description="Display name")
    created_date: date | None = Field(None, description="Creation date")
    updated_date: date | None = Field(None, description="Last update date")

    @field_validator("updated_date", mode="before")
    @classmethod
    def parse_updated_date(cls, v: Any) -> date | Any:
        """Parse updated_date string to date."""
        if isinstance(v, date) or v is None:
            return v
        try:
            return date.fromisoformat(v.split("T")[0])
        except Exception:
            return v

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure ID is a valid URL."""
        TypeAdapter(HttpUrl).validate_python(v)
        return v

    @field_validator("created_date", mode="before")
    @classmethod
    def parse_created_date(cls, v: Any) -> date | Any:
        """Parse created_date string to date."""
        if isinstance(v, date) or v is None:
            return v
        try:
            return date.fromisoformat(v)
        except Exception:
            return v


class DehydratedEntity(OpenAlexBase):
    """Base model for dehydrated (minimal) entities."""

    id: str = Field(..., description="OpenAlex ID")
    display_name: str | None = Field(None, description="Display name")


class CountsByYear(OpenAlexBase):
    """Model for yearly count data."""

    year: int = Field(..., description="Year")
    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Citation count")


class SummaryStats(OpenAlexBase):
    """Summary statistics for an entity."""

    two_year_mean_citedness: float | None = Field(
        None, alias="2yr_mean_citedness"
    )
    h_index: int | None = Field(None, alias="h_index")
    i10_index: int | None = Field(None, alias="i10_index")


class Geo(OpenAlexBase):
    """Geographic location information."""

    city: str | None = None
    geonames_city_id: str | None = None
    region: str | None = None
    country_code: str | None = None
    country: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class InternationalNames(OpenAlexBase):
    """International names for an entity."""

    display_name: dict[str, str] = Field(default_factory=dict)
    description: dict[str, str] | None = None


class Role(OpenAlexBase):
    """Role information."""

    role: str
    id: str
    works_count: int = 0


class Meta(OpenAlexBase):
    """Metadata for API responses."""

    count: int = Field(..., description="Total count of results")
    db_response_time_ms: int = Field(..., description="Database response time")
    page: int = Field(FIRST_PAGE, description="Current page")
    per_page: int = Field(
        FILTER_DEFAULT_PER_PAGE, description="Results per page"
    )
    groups_count: int | None = Field(None, description="Number of groups")
    next_cursor: str | None = Field(None, description="Cursor for next page")


class GroupByResult(OpenAlexBase):
    """Result of a group-by operation."""

    key: str
    key_display_name: str | None = None
    count: int

    def __repr__(self) -> str:
        """Return readable representation."""
        return (
            f"<GroupByResult("
            f"key='{self.key}', "
            f"count={self.count}"
            f")>"
        )


T = TypeVar("T")


class ListResult(OpenAlexBase, Generic[T]):
    """Generic list result container."""

    meta: Meta
    results: list[T] = Field(default_factory=list)
    group_by: list[GroupByResult] | None = None

    @property
    def groups(self) -> list[GroupByResult] | None:
        """Alias for ``group_by`` for backward compatibility."""
        return self.group_by

    def __len__(self) -> int:
        """Return the number of results."""
        return len(self.results)

    def iter_results(self) -> Iterator[T]:
        """Iterate over contained results."""
        return iter(self.results)

    def __getitem__(self, index: int) -> T:
        """Get result at ``index``."""
        return self.results[index]

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        """Truthiness based on contained results."""
        return bool(self.results)

    def __repr__(self) -> str:  # pragma: no cover - for debugging only
        return f"<ListResult {len(self)} results>"


class AutocompleteResult(OpenAlexBase):
    """Autocomplete result item."""

    id: str
    display_name: str
    entity_type: EntityType | None = None
    hint: str | None = None
    cited_by_count: int | None = None
    works_count: int | None = None
    external_id: str | None = None
    filter_key: str | None = None
