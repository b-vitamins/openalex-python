from __future__ import annotations

import asyncio
from typing import Any

import httpx
from structlog import get_logger

from .config import OpenAlexConfig
from .exceptions import (
    APIError,
    NetworkError,
    RateLimitExceeded,
    ServerError,
    TemporaryError,
    TimeoutError,
)
from .utils.retry import RetryConfig

logger = get_logger(__name__)


class Connection:
    """Synchronous connection to OpenAlex API."""

    def __init__(self, config: OpenAlexConfig) -> None:
        self._config = config
        self._client: httpx.Client | None = None
        self._retry = RetryConfig()

    def __enter__(self) -> Connection:
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def open(self) -> None:
        if self._client is None:
            self._client = httpx.Client(
                headers=self._build_headers(),
                timeout=httpx.Timeout(self._config.timeout),
                follow_redirects=True,
            )
            logger.debug("connection_opened")

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.debug("connection_closed")

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        if self._client is None:
            self.open()
        assert self._client is not None

        try:
            response = self._client.request(
                method, url, params=params, **kwargs
            )
            return response
        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {self._config.timeout}s"
            ) from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e!s}") from e
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {e!s}") from e

    def _build_headers(self) -> dict[str, str]:
        return self._config.headers.copy()


class AsyncConnection:
    """Async connection to OpenAlex API."""

    def __init__(self, config: OpenAlexConfig) -> None:
        self._config = config
        self._client: httpx.AsyncClient | None = None
        self._retry = RetryConfig()

    async def __aenter__(self) -> AsyncConnection:
        await self.open()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def open(self) -> None:
        if self._client is None:
            headers = self._build_headers()
            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=httpx.Timeout(self._config.timeout),
                follow_redirects=True,
                http2=True,
            )
            logger.debug("async_connection_opened")

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("async_connection_closed")

    async def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        if self._client is None:
            await self.open()
        assert self._client is not None

        try:
            response = await self._make_request_with_retry(
                method, url, params, **kwargs
            )
            return response
        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {self._config.timeout}s"
            ) from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e!s}") from e
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {e!s}") from e

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        max_attempts = (
            self._config.retry_max_attempts if self._config.retry_enabled else 1
        )
        attempt = 0

        while attempt < max_attempts:
            try:
                assert self._client is not None
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    **kwargs,
                )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = int(retry_after) if retry_after else None
                    raise RateLimitExceeded(
                        f"Rate limit exceeded. Retry after {retry_after} seconds",
                        retry_after=retry_after_int,
                    )

                if 500 <= response.status_code < 600:
                    raise ServerError(
                        f"Server error {response.status_code}: {response.text}"
                    )

                if response.status_code in (502, 503, 504):
                    raise TemporaryError(
                        f"Temporary error {response.status_code}: Service unavailable"
                    )

                return response
            except (RateLimitExceeded, ServerError, TemporaryError) as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise

                if isinstance(e, RateLimitExceeded) and e.retry_after:
                    wait_time = e.retry_after
                else:
                    wait_time = min(
                        60,
                        self._config.retry_initial_wait * (2 ** (attempt - 1)),
                    )

                logger.warning(
                    "async_retry_attempt",
                    attempt=attempt,
                    wait_time=wait_time,
                    error=str(e),
                )

                await asyncio.sleep(wait_time)

        raise RuntimeError("Retry logic failed unexpectedly")

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "User-Agent": self._config.headers.get("User-Agent", ""),
            "Accept": "application/json",
        }
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        elif self._config.email:
            headers["From"] = self._config.email
        return headers


_connections: dict[str, Connection] = {}
_async_connections: dict[str, AsyncConnection] = {}


def get_connection(config: OpenAlexConfig) -> Connection:
    key = f"{config.api_key or ''}{config.email or ''}"
    if key not in _connections:
        _connections[key] = Connection(config)
    return _connections[key]


async def get_async_connection(config: OpenAlexConfig) -> AsyncConnection:
    key = f"{config.api_key or ''}{config.email or ''}"
    if key not in _async_connections:
        _async_connections[key] = AsyncConnection(config)
    return _async_connections[key]


async def close_all_async_connections() -> None:
    """Close all async connections."""
    for connection in list(_async_connections.values()):
        await connection.close()
    _async_connections.clear()
