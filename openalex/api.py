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
from .exceptions import NetworkError, TimeoutError
from .utils import AsyncRateLimiter, RateLimiter
from .utils.retry import RetryConfig, async_with_retry, with_retry

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from httpx import Response

logger = get_logger(__name__)


class APIConnection:
    """Handles direct API communication."""

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

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        """Make HTTP request with retry and rate limiting."""
        params = params or {}
        params["mailto"] = self.config.email
        if self.config.api_key:
            kwargs.setdefault("headers", {})[
                "Authorization"
            ] = f"Bearer {self.config.api_key}"

        wait = self.rate_limiter.acquire()
        if wait > 0:
            time.sleep(wait)

        def make_request() -> Response:
            try:
                return self.client.request(method, url, params=params, **kwargs)
            except httpx.TimeoutException as e:  # pragma: no cover - network
                raise TimeoutError(str(e)) from e
            except httpx.RequestError as e:  # pragma: no cover - network
                raise NetworkError(str(e)) from e

        return with_retry(make_request, self.retry_config)()

    def close(self) -> None:
        if self._client:
            self._client.close()

    def __enter__(self) -> APIConnection:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAPIConnection:
    """Async version of API connection."""

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self.rate_limiter = AsyncRateLimiter(DEFAULT_RATE_LIMIT)
        self.retry_config = RetryConfig()
        self._client: httpx.AsyncClient | None = None

    @property
    def base_url(self) -> str:
        return str(self.config.base_url).rstrip("/")

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

        params = params or {}
        params["mailto"] = self.config.email
        if self.config.api_key:
            kwargs.setdefault("headers", {})[
                "Authorization"
            ] = f"Bearer {self.config.api_key}"

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
