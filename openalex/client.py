"""OpenAlex client implementation."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, cast

__all__ = [
    "AsyncOpenAlex",
    "OpenAlex",
    "async_client",
    "client",
]

from typing import Final

import httpx
from structlog import get_logger

from .config import OpenAlexConfig
from .constants import (
    AUTOCOMPLETE_PATH,
    DEFAULT_RATE_LIMIT,
    HTTP_METHOD_GET,
    PARAM_Q,
    REQUEST_FAILED_MSG,
    TEXT_PATH,
)
from .exceptions import NetworkError, TimeoutError
from .models import AutocompleteResult, ListResult
from .resources import (
    AsyncAuthorsResource,
    AsyncConceptsResource,
    AsyncFundersResource,
    AsyncInstitutionsResource,
    AsyncKeywordsResource,
    AsyncPublishersResource,
    AsyncSourcesResource,
    AsyncTopicsResource,
    AsyncWorksResource,
    AuthorsResource,
    ConceptsResource,
    FundersResource,
    InstitutionsResource,
    KeywordsResource,
    PublishersResource,
    SourcesResource,
    TopicsResource,
    WorksResource,
)
from .utils import (
    AsyncRateLimiter,
    RateLimiter,
    RetryConfig,
    RetryHandler,
    empty_list_result,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Generator

    from .resources.base import BaseResource

logger = get_logger(__name__)

SEARCH_ALL_RESOURCES: Final[list[tuple[str, str]]] = [
    ("works", "works"),
    ("authors", "authors"),
    ("institutions", "institutions"),
    ("sources", "sources"),
    ("concepts", "concepts"),
    ("topics", "topics"),
    ("publishers", "publishers"),
    ("funders", "funders"),
    ("keywords", "keywords"),
]


class OpenAlex:
    """Synchronous client for the OpenAlex API."""

    def __init__(
        self,
        config: OpenAlexConfig | None = None,
        email: str | None = None,
        api_key: str | None = None,
        retry_config: RetryConfig | None = None,
        rate_limit: float = DEFAULT_RATE_LIMIT,
    ) -> None:
        """Initialize OpenAlex client.

        Args:
            config: Configuration object
            email: Email for polite pool (overrides config)
            api_key: API key (overrides config)
            retry_config: Retry configuration
            rate_limit: Requests per second limit
        """
        # Create config if not provided
        if config is None:
            config = OpenAlexConfig()

        # Override email/api_key if provided
        if email is not None:
            config = config.model_copy(update={"email": email})
        if api_key is not None:
            config = config.model_copy(update={"api_key": api_key})

        self.config = config
        if retry_config is None:
            retry_config = RetryConfig()
        self.retry_config = retry_config
        self.retry_handler = RetryHandler(self.retry_config)
        self.rate_limiter = RateLimiter(rate_limit)

        # Initialize HTTP client
        self._client = httpx.Client(
            headers=self.config.headers,
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=True,
        )

        # Initialize resources
        self.works = WorksResource(self)
        self.authors = AuthorsResource(self)
        self.institutions = InstitutionsResource(self)
        self.sources = SourcesResource(self)
        self.concepts = ConceptsResource(self)
        self.topics = TopicsResource(self)
        self.publishers = PublishersResource(self)
        self.funders = FundersResource(self)
        self.keywords = KeywordsResource(self)

    @property
    def base_url(self) -> str:
        """Base URL without a trailing slash."""
        return str(self.config.base_url).rstrip("/")

    def __enter__(self) -> OpenAlex:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with retry and rate limiting.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        # Add default params
        all_params = {**self.config.params}
        if params:
            all_params.update(params)

        # Retry logic
        attempt = 0
        last_error: Exception | None = None

        while attempt < self.retry_config.max_attempts:
            try:
                wait_time = self.rate_limiter.acquire()
                if wait_time > 0:
                    self.retry_handler.wait_sync(wait_time)
                logger.debug(
                    "Making request",
                    method=method,
                    url=url,
                    params=all_params,
                    attempt=attempt + 1,
                )

                return self._client.request(
                    method,
                    url,
                    params=all_params,
                    **kwargs,
                )

            except httpx.TimeoutException as e:
                last_error = TimeoutError(original_error=e)
            except httpx.NetworkError as e:
                last_error = NetworkError(original_error=e)
            except Exception as e:
                last_error = e

            # Check if we should retry
            if not self.retry_handler.should_retry(last_error, attempt + 1):
                break

            # Wait before retry
            wait_time = self.retry_handler.get_wait_time(
                last_error, attempt + 1
            )
            self.retry_handler.wait_sync(wait_time)

            attempt += 1

        # Raise the last error
        if last_error:
            raise last_error

        raise NetworkError(REQUEST_FAILED_MSG)

    def autocomplete(
        self,
        query: str,
        entity_type: str | None = None,
        **params: Any,
    ) -> ListResult[AutocompleteResult]:
        """Autocomplete search across all entity types.

        Args:
            query: Search query
            entity_type: Limit to specific entity type
            **params: Additional parameters

        Returns:
            Autocomplete results
        """
        params[PARAM_Q] = query

        if entity_type:
            url = f"{self.base_url}/{AUTOCOMPLETE_PATH}/{entity_type}"
        else:
            url = f"{self.base_url}/{AUTOCOMPLETE_PATH}"

        response = self._request(HTTP_METHOD_GET, url, params=params)
        response.raise_for_status()

        data = response.json()
        results = [
            AutocompleteResult(**item) for item in data.get("results", [])
        ]

        return ListResult[AutocompleteResult](
            meta=data.get("meta", {}),
            results=results,
        )

    def text_aboutness(
        self,
        title: str,
        abstract: str | None = None,
        entity_type: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Tag free text with OpenAlex aboutness entities.

        Args:
            title: Title text to tag
            abstract: Optional abstract text
            entity_type: Limit to a specific entity type
            **params: Additional query parameters

        Returns:
            Aboutness results from the ``/text`` endpoint
        """
        params["title"] = title
        if abstract is not None:
            params["abstract"] = abstract

        url = f"{self.base_url}/{TEXT_PATH}"
        if entity_type:
            url = f"{url}/{entity_type}"

        response = self._request(HTTP_METHOD_GET, url, params=params)
        response.raise_for_status()

        return cast("dict[str, Any]", response.json())

    def search_all(
        self,
        query: str,
        **params: Any,
    ) -> dict[str, ListResult[Any]]:
        """Search across all entity types.

        Args:
            query: Search query
            **params: Additional parameters

        Returns:
            Dictionary of results by entity type
        """
        results: dict[str, ListResult[Any]] = {}

        entity_types: list[tuple[str, BaseResource[Any, Any]]] = [
            (name, getattr(self, attr)) for name, attr in SEARCH_ALL_RESOURCES
        ]

        for entity_type, resource in entity_types:
            try:
                result = resource.search(query, **params)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Failed to search %s",
                    entity_type,
                    exc_info=exc,
                )
                result = empty_list_result()

            results[entity_type] = result

        return results


class AsyncOpenAlex:
    """Asynchronous client for the OpenAlex API."""

    def __init__(
        self,
        config: OpenAlexConfig | None = None,
        email: str | None = None,
        api_key: str | None = None,
        retry_config: RetryConfig | None = None,
        rate_limit: float = DEFAULT_RATE_LIMIT,
    ) -> None:
        """Initialize async OpenAlex client.

        Args:
            config: Configuration object
            email: Email for polite pool (overrides config)
            api_key: API key (overrides config)
            retry_config: Retry configuration
            rate_limit: Requests per second limit
        """
        # Create config if not provided
        if config is None:
            config = OpenAlexConfig()

        # Override email/api_key if provided
        if email is not None:
            config = config.model_copy(update={"email": email})
        if api_key is not None:
            config = config.model_copy(update={"api_key": api_key})

        self.config = config
        if retry_config is None:
            retry_config = RetryConfig()
        self.retry_config = retry_config
        self.retry_handler = RetryHandler(self.retry_config)
        self.rate_limiter = AsyncRateLimiter(rate_limit)

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            headers=self.config.headers,
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=True,
        )

        # Initialize resources
        self.works = AsyncWorksResource(self)
        self.authors = AsyncAuthorsResource(self)
        self.institutions = AsyncInstitutionsResource(self)
        self.sources = AsyncSourcesResource(self)
        self.concepts = AsyncConceptsResource(self)
        self.topics = AsyncTopicsResource(self)
        self.publishers = AsyncPublishersResource(self)
        self.funders = AsyncFundersResource(self)
        self.keywords = AsyncKeywordsResource(self)

    @property
    def base_url(self) -> str:
        """Base URL without a trailing slash."""
        return str(self.config.base_url).rstrip("/")

    async def __aenter__(self) -> AsyncOpenAlex:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make async HTTP request with retry and rate limiting.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        # Add default params
        all_params = {**self.config.params}
        if params:
            all_params.update(params)

        # Retry logic
        attempt = 0
        last_error: Exception | None = None

        while attempt < self.retry_config.max_attempts:
            try:
                wait_time = await self.rate_limiter.acquire()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                logger.debug(
                    "Making async request",
                    method=method,
                    url=url,
                    params=all_params,
                    attempt=attempt + 1,
                )

                return await self._client.request(
                    method,
                    url,
                    params=all_params,
                    **kwargs,
                )

            except httpx.TimeoutException as e:
                last_error = TimeoutError(original_error=e)
            except httpx.NetworkError as e:
                last_error = NetworkError(original_error=e)
            except Exception as e:
                last_error = e

            # Check if we should retry
            if not self.retry_handler.should_retry(last_error, attempt + 1):
                break

            # Wait before retry
            wait_time = self.retry_handler.get_wait_time(
                last_error, attempt + 1
            )
            await self.retry_handler.wait(wait_time)

            attempt += 1

        # Raise the last error
        if last_error:
            raise last_error

        raise NetworkError(REQUEST_FAILED_MSG)

    async def autocomplete(
        self,
        query: str,
        entity_type: str | None = None,
        **params: Any,
    ) -> ListResult[AutocompleteResult]:
        """Autocomplete search across all entity types.

        Args:
            query: Search query
            entity_type: Limit to specific entity type
            **params: Additional parameters

        Returns:
            Autocomplete results
        """
        params[PARAM_Q] = query

        if entity_type:
            url = f"{self.base_url}/{AUTOCOMPLETE_PATH}/{entity_type}"
        else:
            url = f"{self.base_url}/{AUTOCOMPLETE_PATH}"

        response = await self._request(HTTP_METHOD_GET, url, params=params)
        response.raise_for_status()

        data = response.json()
        results = [
            AutocompleteResult(**item) for item in data.get("results", [])
        ]

        return ListResult[AutocompleteResult](
            meta=data.get("meta", {}),
            results=results,
        )

    async def text_aboutness(
        self,
        title: str,
        abstract: str | None = None,
        entity_type: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Tag free text with OpenAlex aboutness entities asynchronously."""
        params["title"] = title
        if abstract is not None:
            params["abstract"] = abstract

        url = f"{self.base_url}/{TEXT_PATH}"
        if entity_type:
            url = f"{url}/{entity_type}"

        response = await self._request(HTTP_METHOD_GET, url, params=params)
        response.raise_for_status()

        return cast("dict[str, Any]", response.json())

    async def search_all(
        self,
        query: str,
        **params: Any,
    ) -> dict[str, ListResult[Any]]:
        """Search across all entity types concurrently.

        Args:
            query: Search query
            **params: Additional parameters

        Returns:
            Dictionary of results by entity type
        """
        # Create search tasks
        tasks: dict[str, Awaitable[ListResult[Any]]] = {
            name: getattr(self, attr).search(query, **params)
            for name, attr in SEARCH_ALL_RESOURCES
        }

        results: dict[str, ListResult[Any]] = {}
        tasks_list = await asyncio.gather(
            *tasks.values(), return_exceptions=True
        )
        for (entity_type, _), task_result in zip(
            tasks.items(), tasks_list, strict=False
        ):
            if isinstance(
                task_result, Exception
            ):  # pragma: no cover - defensive
                logger.warning(
                    "Failed to search %s",
                    entity_type,
                    exc_info=task_result,
                )
                results[entity_type] = empty_list_result()
            else:
                results[entity_type] = cast("ListResult[Any]", task_result)

        return results


# Convenience functions
@contextmanager
def client(
    email: str | None = None,
    api_key: str | None = None,
    **kwargs: Any,
) -> Generator[OpenAlex, None, None]:
    """Create OpenAlex client as context manager.

    Args:
        email: Email for polite pool
        api_key: API key
        **kwargs: Additional client arguments

    Yields:
        OpenAlex client
    """
    c = OpenAlex(email=email, api_key=api_key, **kwargs)
    try:
        yield c
    finally:
        c.close()


@asynccontextmanager
async def async_client(
    email: str | None = None,
    api_key: str | None = None,
    **kwargs: Any,
) -> AsyncIterator[AsyncOpenAlex]:
    """Create async OpenAlex client as context manager.

    Args:
        email: Email for polite pool
        api_key: API key
        **kwargs: Additional client arguments

    Yields:
        AsyncOpenAlex client
    """
    c = AsyncOpenAlex(email=email, api_key=api_key, **kwargs)
    try:
        yield c
    finally:
        await c.close()
