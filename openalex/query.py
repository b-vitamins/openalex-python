"""Fluent query builder for OpenAlex."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .config import OpenAlexConfig
    from .entities import AsyncBaseEntity, BaseEntity
from .models import BaseFilter, GroupByResult, ListResult
from .utils.pagination import MAX_PER_PAGE, Paginator

__all__ = [
    "Query",
    "gt_",
    "lt_",
    "not_",
    "or_",
]

T = TypeVar("T")
F = TypeVar("F", bound=BaseFilter)


class or_(dict[str, Any]):  # noqa: N801
    """Container to mark a filter dictionary for OR combination."""


@dataclass(slots=True)
class _LogicalExpression:
    """Base class for logical expressions."""

    value: Any
    token: ClassVar[str] = ""

    def __str__(self) -> str:
        return f"{self.token}{self.value}"


class not_(_LogicalExpression):  # noqa: N801
    """Logical NOT expression."""

    token = "!"


class gt_(_LogicalExpression):  # noqa: N801
    """Greater than expression."""

    token = ">"


class lt_(_LogicalExpression):  # noqa: N801
    """Less than expression."""

    token = "<"


class Query(Generic[T, F]):
    """Fluent interface for building API queries."""

    __slots__ = ("entity", "params")

    def __init__(
        self,
        entity: BaseEntity[T, F],
        params: dict[str, Any] | None = None,
    ) -> None:
        self.entity = entity
        self.params: dict[str, Any] = params or {}

    def __getitem__(self, record_id: str | list[str]) -> T | ListResult[T]:
        """Get entity by ID or list of IDs."""
        if isinstance(record_id, list):
            return self.filter(openalex_id=record_id).get(
                per_page=len(record_id)
            )
        return self.entity.get(record_id)

    # internal helper
    def _clone(self, **updates: Any) -> Query[T, F]:
        """Return a new :class:`Query` with updated parameters."""
        params = self.params.copy()
        filt = updates.pop("filter", None)

        if filt is not None:
            current = params.get("filter", {})
            if (
                isinstance(current, dict)
                and isinstance(filt, dict)
                and not isinstance(filt, or_)
            ):
                current.update(filt)
                params["filter"] = current
            else:
                params["filter"] = filt

        params.update(updates)
        return Query(self.entity, params)

    def _merge_filter_dict(
        self,
        current: dict[str, Any],
        new: dict[str, Any],
        operation: str = "and",
    ) -> dict[str, Any]:
        """Merge filter dictionaries based on operation type."""
        if operation == "or":
            return or_(current | new)
        return current | new

    def _apply_logical_operation(
        self, filter_dict: dict[str, Any], operation: type[_LogicalExpression]
    ) -> dict[str, Any]:
        """Apply a logical operation to all values in a filter dict."""
        return {k: operation(v) for k, v in filter_dict.items()}

    # --- builder methods -------------------------------------------------
    def filter(self, **kwargs: Any) -> Query[T, F]:
        """Add filter parameters."""
        return self._clone(filter=kwargs)

    def search(self, query: str) -> Query[T, F]:
        """Add a search term."""
        return self._clone(search=query)

    def sort(self, **kwargs: str) -> Query[T, F]:
        """Add sorting parameters."""
        sort_parts = [f"{k}:{v}" for k, v in kwargs.items()]
        return self._clone(sort=",".join(sort_parts))

    def group_by(self, key: str) -> Query[T, F]:
        """Group results by ``key``."""
        return self._clone(**{"group-by": key})

    def select(self, fields: list[str] | str) -> Query[T, F]:
        """Select specific fields."""
        return self._clone(select=fields)

    def sample(self, n: int, seed: int | None = None) -> Query[T, F]:
        """Sample random results."""
        params = {"sample": n}
        if seed is not None:
            params["seed"] = seed
        return self._clone(**params)

    def filter_or(self, **kwargs: Any) -> Query[T, F]:
        """Add OR filter parameters."""
        current = self.params.get("filter", {})
        if isinstance(current, dict):
            new_filter = self._merge_filter_dict(current, kwargs, "or")
            return self._clone(filter=new_filter)
        return self._clone(filter=or_(kwargs))

    def filter_not(self, **kwargs: Any) -> Query[T, F]:
        """Add NOT filter parameters."""
        not_filters = self._apply_logical_operation(kwargs, not_)
        return self.filter(**not_filters)

    def filter_gt(self, **kwargs: Any) -> Query[T, F]:
        """Add greater than filter parameters."""
        gt_filters = self._apply_logical_operation(kwargs, gt_)
        return self.filter(**gt_filters)

    def filter_lt(self, **kwargs: Any) -> Query[T, F]:
        """Add less than filter parameters."""
        lt_filters = self._apply_logical_operation(kwargs, lt_)
        return self.filter(**lt_filters)

    def search_filter(self, **kwargs: Any) -> Query[T, F]:
        """Add search filter parameters (search within specific fields)."""
        search_filters = {f"{k}.search": v for k, v in kwargs.items()}
        return self.filter(**search_filters)

    # --- execution methods -----------------------------------------------
    def get(self, **kwargs: Any) -> ListResult[T]:
        """Execute query and return results (alias for list())."""
        params = {**self.params, **kwargs}
        filter_param = params.pop("filter", None)
        return self.entity.list(filter=filter_param, **params)

    def list(self, **kwargs: Any) -> ListResult[T]:
        """Alias for :meth:`get`."""
        return self.get(**kwargs)

    def paginate(
        self,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> Paginator[T]:
        """Return a paginator for this query."""
        params = {**self.params, **kwargs}
        filter_param = params.pop("filter", None)
        return self.entity.paginate(
            filter=filter_param,
            per_page=per_page,
            max_results=max_results,
            **params,
        )

    def count(self) -> int:
        """Get count of results without fetching them."""
        result = self.get(per_page=1)
        return result.meta.count

    def random(self) -> T:
        """Get a random entity."""
        return self.entity.random()

    def autocomplete(self, query: str, **kwargs: Any) -> ListResult[Any]:
        """Autocomplete search."""
        return self.entity.autocomplete(query, **kwargs)

    def __repr__(self) -> str:
        """String representation of query."""
        parts = [
            (
                f"{k}={self.params[k]!r}"
                if k == "search"
                else f"{k}={self.params[k]}"
            )
            for k in ("filter", "search", "sort", "select")
            if k in self.params
        ]

        params_str = ", ".join(parts) if parts else "no filters"
        return f"<Query({self.entity.__class__.__name__}) {params_str}>"


class AsyncQuery(Generic[T, F]):
    """Async query builder for OpenAlex entities."""

    def __init__(
        self,
        entity: AsyncBaseEntity[T, F],
        model_class: type[T],
        config: OpenAlexConfig,
    ) -> None:
        self._entity = entity
        self._model_class = model_class
        self._config = config
        self._params: dict[str, Any] = {}

    def filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        current = self._params.get("filter")
        if isinstance(current, dict):
            current.update(kwargs)
            self._params["filter"] = current
        else:
            self._params["filter"] = kwargs
        return self

    def search(self, query: str) -> AsyncQuery[T, F]:
        self._params["search"] = query
        return self

    def search_filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        if "filter" not in self._params:
            self._params["filter"] = {}
        for field, value in kwargs.items():
            self._params["filter"][f"{field}.search"] = value
        return self

    def sort(self, field: str, order: str = "desc") -> AsyncQuery[T, F]:
        self._params["sort"] = f"{field}:{order}"
        return self

    def group_by(self, field: str) -> AsyncQuery[T, F]:
        self._params["group_by"] = field
        return self

    def select(self, *fields: str) -> AsyncQuery[T, F]:
        self._params["select"] = ",".join(fields)
        return self

    async def get(
        self,
        page: int | None = None,
        per_page: int | None = None,
    ) -> ListResult[T] | GroupByResult:
        params = self._params.copy()
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        data = await self._entity.get_list(params=params)

        if "group_by" in self._params:
            return GroupByResult(**data)

        return ListResult[T](
            meta=data.get("meta", {}),
            results=[
                self._model_class(**item) for item in data.get("results", [])
            ],
        )

    async def all(self) -> AsyncIterator[T]:
        page = 1
        while True:
            results = await self.get(page=page)

            if isinstance(results, GroupByResult):
                raise ValueError("Cannot iterate over grouped results")

            for item in results.results:
                yield item

            if not results.results:
                break

            page += 1

    async def count(self) -> int:
        results = await self.get(per_page=1)

        if isinstance(results, GroupByResult):
            return 1

        return results.meta.count or 0

    async def first(self) -> T | None:
        results = await self.get(per_page=1)

        if isinstance(results, GroupByResult):
            raise ValueError("Cannot get first item from grouped results")

        return results.results[0] if results.results else None
