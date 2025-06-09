"""Fluent query builder for OpenAlex resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .resources.base import BaseResource

from .models import BaseFilter, ListResult
from .utils.pagination import MAX_PER_PAGE, Paginator

T = TypeVar("T")
F = TypeVar("F", bound=BaseFilter)


class Query(Generic[T, F]):
    """Fluent interface for building API queries."""

    def __init__(
        self,
        resource: BaseResource[T, F],
        params: dict[str, Any] | None = None,
    ) -> None:
        self.resource = resource
        self.params: dict[str, Any] = params or {}

    # internal helper
    def _clone(self, **updates: Any) -> Query[T, F]:
        new_params = {**self.params}
        for key, value in updates.items():
            if key == "filter" and value is not None:
                current = new_params.get("filter", {})
                if isinstance(current, dict) and isinstance(value, dict):
                    current.update(value)
                    new_params[key] = current
                else:
                    new_params[key] = value
            else:
                new_params[key] = value
        return Query(self.resource, new_params)

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

    # --- execution methods -----------------------------------------------
    def list(self, **kwargs: Any) -> ListResult[T]:
        """Execute the query and return a list of results."""
        params = {**self.params, **kwargs}
        return self.resource.list(filter=params.get("filter"), **params)

    def paginate(
        self,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        **kwargs: Any,
    ) -> Paginator[T]:
        """Return a paginator for this query."""
        params = {**self.params, **kwargs}
        return self.resource.paginate(
            filter=params.get("filter"),
            per_page=per_page,
            max_results=max_results,
            **params,
        )

    def count(self) -> int:
        """Return the total count for this query."""
        result = self.list(per_page=1)
        return result.meta.count
