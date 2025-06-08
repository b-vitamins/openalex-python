"""Base resource class for OpenAlex API endpoints."""
# pragma: no cover

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic import ValidationError
from structlog import get_logger

from ..exceptions import ValidationError as OpenAlexValidationError
from ..exceptions import raise_for_status
from ..models import BaseFilter, ListResult
from ..utils import AsyncPaginator, Paginator

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex

logger = get_logger(__name__)

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
        base = f"{str(self.client.config.base_url).rstrip('/')}/{self.endpoint}"
        if path:
            return f"{base}/{path.lstrip('/')}"
        return base

    def _normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Normalize parameter names and values for the API."""
        normalized: dict[str, Any] = {}
        for key, value in params.items():
            # Convert snake_case keys used by the SDK to the API format
            if key == "per_page":
                key = "per-page"
            elif key == "group_by":
                key = "group-by"

            if key == "select" and isinstance(value, list):
                normalized[key] = ",".join(value)
            else:
                normalized[key] = value

        return normalized

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

    def get(self, id: str, **params: Any) -> T:
        """Get a single entity by ID.

        Args:
            id: Entity ID (with or without URL prefix)
            **params: Additional query parameters

        Returns:
            Entity model instance
        """
        # Remove OpenAlex prefix if present but keep full IDs like ORCID/ROR
        if id.startswith("https://openalex.org/"):
            id = id.split("/")[-1]

        url = self._build_url(id)
        response = self.client._request("GET", url, params=params)  # noqa: SLF001
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
        # Handle filter parameter
        if filter is not None:
            if isinstance(filter, BaseFilter):
                params.update(filter.to_params())
            elif isinstance(filter, dict):
                known_fields = set(self.filter_class.model_fields)
                filter_kwargs: dict[str, Any] = {}
                raw_filters: dict[str, Any] = {}
                for k, v in filter.items():
                    if k in known_fields:
                        filter_kwargs[k] = v
                    else:
                        raw_filters[k] = v

                if raw_filters:
                    filter_kwargs["filter"] = raw_filters

                filter_obj = self.filter_class(**filter_kwargs)
                params.update(filter_obj.to_params())

        params = self._normalize_params(params)

        url = self._build_url()
        response = self.client._request("GET", url, params=params)  # noqa: SLF001
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

    def filter(self, **filter_params: Any) -> F:
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
        per_page: int = 200,
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
        # Prepare parameters
        if filter is not None:
            if isinstance(filter, BaseFilter):
                params.update(filter.to_params())
            elif isinstance(filter, dict):
                known_fields = set(self.filter_class.model_fields)
                filter_kwargs: dict[str, Any] = {}
                raw_filters: dict[str, Any] = {}
                for k, v in filter.items():
                    if k in known_fields:
                        filter_kwargs[k] = v
                    else:
                        raw_filters[k] = v

                if raw_filters:
                    filter_kwargs["filter"] = raw_filters

                filter_obj = self.filter_class(**filter_kwargs)
                params.update(filter_obj.to_params())

        def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            url = self._build_url()
            all_params = {**params, **page_params}
            all_params = self._normalize_params(all_params)
            response = self.client._request(  # noqa: SLF001
                "GET", url, params=all_params
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
        params = self._normalize_params(params)
        response = self.client._request("GET", url, params=params)  # noqa: SLF001
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
        url = f"{str(self.client.config.base_url).rstrip('/')}/autocomplete/{self.endpoint}"
        params = self._normalize_params(params)
        response = self.client._request("GET", url, params=params)  # noqa: SLF001
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

    def _normalize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Normalize parameter names and values for the API."""
        normalized: dict[str, Any] = {}
        for key, value in params.items():
            if key == "per_page":
                key = "per-page"
            elif key == "group_by":
                key = "group-by"

            if key == "select" and isinstance(value, list):
                normalized[key] = ",".join(value)
            else:
                normalized[key] = value

        return normalized

    def _build_url(self, path: str = "") -> str:
        """Build full URL for endpoint."""
        base = f"{str(self.client.config.base_url).rstrip('/')}/{self.endpoint}"
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

    async def get(self, id: str, **params: Any) -> T:
        """Get a single entity by ID."""
        if id.startswith("https://openalex.org/"):
            id = id.split("/")[-1]

        url = self._build_url(id)
        response = await self.client._request("GET", url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_response(response.json())

    async def list(
        self,
        filter: F | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[T]:
        """List entities with optional filtering."""
        if filter is not None:
            if isinstance(filter, BaseFilter):
                params.update(filter.to_params())
            elif isinstance(filter, dict):
                known_fields = set(self.filter_class.model_fields)
                filter_kwargs: dict[str, Any] = {}
                raw_filters: dict[str, Any] = {}
                for k, v in filter.items():
                    if k in known_fields:
                        filter_kwargs[k] = v
                    else:
                        raw_filters[k] = v

                if raw_filters:
                    filter_kwargs["filter"] = raw_filters

                filter_obj = self.filter_class(**filter_kwargs)
                params.update(filter_obj.to_params())

        params = self._normalize_params(params)

        url = self._build_url()
        response = await self.client._request("GET", url, params=params)  # noqa: SLF001
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

    def filter(self, **filter_params: Any) -> F:
        """Create a filter object."""
        return self.filter_class(**filter_params)

    def paginate(
        self,
        filter: F | dict[str, Any] | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **params: Any,
    ) -> AsyncPaginator[T]:
        """Create an async paginator."""
        if filter is not None:
            if isinstance(filter, BaseFilter):
                params.update(filter.to_params())
            elif isinstance(filter, dict):
                known_fields = set(self.filter_class.model_fields)
                filter_kwargs: dict[str, Any] = {}
                raw_filters: dict[str, Any] = {}
                for k, v in filter.items():
                    if k in known_fields:
                        filter_kwargs[k] = v
                    else:
                        raw_filters[k] = v

                if raw_filters:
                    filter_kwargs["filter"] = raw_filters

                filter_obj = self.filter_class(**filter_kwargs)
                params.update(filter_obj.to_params())

        async def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            url = self._build_url()
            all_params = {**params, **page_params}
            all_params = self._normalize_params(all_params)
            response = await self.client._request(  # noqa: SLF001
                "GET", url, params=all_params
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
        params = self._normalize_params(params)
        response = await self.client._request("GET", url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_response(response.json())

    async def autocomplete(
        self,
        query: str,
        **params: Any,
    ) -> ListResult[Any]:
        """Autocomplete search."""
        params["q"] = query
        url = f"{str(self.client.config.base_url).rstrip('/')}/autocomplete/{self.endpoint}"
        params = self._normalize_params(params)
        response = await self.client._request("GET", url, params=params)  # noqa: SLF001
        raise_for_status(response)

        return self._parse_list_response(response.json())
