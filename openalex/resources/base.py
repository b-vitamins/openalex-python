"""Base resource class for OpenAlex API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar

from pydantic import ValidationError
from structlog import get_logger

from ..constants import HTTP_METHOD_GET, OPENALEX_ID_PREFIX
from ..exceptions import ValidationError as OpenAlexValidationError
from ..exceptions import raise_for_status
from ..models import BaseFilter, ListResult
from ..utils import (
    AsyncPaginator,
    Paginator,
    normalize_params,
)
from ..utils.pagination import MAX_PER_PAGE

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex

logger = get_logger(__name__)

__all__ = ["AsyncBaseResource", "BaseResource"]

T = TypeVar("T")
F = TypeVar("F", bound=BaseFilter)


class BaseResource(Generic[T, F]):
    """Base class for API resources."""

    # Override in subclasses
    endpoint: str = ""
    model_class: type[T] = None  # type: ignore
    filter_class: type[F] = BaseFilter  # type: ignore

    def __init__(self, client: OpenAlex) -> None:
        """Initialize resource."""
        self.client = client

    def _build_url(self, path: str = "") -> str:
        """Build full URL for endpoint."""
        base = f"{self.client.base_url}/{self.endpoint}"
        if path:
            return f"{base}/{path.lstrip('/')}"
        return base

    def _parse_response(self, data: dict[str, Any]) -> T:
        """Parse response data into model."""
        try:
            return self.model_class(**data)
        except ValidationError:
            # Fallback to constructing the model without validation so
            # downstream code still receives an object.
            return self.model_class.model_construct(**data)  # type: ignore[attr-defined,no-any-return]

    def _parse_list_response(self, data: dict[str, Any]) -> ListResult[T]:
        """Parse list response into ListResult."""
        try:
            results = [
                self._parse_response(item) for item in data.get("results", [])
            ]
            return ListResult[T](
                meta=data.get("meta", {}),
                results=results,
                group_by=data.get("group_by"),
            )
        except ValidationError as e:
            msg = "Failed to parse list response"
            raise OpenAlexValidationError(
                msg,
                field=str(e),
                value=data,
            ) from e

    def _apply_filter_params(
        self, params: dict[str, Any], filter: F | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Merge filter information into ``params``."""
        if filter is None:
            return params

        if isinstance(filter, BaseFilter):
            params.update(filter.to_params(include_defaults=False))
            return params

        known_fields = set(self.filter_class.model_fields)
        filter_kwargs: dict[str, Any] = {}
        raw_filters: dict[str, Any] = {}
        for key, value in filter.items():
            if key in known_fields:
                filter_kwargs[key] = value
            else:
                raw_filters[key] = value

        if raw_filters:
            filter_kwargs["filter"] = raw_filters

        filter_obj = self.filter_class(**filter_kwargs)
        params.update(filter_obj.to_params(include_defaults=False))

        return params

    def get(self, id: str, **params: Any) -> T:
        """Get a single entity by ID.

        Args:
            id: Entity ID (with or without URL prefix)
            **params: Additional query parameters

        Returns:
            Entity model instance
        """
        # Remove OpenAlex prefix if present but keep full IDs like ORCID/ROR
        if id.startswith(OPENALEX_ID_PREFIX):
            id = id[len(OPENALEX_ID_PREFIX) :]

        url = self._build_url(id)
        response = self.client._request(HTTP_METHOD_GET, url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_response(response.json())

    def list(
        self,
        filter: F | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[T]:
        """List entities with optional filtering.

        Args:
            filter: Filter object or dictionary
            **params: Additional query parameters

        Returns:
            List result with metadata
        """
        params = self._apply_filter_params(params, filter)

        params = normalize_params(params)

        url = self._build_url()
        response = self.client._request(HTTP_METHOD_GET, url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_list_response(response.json())

    def search(
        self,
        query: str,
        filter: F | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[T]:
        """Search entities.

        Args:
            query: Search query
            filter: Filter object or dictionary
            **params: Additional query parameters

        Returns:
            Search results with metadata
        """
        params["search"] = query
        return self.list(filter=filter, **params)

    def filter(self, **filter_params: Any) -> Self | F:
        """Create a filter object.

        Args:
            **filter_params: Filter parameters

        Returns:
            Filter instance
        """
        return self.filter_class(**filter_params)

    def paginate(
        self,
        filter: F | dict[str, Any] | None = None,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        **params: Any,
    ) -> Paginator[T]:
        """Create a paginator for iterating through results.

        Args:
            filter: Filter object or dictionary
            per_page: Results per page
            max_results: Maximum total results
            **params: Additional query parameters

        Returns:
            Paginator instance
        """
        params = self._apply_filter_params(params, filter)

        def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            url = self._build_url()
            all_params = {**params, **page_params}
            all_params = normalize_params(all_params)
            response = self.client._request(  # noqa: SLF001
                HTTP_METHOD_GET, url, params=all_params
            )
            raise_for_status(response)
            return self._parse_list_response(response.json())

        return Paginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    def random(self, **params: Any) -> T:
        """Get a random entity.

        Args:
            **params: Query parameters

        Returns:
            Random entity
        """
        url = self._build_url("random")
        params = normalize_params(params)
        response = self.client._request(HTTP_METHOD_GET, url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_response(response.json())

    def autocomplete(
        self,
        query: str,
        **params: Any,
    ) -> ListResult[Any]:
        """Autocomplete search.

        Args:
            query: Search query
            **params: Additional parameters

        Returns:
            Autocomplete results
        """
        params["q"] = query
        url = f"{self.client.base_url}/autocomplete/{self.endpoint}"
        params = normalize_params(params)
        response = self.client._request(HTTP_METHOD_GET, url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_list_response(response.json())


class AsyncBaseResource(Generic[T, F]):
    """Async base class for API resources."""

    endpoint: str = ""
    model_class: type[T] = None  # type: ignore
    filter_class: type[F] = BaseFilter  # type: ignore

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async resource."""
        self.client = client

    def _build_url(self, path: str = "") -> str:
        """Build full URL for endpoint."""
        base = f"{self.client.base_url}/{self.endpoint}"
        if path:
            return f"{base}/{path.lstrip('/')}"
        return base

    def _parse_response(self, data: dict[str, Any]) -> T:
        """Parse response data into model."""
        try:
            return self.model_class(**data)
        except ValidationError:
            # Fallback to constructing the model without validation so
            # downstream code still receives an object.
            return self.model_class.model_construct(**data)  # type: ignore[attr-defined,no-any-return]

    def _parse_list_response(self, data: dict[str, Any]) -> ListResult[T]:
        """Parse list response into ListResult."""
        try:
            results = [
                self._parse_response(item) for item in data.get("results", [])
            ]
            return ListResult[T](
                meta=data.get("meta", {}),
                results=results,
                group_by=data.get("group_by"),
            )
        except ValidationError as e:
            msg = "Failed to parse list response"
            raise OpenAlexValidationError(
                msg,
                field=str(e),
                value=data,
            ) from e

    def _apply_filter_params(
        self, params: dict[str, Any], filter: F | dict[str, Any] | None
    ) -> dict[str, Any]:
        """Merge filter information into ``params``."""
        if filter is None:
            return params

        if isinstance(filter, BaseFilter):
            params.update(filter.to_params(include_defaults=False))
            return params

        known_fields = set(self.filter_class.model_fields)
        filter_kwargs: dict[str, Any] = {}
        raw_filters: dict[str, Any] = {}
        for key, value in filter.items():
            if key in known_fields:
                filter_kwargs[key] = value
            else:
                raw_filters[key] = value

        if raw_filters:
            filter_kwargs["filter"] = raw_filters

        filter_obj = self.filter_class(**filter_kwargs)
        params.update(filter_obj.to_params(include_defaults=False))

        return params

    async def get(self, id: str, **params: Any) -> T:
        """Get a single entity by ID."""
        if id.startswith(OPENALEX_ID_PREFIX):
            id = id[len(OPENALEX_ID_PREFIX) :]

        url = self._build_url(id)
        response = await self.client._request(  # noqa: SLF001
            HTTP_METHOD_GET, url, params=params
        )
        raise_for_status(response)

        return self._parse_response(response.json())

    async def list(
        self,
        filter: F | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[T]:
        """List entities with optional filtering."""
        params = self._apply_filter_params(params, filter)

        params = normalize_params(params)

        url = self._build_url()
        response = await self.client._request(  # noqa: SLF001
            HTTP_METHOD_GET, url, params=params
        )
        raise_for_status(response)

        return self._parse_list_response(response.json())

    async def search(
        self,
        query: str,
        filter: F | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[T]:
        """Search entities."""
        params["search"] = query
        return await self.list(filter=filter, **params)

    def filter(self, **filter_params: Any) -> Self | F:
        """Create a filter object."""
        return self.filter_class(**filter_params)

    def paginate(
        self,
        filter: F | dict[str, Any] | None = None,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        **params: Any,
    ) -> AsyncPaginator[T]:
        """Create an async paginator."""
        params = self._apply_filter_params(params, filter)

        async def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            url = self._build_url()
            all_params = {**params, **page_params}
            all_params = normalize_params(all_params)
            response = await self.client._request(  # noqa: SLF001
                HTTP_METHOD_GET, url, params=all_params
            )
            raise_for_status(response)
            return self._parse_list_response(response.json())

        return AsyncPaginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    async def random(self, **params: Any) -> T:
        """Get a random entity."""
        url = self._build_url("random")
        params = normalize_params(params)
        response = await self.client._request(  # noqa: SLF001
            HTTP_METHOD_GET, url, params=params
        )
        raise_for_status(response)

        return self._parse_response(response.json())

    async def autocomplete(
        self,
        query: str,
        **params: Any,
    ) -> ListResult[Any]:
        """Autocomplete search."""
        params["q"] = query
        url = f"{self.client.base_url}/autocomplete/{self.endpoint}"
        params = normalize_params(params)
        response = await self.client._request(  # noqa: SLF001
            HTTP_METHOD_GET, url, params=params
        )
        raise_for_status(response)

        return self._parse_list_response(response.json())
