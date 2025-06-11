"""Direct API interface for OpenAlex."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

import httpx
from structlog import get_logger

__all__ = ["APIConnection", "AsyncAPIConnection", "get_connection"]

from .config import OpenAlexConfig
from .constants import DEFAULT_RATE_LIMIT
from .exceptions import (
    NetworkError,
    TimeoutError,
    ServerError,
    RateLimitExceeded,
    TemporaryError,
)
from .utils import AsyncRateLimiter, RateLimiter
from .utils.retry import (
    RetryConfig,
    async_with_retry,
    with_retry,
    retry_with_rate_limit,
)

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from httpx import Response

logger = get_logger(__name__)


class APIConnection:
    """Handles direct API communication."""

    __slots__ = ("_client", "config", "rate_limiter", "retry_config")

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self.rate_limiter = RateLimiter(DEFAULT_RATE_LIMIT)
        self.retry_config = RetryConfig()
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                headers=self.config.headers,
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=True,
            )
        return self._client

    @property
    def base_url(self) -> str:
        """Base URL without trailing slash."""
        return str(self.config.base_url).rstrip("/")

    def _default_headers(
        self, headers: dict[str, str] | None
    ) -> dict[str, str]:
        merged = self.config.headers.copy()
        if headers:
            merged.update(headers)
        return merged

    def _default_params(self, params: dict[str, Any] | None) -> dict[str, Any]:
        merged = self.config.params.copy()
        if params:
            merged.update(params)
        return merged

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<APIConnection base_url={self.base_url}>"

    @retry_with_rate_limit
    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        """Make HTTP request with retry logic."""
        params = self._default_params(params)
        kwargs["headers"] = self._default_headers(kwargs.get("headers"))

        wait = self.rate_limiter.acquire()
        if wait > 0:
            time.sleep(wait)

        try:
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                timeout=self.config.timeout,
                **kwargs,
            )

            status_code = getattr(response, "status_code", 200)
            if isinstance(status_code, int) and status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_after_int = int(retry_after) if retry_after else None
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    retry_after=retry_after_int,
                )

            if isinstance(status_code, int) and 500 <= status_code < 600:
                raise ServerError(
                    f"Server error {status_code}: {getattr(response, 'text', '')}"
                )

            if isinstance(status_code, int) and status_code in (502, 503, 504):
                raise TemporaryError(
                    f"Temporary error {status_code}: Service unavailable"
                )

            return response

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {self.config.timeout}s"
            ) from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}") from e
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {str(e)}") from e

    def close(self) -> None:
        if self._client:
            self._client.close()

    def __enter__(self) -> APIConnection:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAPIConnection:
    """Async version of API connection."""

    __slots__ = ("_client", "config", "rate_limiter", "retry_config")

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self.rate_limiter = AsyncRateLimiter(DEFAULT_RATE_LIMIT)
        self.retry_config = RetryConfig()
        self._client: httpx.AsyncClient | None = None

    @property
    def base_url(self) -> str:
        return str(self.config.base_url).rstrip("/")

    def _default_headers(
        self, headers: dict[str, str] | None
    ) -> dict[str, str]:
        merged = self.config.headers.copy()
        if headers:
            merged.update(headers)
        return merged

    def _default_params(self, params: dict[str, Any] | None) -> dict[str, Any]:
        merged = self.config.params.copy()
        if params:
            merged.update(params)
        return merged

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<AsyncAPIConnection base_url={self.base_url}>"

    async def __aenter__(self) -> AsyncAPIConnection:
        self._client = httpx.AsyncClient(
            headers=self.config.headers,
            timeout=httpx.Timeout(self.config.timeout),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        """Make async HTTP request with retry and rate limiting."""
        if not self._client:
            msg = "Use async with statement"
            raise RuntimeError(msg)

        params = self._default_params(params)
        kwargs["headers"] = self._default_headers(kwargs.get("headers"))

        wait = await self.rate_limiter.acquire()
        if wait > 0:
            await asyncio.sleep(wait)

        async def make_request() -> Response:
            assert self._client is not None
            try:
                return await self._client.request(
                    method, url, params=params, **kwargs
                )
            except httpx.TimeoutException as e:  # pragma: no cover - network
                raise TimeoutError(str(e)) from e
            except httpx.RequestError as e:  # pragma: no cover - network
                raise NetworkError(str(e)) from e

        return await async_with_retry(make_request, self.retry_config)()


_connection_pool: dict[str, APIConnection] = {}


def get_connection(config: OpenAlexConfig | None = None) -> APIConnection:
    """Get or create an API connection."""
    key = str(config) if config else "default"
    if key not in _connection_pool:
        _connection_pool[key] = APIConnection(config)
    return _connection_pool[key]
