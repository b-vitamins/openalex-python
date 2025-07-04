"""Fluent query builder for OpenAlex."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from .config import OpenAlexConfig
    from .entities import AsyncBaseEntity, BaseEntity
    from .models.base import ListResult
    from .streaming.stream import AsyncStreamingPaginator, StreamingPaginator

from .models import BaseFilter, GroupByResult
from .utils.pagination import MAX_PER_PAGE, AsyncPaginator, Paginator

__all__ = [
    "LogicalExpression",
    "Query",
    "gt_",
    "gte_",
    "lt_",
    "lte_",
    "not_",
    "or_",
]

T = TypeVar("T", bound=BaseModel)
F = TypeVar("F", bound=BaseFilter)


class or_(dict[str, Any]):  # noqa: N801
    """Container to mark a filter dictionary for OR combination."""


@dataclass(slots=True)
class LogicalExpression:
    """Base class for logical expressions."""

    value: Any
    token: ClassVar[str] = ""

    def __str__(self) -> str:
        return f"{self.token}{self.value}"


# Maintain backward compatibility
_LogicalExpression = LogicalExpression


class not_(LogicalExpression):  # noqa: N801
    """Logical NOT expression."""

    token = "!"


class gt_(LogicalExpression):  # noqa: N801
    """Greater than expression."""

    token = ">"


class lt_(LogicalExpression):  # noqa: N801
    """Less than expression."""

    token = "<"


class gte_(LogicalExpression):  # noqa: N801
    """Greater than or equal expression."""

    token = ">="


class lte_(LogicalExpression):  # noqa: N801
    """Less than or equal expression."""

    token = "<="


def _build_list_result(data: dict[str, Any], model: type[T]) -> ListResult[T]:
    """Construct a :class:`ListResult` from raw data using shared logic."""
    from .config import OpenAlexConfig
    from .templates import EntityLogicBase

    # Use the shared parsing logic from templates
    logic = EntityLogicBase[T, Any](config=OpenAlexConfig())
    logic.model_class = model
    return logic.parse_list_response(data)


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
                current_dict: dict[str, Any] = cast(dict[str, Any], current)
                filt_dict: dict[str, Any] = cast(dict[str, Any], filt)
                params["filter"] = self._merge_filters(current_dict, filt_dict)
            else:
                params["filter"] = filt

        params.update(updates)
        return Query(self.entity, params)

    def _merge_filters(
        self,
        current: dict[str, Any] | Any,
        new: dict[str, Any] | Any,
        operation: str = "and",
    ) -> dict[str, Any] | Any:
        """Merge filter dictionaries with proper operator handling."""
        if operation == "or":
            return (
                or_({**current, **new})
                if isinstance(current, dict)
                else or_(new)
            )

        if not isinstance(current, dict) or not isinstance(new, dict):
            if not isinstance(current, dict):
                return new
            merged: dict[str, Any] = {**current, **new}
            return merged

        current_dict: dict[str, Any] = cast(dict[str, Any], current)
        result: dict[str, Any] = current_dict.copy()
        new_dict: dict[str, Any] = cast(dict[str, Any], new)
        for key, value in new_dict.items():
            key_str: str = key
            value_any: Any = value
            if key_str in result:
                existing = result[key_str]
                if isinstance(existing, dict) and isinstance(value_any, dict):
                    existing_dict: dict[str, Any] = cast(
                        dict[str, Any], existing
                    )
                    value_dict: dict[str, Any] = cast(dict[str, Any], value_any)
                    result[key_str] = self._merge_filters(
                        existing_dict, value_dict
                    )
                elif isinstance(existing, tuple):
                    result[key_str] = (*existing, value_any)
                else:
                    result[key_str] = (existing, value_any)
            else:
                result[key_str] = value_any
        return result

    def _apply_logical_operation(
        self, filter_dict: dict[str, Any], operation: type[_LogicalExpression]
    ) -> dict[str, Any]:
        """Apply a logical operation recursively to all filter values."""

        def apply(value: Any) -> Any:
            if isinstance(value, dict):
                value_dict: dict[str, Any] = cast(dict[str, Any], value)
                return {k: apply(v) for k, v in value_dict.items()}
            return operation(value)

        return {k: apply(v) for k, v in filter_dict.items()}

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

    def group_by(self, *keys: str) -> Query[T, F]:
        """Group results by one or more ``keys``."""

        if len(keys) == 1 and isinstance(keys[0], list | tuple):
            keys = tuple(keys[0])

        existing = self.params.get("group_by")
        if existing:
            if isinstance(existing, list):
                new_keys: list[str] = [*existing, *keys]
            else:
                new_keys = [existing, *keys]
        else:
            new_keys = list(keys)

        group_param: str | list[str] = (
            new_keys[0] if len(new_keys) == 1 else new_keys
        )

        return self._clone(group_by=group_param)

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
            current_dict: dict[str, Any] = cast(dict[str, Any], current)
            new_filter = self._merge_filters(current_dict, kwargs, "or")
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

    def filter_gte(self, **kwargs: Any) -> Query[T, F]:
        """Add greater than or equal filter parameters."""
        gte_filters = self._apply_logical_operation(kwargs, gte_)
        return self.filter(**gte_filters)

    def filter_lt(self, **kwargs: Any) -> Query[T, F]:
        """Add less than filter parameters."""
        lt_filters = self._apply_logical_operation(kwargs, lt_)
        return self.filter(**lt_filters)

    def filter_lte(self, **kwargs: Any) -> Query[T, F]:
        """Add less than or equal filter parameters."""
        lte_filters = self._apply_logical_operation(kwargs, lte_)
        return self.filter(**lte_filters)

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

    def stream(
        self,
        per_page: int = 200,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> StreamingPaginator[T]:
        """Return a memory-efficient streaming paginator."""
        from .streaming import StreamingPaginator

        params = {**self.params, **kwargs}
        filter_param = params.pop("filter", None)

        def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            return self.entity.list(
                filter=filter_param, **{**params, **page_params}
            )

        return StreamingPaginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    def all(
        self,
        per_page: int = 1,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> Iterator[T]:
        """Iterate over all results of the query."""
        paginator = self.paginate(
            per_page=per_page, max_results=max_results, **kwargs
        )
        for page in paginator:
            yield from page.results

    def count(self) -> int:
        """Get count of results without fetching them."""
        result = self.get(per_page=1)
        return result.meta.count

    def first(self) -> T | None:
        """Return the first result of the query or ``None`` if empty."""
        results = self.get(per_page=1)
        return results.results[0] if results.results else None

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
            current_dict: dict[str, Any] = cast(dict[str, Any], current)
            current_dict.update(kwargs)
            self._params["filter"] = current_dict
        else:
            self._params["filter"] = kwargs
        return self

    def filter_or(self, **kwargs: Any) -> AsyncQuery[T, F]:
        current = self._params.get("filter")
        if isinstance(current, or_):
            current.update(kwargs)
            self._params["filter"] = current
        elif isinstance(current, dict):
            current_dict: dict[str, Any] = cast(dict[str, Any], current)
            new_filter = or_(current_dict | kwargs)
            self._params["filter"] = new_filter
        else:
            self._params["filter"] = or_(kwargs)
        return self

    def filter_not(self, **kwargs: Any) -> AsyncQuery[T, F]:
        return self.filter(**{k: not_(v) for k, v in kwargs.items()})

    def filter_gt(self, **kwargs: Any) -> AsyncQuery[T, F]:
        return self.filter(**{k: gt_(v) for k, v in kwargs.items()})

    def filter_gte(self, **kwargs: Any) -> AsyncQuery[T, F]:
        return self.filter(**{k: gte_(v) for k, v in kwargs.items()})

    def filter_lt(self, **kwargs: Any) -> AsyncQuery[T, F]:
        return self.filter(**{k: lt_(v) for k, v in kwargs.items()})

    def filter_lte(self, **kwargs: Any) -> AsyncQuery[T, F]:
        return self.filter(**{k: lte_(v) for k, v in kwargs.items()})

    def search(self, query: str) -> AsyncQuery[T, F]:
        self._params["search"] = query
        return self

    def search_filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        if "filter" not in self._params:
            self._params["filter"] = {}
        for field, value in kwargs.items():
            self._params["filter"][f"{field}.search"] = value
        return self

    def sort(self, **kwargs: str) -> AsyncQuery[T, F]:
        sort_parts = [f"{k}:{v}" for k, v in kwargs.items()]
        self._params["sort"] = ",".join(sort_parts)
        return self

    def group_by(self, field: str) -> AsyncQuery[T, F]:
        self._params["group_by"] = field
        return self

    def select(self, fields: list[str] | str) -> AsyncQuery[T, F]:
        if isinstance(fields, str):
            self._params["select"] = fields
        else:
            self._params["select"] = ",".join(fields)
        return self

    def sample(self, n: int, seed: int | None = None) -> AsyncQuery[T, F]:
        """Sample random results."""
        self._params["sample"] = n
        if seed is not None:
            self._params["seed"] = seed
        return self

    def update_params(self, **params: Any) -> AsyncQuery[T, F]:
        """Update query parameters."""
        self._params.update(params)
        return self

    def paginate(
        self,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> AsyncPaginator[T]:
        params = {**self._params, **kwargs}

        async def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            all_params = {**params, **page_params}
            data = await self._entity.get_list(**all_params)
            return _build_list_result(data, self._model_class)

        return AsyncPaginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    async def stream(
        self,
        per_page: int = 200,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> AsyncStreamingPaginator[T]:
        """Return a memory-efficient async streaming paginator."""
        from .streaming import AsyncStreamingPaginator

        params = {**self._params, **kwargs}

        async def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            all_params = {**params, **page_params}
            data = await self._entity.get_list(**all_params)
            return _build_list_result(data, self._model_class)

        return AsyncStreamingPaginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

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

        data = await self._entity.get_list(**params)

        if "group_by" in self._params:
            return GroupByResult(**data)

        return _build_list_result(data, self._model_class)

    async def all(self) -> AsyncIterator[T]:
        """Iterate over all results using proper pagination."""
        paginator = self.paginate(per_page=1)
        async for item in paginator:
            yield item

    async def count(self) -> int:
        results = await self.get(per_page=1)

        if isinstance(results, GroupByResult):
            return 1

        return results.meta.count or 0

    async def first(self) -> T | None:
        results = await self.get(per_page=1)

        if isinstance(results, GroupByResult):
            msg = "Cannot get first item from grouped results"
            raise TypeError(msg)

        return results.results[0] if results.results else None

    def __repr__(self) -> str:
        """String representation of async query."""
        parts: list[str] = []
        for k in ("filter", "search", "sort", "select"):
            if k in self._params:
                if k == "search":
                    parts.append(f"{k}={self._params[k]!r}")
                else:
                    parts.append(f"{k}={self._params[k]}")

        params_str = ", ".join(parts) if parts else "no filters"
        return f"<AsyncQuery({self._entity.__class__.__name__}) {params_str}>"
