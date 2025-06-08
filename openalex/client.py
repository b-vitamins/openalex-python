"""OpenAlex client implementation."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any

import httpx
from structlog import get_logger

from .config import OpenAlexConfig
from .exceptions import NetworkError, TimeoutError
from .models import AutocompleteResult, ListResult, Meta
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
from .utils import AsyncRateLimiter, RateLimiter, RetryConfig, RetryHandler

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Generator

    from .resources.base import BaseResource

logger = get_logger(__name__)


class OpenAlex:
    """Synchronous client for the OpenAlex API."""

    def __init__(
        self,
        config: OpenAlexConfig | None = None,
        email: str | None = None,
        api_key: str | None = None,
        retry_config: RetryConfig | None = None,
        rate_limit: float = 10.0,
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
        self.retry_config = retry_config or RetryConfig()
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

        # Rate limiting
        wait_time = self.rate_limiter.acquire()
        if wait_time > 0:
            self.retry_handler.wait_sync(wait_time)

        # Retry logic
        attempt = 0
        last_error: Exception | None = None

        while attempt < self.retry_config.max_attempts:
            try:
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

        msg = "Request failed after all retries"
        raise NetworkError(msg)

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
        params["q"] = query

        base = str(self.config.base_url).rstrip("/")
        if entity_type:
            url = f"{base}/autocomplete/{entity_type}"
        else:
            url = f"{base}/autocomplete"

        response = self._request("GET", url, params=params)
        response.raise_for_status()

        data = response.json()
        results = [
            AutocompleteResult(**item) for item in data.get("results", [])
        ]

        return ListResult[AutocompleteResult](
            meta=data.get("meta", {}),
            results=results,
        )

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

        # Search each entity type
        entity_types: list[tuple[str, BaseResource[Any, Any]]] = [
            ("works", self.works),
            ("authors", self.authors),
            ("institutions", self.institutions),
            ("sources", self.sources),
            ("concepts", self.concepts),
            ("topics", self.topics),
            ("publishers", self.publishers),
            ("funders", self.funders),
            ("keywords", self.keywords),
        ]

        for entity_type, resource in entity_types:
            try:
                results[entity_type] = resource.search(query, **params)
            except Exception as e:
                logger.warning(
                    "Failed to search %s",
                    entity_type,
                    error=str(e),
                )
                results[entity_type] = ListResult(
                    meta=Meta(
                        count=0,
                        db_response_time_ms=0,
                        page=1,
                        per_page=0,
                        groups_count=0,
                        next_cursor=None,
                    ),
                    results=[],
                )

        return results


class AsyncOpenAlex:
    """Asynchronous client for the OpenAlex API."""

    def __init__(
        self,
        config: OpenAlexConfig | None = None,
        email: str | None = None,
        api_key: str | None = None,
        retry_config: RetryConfig | None = None,
        rate_limit: float = 10.0,
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
        self.retry_config = retry_config or RetryConfig()
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

        # Rate limiting
        async with self.rate_limiter:
            pass

        # Retry logic
        attempt = 0
        last_error: Exception | None = None

        while attempt < self.retry_config.max_attempts:
            try:
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

        msg = "Request failed after all retries"
        raise NetworkError(msg)

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
        params["q"] = query

        base = str(self.config.base_url).rstrip("/")
        if entity_type:
            url = f"{base}/autocomplete/{entity_type}"
        else:
            url = f"{base}/autocomplete"

        response = await self._request("GET", url, params=params)
        response.raise_for_status()

        data = response.json()
        results = [
            AutocompleteResult(**item) for item in data.get("results", [])
        ]

        return ListResult[AutocompleteResult](
            meta=data.get("meta", {}),
            results=results,
        )

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
            "works": self.works.search(query, **params),
            "authors": self.authors.search(query, **params),
            "institutions": self.institutions.search(query, **params),
            "sources": self.sources.search(query, **params),
            "concepts": self.concepts.search(query, **params),
            "topics": self.topics.search(query, **params),
            "publishers": self.publishers.search(query, **params),
            "funders": self.funders.search(query, **params),
            "keywords": self.keywords.search(query, **params),
        }

        # Run concurrently
        results: dict[str, ListResult[Any]] = {}
        for entity_type, task in tasks.items():
            try:
                results[entity_type] = await task
            except Exception as e:
                logger.warning(
                    "Failed to search %s",
                    entity_type,
                    error=str(e),
                )
                results[entity_type] = ListResult(
                    meta=Meta(
                        count=0,
                        db_response_time_ms=0,
                        page=1,
                        per_page=0,
                        groups_count=0,
                        next_cursor=None,
                    ),
                    results=[],
                )

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
