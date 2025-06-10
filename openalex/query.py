"""Fluent query builder for OpenAlex resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .resources.base import BaseResource

from .models import BaseFilter, ListResult
from .utils.pagination import MAX_PER_PAGE, Paginator

T = TypeVar("T")
F = TypeVar("F", bound=BaseFilter)


class or_(dict[str, Any]):  # noqa: N801
    """Logical OR expression for filters."""


class _LogicalExpression:
    """Base class for logical expressions."""

    token: str = ""

    def __init__(self, value: Any) -> None:
        self.value = value

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

    def __init__(
        self,
        resource: BaseResource[T, F],
        params: dict[str, Any] | None = None,
    ) -> None:
        self.resource = resource
        self.params: dict[str, Any] = params or {}

    def __getitem__(self, record_id: str | list[str]) -> T | ListResult[T]:
        """Get entity by ID or list of IDs."""
        if isinstance(record_id, list):
            return self.filter(openalex_id=record_id).get(
                per_page=len(record_id)
            )
        return self.resource.get(record_id)

    # internal helper
    def _clone(self, **updates: Any) -> Query[T, F]:
        new_params = {**self.params}
        for key, value in updates.items():
            if key == "filter" and value is not None:
                current = new_params.get("filter", {})
                if (
                    isinstance(current, dict)
                    and isinstance(value, dict)
                    and not isinstance(value, or_)
                ):
                    current.update(value)
                    new_params[key] = current
                else:
                    new_params[key] = value
            else:
                new_params[key] = value
        return Query(self.resource, new_params)

    def _merge_filter_dict(
        self,
        current: dict[str, Any],
        new: dict[str, Any],
        operation: str = "and",
    ) -> dict[str, Any]:
        """Merge filter dictionaries based on operation type."""
        if operation == "or":
            return or_({**current, **new})
        result = current.copy()
        result.update(new)
        return result

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
        return self.resource.list(filter=filter_param, **params)

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
        return self.resource.paginate(
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
        return self.resource.random()

    def autocomplete(self, query: str, **kwargs: Any) -> ListResult[Any]:
        """Autocomplete search."""
        return self.resource.autocomplete(query, **kwargs)
