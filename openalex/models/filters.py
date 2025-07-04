"""Query filters and parameters for OpenAlex API."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, cast

from pydantic import BaseModel, Field, field_validator

from ..constants import FILTER_DEFAULT_PER_PAGE, FIRST_PAGE

__all__ = [
    "BaseFilter",
    "GroupBy",
    "SortOrder",
]


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class GroupBy(str, Enum):
    """Common group-by options."""

    PUBLICATION_YEAR = "publication_year"
    TYPE = "type"
    OPEN_ACCESS_STATUS = "open_access.oa_status"
    AUTHORSHIPS_INSTITUTION = "authorships.institutions.id"
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
    page: int | None = Field(
        default=FIRST_PAGE,
        ge=1,
        le=10000,
        description="Page number",
    )
    per_page: int | None = Field(
        default=FILTER_DEFAULT_PER_PAGE,
        ge=1,
        le=200,
        description="Results per page",
    )
    cursor: str | None = Field(None, description="Pagination cursor")
    sample: int | None = Field(None, ge=1, description="Random sample size")
    seed: int | None = Field(None, description="Random seed")
    select: list[str] | str | None = Field(None, description="Fields to select")

    @field_validator("filter", mode="before")
    @classmethod
    def validate_filter(cls, v: Any) -> dict[str, Any] | str | None:
        if v is None:
            return None
        if isinstance(v, str | dict):
            filter_val: str | dict[str, Any] = cast(str | dict[str, Any], v)
            return filter_val
        msg = "Filter must be a string or dictionary"
        raise ValueError(msg)

    @field_validator("select", mode="before")
    @classmethod
    def validate_select(cls, v: Any) -> list[str] | str | None:
        if v is None:
            return None
        if isinstance(v, str | list):
            select_val: str | list[str] = cast(str | list[str], v)
            return select_val
        msg = "Select must be a string or list of strings"
        raise ValueError(msg)

    def to_params(self, *, include_defaults: bool = True) -> dict[str, Any]:
        params: dict[str, Any] = {}

        exclude: set[str] = set()
        if not include_defaults:
            if "page" not in self.model_fields_set:
                exclude.add("page")
            if "per_page" not in self.model_fields_set:
                exclude.add("per_page")

        for field_name, field_value in self.model_dump(
            exclude_none=True, exclude=exclude
        ).items():
            if field_name == "filter" and isinstance(field_value, dict):
                filter_dict: dict[str, Any] = cast(dict[str, Any], field_value)
                params["filter"] = self._build_filter_string(filter_dict)
            elif field_name == "select" and isinstance(field_value, list):
                select_list: list[str] = cast(list[str], field_value)
                params["select"] = ",".join(select_list)
            elif field_name == "group_by":
                params["group-by"] = field_value
            elif field_name == "per_page":
                params["per-page"] = field_value
            else:
                params[field_name] = field_value

        return params

    def _build_filter_string(self, filters: dict[str, Any]) -> str:
        filter_parts: list[str] = []

        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, bool):
                bool_val: bool = value
                filter_parts.append(f"{key}:{str(bool_val).lower()}")
            elif isinstance(value, list | tuple | set):
                if not value:
                    continue
                value_collection: list[Any] | tuple[Any, ...] | set[Any] = cast(
                    list[Any] | tuple[Any, ...] | set[Any], value
                )
                values = "|".join(str(v) for v in value_collection)
                filter_parts.append(f"{key}:{values}")
            elif isinstance(value, date | datetime):
                filter_parts.append(f"{key}:{value.strftime('%Y-%m-%d')}")
            else:
                filter_parts.append(f"{key}:{value}")

        return ",".join(filter_parts)
