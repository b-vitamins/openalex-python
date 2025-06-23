from __future__ import annotations

import asyncio
import time
import weakref
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any, cast

import httpx
from structlog import get_logger

__all__ = [
    "AsyncConnection",
    "Connection",
    "close_all_async_connections",
    "get_async_connection",
    "get_connection",
]

if TYPE_CHECKING:
    from .config import OpenAlexConfig
from .exceptions import (
    APIError,
    NetworkError,
    RateLimitError,
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
        operation: str | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        if self._client is None:
            self.open()
        assert self._client is not None

        # Merge config default params with request params
        merged_params = self._config.params.copy()
        if params:
            merged_params.update(params)

        if operation is None:
            if "/autocomplete/" in url:
                operation = "autocomplete"
            elif method == "GET":
                # Count path segments: /works = 1, /works/W123 = 2
                from urllib.parse import urlparse

                path = urlparse(url).path.strip("/")
                path_segments = len(path.split("/")) if path else 0
                if path_segments > 1:
                    operation = "get"
                elif merged_params and (
                    (
                        isinstance(merged_params.get("filter"), dict)
                        and "search" in merged_params["filter"]
                    )
                    or merged_params.get("search")
                ):
                    operation = "search"
                else:
                    operation = "list"
            else:
                operation = "list"

        timeout_val = self._config.operation_timeouts.get(
            operation, self._config.timeout
        )
        if "timeout" not in kwargs:
            kwargs["timeout"] = httpx.Timeout(timeout_val)

        metrics = None
        start_time = 0.0
        endpoint = "unknown"
        if self._config.collect_metrics:
            from .metrics import get_metrics_collector

            metrics = get_metrics_collector(self._config)
            start_time = time.time()
            endpoint = url.split("/")[-2] if "/" in url else "unknown"

        try:
            response = self._make_request_with_retry(
                method, url, merged_params, **kwargs
            )
        except httpx.TimeoutException as e:
            if metrics is not None:
                duration = time.time() - start_time
                metrics.record_request(endpoint, duration, success=False)
            msg = f"Request timed out after {timeout_val}s"
            raise TimeoutError(
                msg, operation=operation, timeout_value=timeout_val
            ) from e
        except httpx.NetworkError as e:
            if metrics is not None:
                duration = time.time() - start_time
                metrics.record_request(endpoint, duration, success=False)
            msg = f"Network error: {e!s}"
            raise NetworkError(msg) from e
        except httpx.HTTPError as e:
            if metrics is not None:
                duration = time.time() - start_time
                metrics.record_request(endpoint, duration, success=False)
            msg = f"HTTP error: {e!s}"
            raise APIError(msg) from e
        else:
            if metrics is not None:
                duration = time.time() - start_time
                metrics.record_request(
                    endpoint, duration, success=response.is_success
                )
            return response

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        max_attempts = (
            (self._config.retry_max_attempts + 1)
            if self._config.retry_enabled
            else 1
        )
        attempt = 1

        def _raise(err: Exception) -> None:
            raise err

        while attempt <= max_attempts:
            try:
                assert self._client is not None

                if (
                    self._config.middleware.request_interceptors
                    or self._config.middleware.response_interceptors
                ):
                    request = self._client.build_request(
                        method, url, params=params, **kwargs
                    )
                    for (
                        req_interceptor
                    ) in self._config.middleware.request_interceptors:
                        request = req_interceptor.process_request(request)
                    send_kwargs: dict[str, Any] = {}
                    response = self._client.send(request, **send_kwargs)
                    for (
                        resp_interceptor
                    ) in self._config.middleware.response_interceptors:
                        response = resp_interceptor.process_response(response)
                else:
                    # Include headers for test compatibility
                    headers = {
                        **self._build_headers(),
                        **kwargs.pop("headers", {}),
                    }
                    response = self._client.request(
                        method,
                        url=url,
                        params=params,
                        headers=headers,
                        **kwargs,
                    )

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = None
                    if retry_after:
                        if retry_after.isdigit():
                            retry_after_int = int(retry_after)
                        else:
                            # Try to parse as HTTP date
                            try:
                                parsed_dt = cast(
                                    datetime | None,
                                    parsedate_to_datetime(retry_after),
                                )
                                if parsed_dt is not None:
                                    retry_dt: datetime = parsed_dt
                                    retry_after_int = int(
                                        (
                                            retry_dt - datetime.now(UTC)
                                        ).total_seconds()  # type: ignore[misc]
                                    )
                                else:
                                    retry_after_int = None
                            except Exception:
                                retry_after_int = None
                    _raise(RateLimitError(retry_after=retry_after_int))

                if response.status_code == 503:
                    msg = "Service temporarily unavailable"
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = None
                    if retry_after:
                        try:
                            retry_after_int = (
                                int(retry_after)
                                if isinstance(retry_after, str | int)
                                else None
                            )
                        except (ValueError, TypeError):
                            retry_after_int = None
                    _raise(
                        TemporaryError(
                            msg, status_code=503, retry_after=retry_after_int
                        )
                    )

                if response.status_code in (502, 504):
                    msg = f"Server error {response.status_code}: Service unavailable"
                    _raise(ServerError(msg, status_code=response.status_code))

                if 500 <= response.status_code < 600:
                    msg = (
                        f"Server error {response.status_code}: {response.text}"
                    )
                    _raise(ServerError(msg, status_code=response.status_code))

            except (ServerError, TemporaryError, RateLimitError) as e:
                attempt += 1
                if attempt > max_attempts:
                    raise

                if isinstance(e, RateLimitError) and e.retry_after:
                    wait_time = e.retry_after
                else:
                    wait_time = min(
                        60,
                        self._config.retry_initial_wait
                        * (
                            self._config.retry_exponential_base ** (attempt - 2)
                        ),
                    )

                logger.warning(
                    "retry_attempt",
                    attempt=attempt,
                    wait_time=wait_time,
                    error=str(e),
                )

                import time

                time.sleep(wait_time)
            else:
                return response

        msg = "Retry logic failed unexpectedly"
        raise RuntimeError(msg)

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

        # Merge config default params with request params
        merged_params = self._config.params.copy()
        if params:
            merged_params.update(params)

        try:
            response = await self._make_request_with_retry(
                method, url, merged_params, **kwargs
            )
        except httpx.TimeoutException as e:
            msg = f"Request timed out after {self._config.timeout}s"
            raise TimeoutError(msg) from e
        except httpx.NetworkError as e:
            msg = f"Network error: {e!s}"
            raise NetworkError(msg) from e
        except httpx.HTTPError as e:
            msg = f"HTTP error: {e!s}"
            raise APIError(msg) from e
        else:
            return response

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        max_attempts = (
            (self._config.retry_max_attempts + 1)
            if self._config.retry_enabled
            else 1
        )
        attempt = 1
        # attempt 1 is the initial request, 2+ are retries

        def _raise(err: Exception) -> None:
            raise err

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
                    retry_after_int = None
                    if retry_after:
                        if retry_after.isdigit():
                            retry_after_int = int(retry_after)
                        else:
                            # Try to parse as HTTP date
                            try:
                                parsed_dt = cast(
                                    datetime | None,
                                    parsedate_to_datetime(retry_after),
                                )
                                if parsed_dt is not None:
                                    retry_dt: datetime = parsed_dt
                                    retry_after_int = int(
                                        (
                                            retry_dt - datetime.now(UTC)
                                        ).total_seconds()  # type: ignore[misc]
                                    )
                                else:
                                    retry_after_int = None
                            except Exception:
                                retry_after_int = None
                    _raise(RateLimitError(retry_after=retry_after_int))

                if response.status_code == 503:
                    msg = "Service temporarily unavailable"
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = None
                    if retry_after:
                        try:
                            retry_after_int = (
                                int(retry_after)
                                if isinstance(retry_after, str | int)
                                else None
                            )
                        except (ValueError, TypeError):
                            retry_after_int = None
                    _raise(
                        TemporaryError(
                            msg, status_code=503, retry_after=retry_after_int
                        )
                    )

                if response.status_code in (502, 504):
                    msg = f"Server error {response.status_code}: Service unavailable"
                    _raise(ServerError(msg, status_code=response.status_code))

                if 500 <= response.status_code < 600:
                    msg = (
                        f"Server error {response.status_code}: {response.text}"
                    )
                    _raise(ServerError(msg, status_code=response.status_code))

            except (ServerError, TemporaryError, RateLimitError) as e:
                attempt += 1
                if attempt > max_attempts:
                    raise

                if isinstance(e, RateLimitError) and e.retry_after:
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
            else:
                return response

        msg = "Retry logic failed unexpectedly"
        raise RuntimeError(msg)

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


_connections: dict[
    int, tuple[weakref.ReferenceType[OpenAlexConfig], Connection]
] = {}
_async_connections: dict[
    int, tuple[weakref.ReferenceType[OpenAlexConfig], AsyncConnection]
] = {}


def get_connection(config: OpenAlexConfig) -> Connection:
    key = id(config)
    entry = _connections.get(key)
    if entry is not None:
        ref, conn = entry
        if ref() is config:
            return conn
        if ref() is None:
            del _connections[key]
    conn = Connection(config)
    _connections[key] = (weakref.ref(config), conn)
    return conn


async def get_async_connection(config: OpenAlexConfig) -> AsyncConnection:
    key = id(config)
    entry = _async_connections.get(key)
    if entry is not None:
        ref, conn = entry
        if ref() is config:
            return conn
        if ref() is None:
            del _async_connections[key]
    conn = AsyncConnection(config)
    _async_connections[key] = (weakref.ref(config), conn)
    return conn


async def close_all_async_connections() -> None:
    """Close all async connections."""
    for key, (ref, connection) in list(_async_connections.items()):
        await connection.close()
        if ref() is None:
            del _async_connections[key]
