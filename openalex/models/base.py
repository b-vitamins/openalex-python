"""Base models and common types for OpenAlex entities."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


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
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            HttpUrl: str,
        },
    )


class OpenAlexEntity(OpenAlexBase):
    """Base model for OpenAlex entities with common fields."""

    id: str = Field(..., description="OpenAlex ID")
    display_name: str = Field(..., description="Display name")
    created_date: date | None = Field(None, description="Creation date")
    updated_date: datetime | None = Field(None, description="Last update date")


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


class Role(OpenAlexBase):
    """Role information."""

    role: str
    id: str
    works_count: int = 0


class Meta(OpenAlexBase):
    """Metadata for API responses."""

    count: int = Field(..., description="Total count of results")
    db_response_time_ms: int = Field(..., description="Database response time")
    page: int = Field(1, description="Current page")
    per_page: int = Field(25, description="Results per page")
    groups_count: int | None = Field(None, description="Number of groups")
    next_cursor: str | None = Field(None, description="Cursor for next page")


class GroupByResult(OpenAlexBase):
    """Result of a group-by operation."""

    key: str
    key_display_name: str | None = None
    count: int


T = TypeVar("T")


class ListResult(OpenAlexBase, Generic[T]):
    """Generic list result container."""

    meta: Meta
    results: list[T] = Field(default_factory=list)
    group_by: list[GroupByResult] | None = None


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
