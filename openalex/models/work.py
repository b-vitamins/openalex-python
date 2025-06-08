"""Query filters and parameters for OpenAlex API."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class GroupBy(str, Enum):
    """Common group-by options."""

    PUBLICATION_YEAR = "publication_year"
    TYPE = "type"
    OPEN_ACCESS_STATUS = "oa_status"
    AUTHORSHIPS_INSTITUTIONS_COUNTRY_CODE = (
        "authorships.institutions.country_code"
    )
    INSTITUTIONS_TYPE = "institutions.type"
    CITED_BY_COUNT = "cited_by_count"
    WORKS_COUNT = "works_count"


class BaseFilter(BaseModel):
    """Base class for query filters."""

    search: str | None = Field(None, description="Search query")
    filter: dict[str, Any] | str | None = Field(
        None, description="Filter expression"
    )
    sort: str | None = Field(None, description="Sort field")
    group_by: str | GroupBy | None = Field(None, description="Group by field")
    page: int | None = Field(None, ge=1, le=10000, description="Page number")
    per_page: int | None = Field(
        None, ge=1, le=200, description="Results per page"
    )
    cursor: str | None = Field(None, description="Pagination cursor")
    sample: int | None = Field(None, ge=1, description="Random sample size")
    seed: int | None = Field(None, description="Random seed")
    select: list[str] | str | None = Field(None, description="Fields to select")

    @field_validator("filter", mode="before")
    @classmethod
    def validate_filter(cls, v: Any) -> dict[str, Any] | str | None:
        """Validate and normalize filter parameter."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            return v
        msg = "Filter must be a string or dictionary"
        raise ValueError(msg)

    @field_validator("select", mode="before")
    @classmethod
    def validate_select(cls, v: Any) -> list[str] | str | None:
        """Validate select parameter."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return v
        msg = "Select must be a string or list of strings"
        raise ValueError(msg)

    def to_params(self) -> dict[str, Any]:
        """Convert to API query parameters."""
        params = {}

        for field_name, field_value in self.model_dump(
            exclude_none=True
        ).items():
            if field_name == "filter" and isinstance(field_value, dict):
                # Convert filter dict to API format
                params["filter"] = self._build_filter_string(field_value)
            elif field_name == "select" and isinstance(field_value, list):
                params["select"] = ",".join(field_value)
            elif field_name == "group_by":
                params["group-by"] = field_value
            elif field_name == "per_page":
                params["per-page"] = field_value
            else:
                params[field_name] = field_value

        return params

    def _build_filter_string(self, filters: dict[str, Any]) -> str:
        """Build filter string from dictionary."""
        filter_parts = []

        for key, value in filters.items():
            if value is None:
                continue

            if isinstance(value, bool):
                filter_parts.append(f"{key}:{str(value).lower()}")
            elif isinstance(value, list | tuple):
                values = "|".join(str(v) for v in value)
                filter_parts.append(f"{key}:{values}")
            elif isinstance(value, date | datetime):
                filter_parts.append(f"{key}:{value.isoformat()}")
            else:
                filter_parts.append(f"{key}:{value}")

        return ",".join(filter_parts)


class WorksFilter(BaseFilter):
    """Filters specific to works endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        regex="^(publication_date|cited_by_count|relevance_score)(:(asc|desc))?$",
    )

    def with_publication_year(self, year: int | list[int]) -> WorksFilter:
        """Filter by publication year."""
        if isinstance(year, int):
            year = [year]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["publication_year"] = year
        return self.model_copy(update={"filter": current_filter})

    def with_type(self, work_type: str | list[str]) -> WorksFilter:
        """Filter by work type."""
        if isinstance(work_type, str):
            work_type = [work_type]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["type"] = work_type
        return self.model_copy(update={"filter": current_filter})

    def with_open_access(self, is_oa: bool = True) -> WorksFilter:
        """Filter by open access status."""
        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["is_oa"] = is_oa
        return self.model_copy(update={"filter": current_filter})


class AuthorsFilter(BaseFilter):
    """Filters specific to authors endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        regex="^(display_name|cited_by_count|works_count|relevance_score)(:(asc|desc))?$",
    )


class InstitutionsFilter(BaseFilter):
    """Filters specific to institutions endpoint."""

    sort: str | None = Field(
        None,
        description="Sort field",
        regex="^(display_name|cited_by_count|works_count|relevance_score)(:(asc|desc))?$",
    )

    def with_country(self, country_code: str | list[str]) -> InstitutionsFilter:
        """Filter by country code."""
        if isinstance(country_code, str):
            country_code = [country_code]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["country_code"] = country_code
        return self.model_copy(update={"filter": current_filter})

    def with_type(
        self, institution_type: str | list[str]
    ) -> InstitutionsFilter:
        """Filter by institution type."""
        if isinstance(institution_type, str):
            institution_type = [institution_type]

        current_filter = self.filter or {}
        if isinstance(current_filter, str):
            current_filter = {"raw": current_filter}

        current_filter["type"] = institution_type
        return self.model_copy(update={"filter": current_filter})
