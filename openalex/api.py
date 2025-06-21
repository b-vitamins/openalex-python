"""Direct API interface for OpenAlex."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

import httpx
from structlog import get_logger

__all__ = ["APIConnection", "AsyncAPIConnection", "get_connection"]

from httpx import Response

from .cache.manager import get_cache_manager
from .config import OpenAlexConfig
from .constants import (
    AUTOCOMPLETE_PATH,
    DEFAULT_RATE_LIMIT,
    HTTP_METHOD_GET,
    PARAM_Q,
    RANDOM_PATH,
)
from .exceptions import (
    APIError,
    NetworkError,
    ServerError,
    TimeoutError,
    raise_for_status,
)
from .utils import AsyncRateLimiter, RateLimiter, strip_id_prefix
from .utils.params import normalize_params
from .utils.retry import (
    RetryConfig,
    async_with_retry,
    retry_with_rate_limit,
)

if TYPE_CHECKING:
    from .connection import AsyncConnection
    from .resilience import CircuitBreaker, RequestQueue

T = TypeVar("T")

logger = get_logger(__name__)


class APIConnection:
    """Handles direct API communication."""

    __slots__ = (
        "_circuit_breaker",
        "_client",
        "_request_queue",
        "config",
        "rate_limiter",
        "retry_config",
    )

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self.rate_limiter = RateLimiter(DEFAULT_RATE_LIMIT)
        self.retry_config = RetryConfig()
        self._client: httpx.Client | None = None

        self._circuit_breaker: CircuitBreaker | None
        self._request_queue: RequestQueue | None

        if self.config.circuit_breaker_enabled:
            from .resilience import CircuitBreaker

            self._circuit_breaker = CircuitBreaker(
                failure_threshold=self.config.circuit_breaker_failure_threshold,
                recovery_timeout=self.config.circuit_breaker_recovery_timeout,
                expected_exception=(ServerError, NetworkError),
            )
        else:
            self._circuit_breaker = None

        if self.config.request_queue_enabled:
            from .resilience import RequestQueue

            self._request_queue = RequestQueue(
                max_size=self.config.request_queue_max_size
            )
            self._request_queue.set_rate_limiter(self.rate_limiter)
            self._request_queue.start()
        else:
            self._request_queue = None

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

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> Response:
        if operation is None:
            if "/autocomplete/" in url:
                operation = "autocomplete"
            elif method == "GET" and url.count("/") > 3:
                operation = "get"
            elif params and (
                (
                    isinstance(params.get("filter"), dict)
                    and "search" in params["filter"]
                )
                or params.get("search")
            ):
                operation = "search"
            else:
                operation = "list"

        if self._request_queue is not None:
            return cast(
                Response,
                self._request_queue.enqueue(
                    self._protected_request,
                    method,
                    url,
                    params,
                    operation=operation,
                    **kwargs,
                ),
            )
        return self._protected_request(
            method, url, params, operation=operation, **kwargs
        )

    def _protected_request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        operation: str | None = None,
        **kwargs: Any,
    ) -> Response:
        if self._circuit_breaker is not None:
            return cast(
                httpx.Response,
                self._circuit_breaker.call(
                    self._do_request,
                    method,
                    url,
                    params,
                    operation=operation,
                    **kwargs,
                ),
            )
        return self._do_request(
            method, url, params, operation=operation, **kwargs
        )

    @retry_with_rate_limit
    def _do_request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        operation = kwargs.pop("operation", None)
        params = self._default_params(params)
        kwargs["headers"] = self._default_headers(kwargs.get("headers"))

        wait = self.rate_limiter.acquire()
        if wait > 0:
            time.sleep(wait)

        metrics = None
        start_time = 0.0
        endpoint = "unknown"
        if self.config.collect_metrics:
            from .metrics import get_metrics_collector

            metrics = get_metrics_collector(self.config)
            start_time = time.time()
            endpoint = url.split("/")[-2] if "/" in url else "unknown"

        timeout_value = self.config.operation_timeouts.get(
            cast(str, operation), self.config.timeout
        )

        try:
            if (
                self.config.middleware.request_interceptors
                or self.config.middleware.response_interceptors
            ):
                request = self.client.build_request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=httpx.Timeout(timeout_value),
                    **kwargs,
                )
                for (
                    req_interceptor
                ) in self.config.middleware.request_interceptors:
                    request = req_interceptor.process_request(request)
                response = self.client.send(request)
                raise_for_status(response)
                for (
                    resp_interceptor
                ) in self.config.middleware.response_interceptors:
                    response = resp_interceptor.process_response(response)
            else:
                response = self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=httpx.Timeout(timeout_value),
                    **kwargs,
                )
                raise_for_status(response)
        except httpx.TimeoutException as e:
            if metrics is not None:
                duration = time.time() - start_time
                metrics.record_request(endpoint, duration, success=False)
            msg = f"Request timed out after {timeout_value}s"
            raise TimeoutError(
                msg,
                operation=cast(str | None, operation),
                timeout_value=timeout_value,
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

    def close(self) -> None:
        if self._client:
            self._client.close()
        if self._request_queue is not None:
            self._request_queue.stop()

    def __enter__(self) -> APIConnection:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAPIConnection:
    """Async version of API connection."""

    __slots__ = (
        "_client",
        "_request_queue",
        "config",
        "rate_limiter",
        "retry_config",
    )

    def __init__(self, config: OpenAlexConfig | None = None) -> None:
        self.config = config or OpenAlexConfig()
        self.rate_limiter = AsyncRateLimiter(DEFAULT_RATE_LIMIT)
        self.retry_config = RetryConfig()
        self._client: httpx.AsyncClient | None = None
        if self.config.request_queue_enabled:
            from .resilience import AsyncRequestQueue

            self._request_queue: AsyncRequestQueue | None = AsyncRequestQueue(
                max_size=self.config.request_queue_max_size
            )
            self._request_queue.set_rate_limiter(self.rate_limiter)
        else:
            self._request_queue = None

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
        if self._request_queue is not None:
            self._request_queue.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
        if self._request_queue is not None:
            await self._request_queue.stop()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()
        if self._request_queue is not None:
            await self._request_queue.stop()

    async def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        """Make async HTTP request with retry and rate limiting."""
        if self._request_queue is not None:
            return cast(
                Response,
                await self._request_queue.enqueue(
                    self._protected_request, method, url, params, **kwargs
                ),
            )
        return await self._protected_request(method, url, params, **kwargs)

    async def _protected_request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
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
                if (
                    self.config.middleware.request_interceptors
                    or self.config.middleware.response_interceptors
                ):
                    request = self._client.build_request(
                        method,
                        url,
                        params=params,
                        timeout=self.config.timeout,
                        **kwargs,
                    )
                    for (
                        req_interceptor
                    ) in self.config.middleware.request_interceptors:
                        request = req_interceptor.process_request(request)
                    response = await self._client.send(request)
                else:
                    response = await self._client.request(
                        method,
                        url,
                        params=params,
                        timeout=self.config.timeout,
                        **kwargs,
                    )
                raise_for_status(response)
            except httpx.TimeoutException as e:  # pragma: no cover - network
                raise TimeoutError(str(e)) from e
            except httpx.RequestError as e:  # pragma: no cover - network
                raise NetworkError(str(e)) from e
            else:
                for (
                    resp_interceptor
                ) in self.config.middleware.response_interceptors:
                    response = resp_interceptor.process_response(response)
                return response

        return await async_with_retry(make_request, self.retry_config)()


_connection_pool: dict[str, APIConnection] = {}


def get_connection(config: OpenAlexConfig | None = None) -> APIConnection:
    """Get or create an API connection."""
    key = str(config) if config else "default"
    if key not in _connection_pool:
        _connection_pool[key] = APIConnection(config)
    return _connection_pool[key]


class AsyncBaseAPI(Generic[T]):
    """Base class for async API endpoints."""

    endpoint: str = ""
    model_class: type[T]

    def __init__(self, config: OpenAlexConfig) -> None:
        self._config = config
        self._base_url = str(config.base_url).rstrip("/")

    async def _get_connection(self) -> AsyncConnection:
        from .connection import get_async_connection

        return await get_async_connection(self._config)

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}/{path}"

    async def get_single_entity(
        self,
        entity_id: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entity_id = strip_id_prefix(entity_id)
        endpoint = f"{self.endpoint}/{entity_id}"

        cache_manager = get_cache_manager(self._config)

        async def fetch() -> dict[str, Any]:
            connection = await self._get_connection()
            url = self._build_url(endpoint)
            params_norm = normalize_params(params or {})
            response = await connection.request(
                HTTP_METHOD_GET, url, params=params_norm
            )
            raise_for_status(response)
            return cast("dict[str, Any]", response.json())

        cache_key = None
        if cache_manager.enabled:
            from .cache.base import CacheKeyBuilder

            cache_key = CacheKeyBuilder.build_key(
                self.endpoint, entity_id, params
            )
            cached = (
                cache_manager.cache.get(cache_key)
                if cache_manager.cache
                else None
            )
            if cached is not None:
                return cast("dict[str, Any]", cached)

        data = await fetch()

        if (
            cache_manager.enabled
            and cache_manager.cache
            and cache_key is not None
        ):
            ttl = cache_manager.get_ttl_for_endpoint(self.endpoint)
            cache_manager.cache.set(cache_key, data, ttl)

        return data

    async def get_list(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        connection = await self._get_connection()
        url = self._build_url(self.endpoint)
        params_norm = normalize_params(params or {})
        response = await connection.request(
            HTTP_METHOD_GET, url, params=params_norm
        )
        raise_for_status(response)
        return cast("dict[str, Any]", response.json())

    async def autocomplete(
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        connection = await self._get_connection()
        url = self._build_url(f"{AUTOCOMPLETE_PATH}/{self.endpoint}")
        params_norm = normalize_params(params or {})
        params_norm[PARAM_Q] = query
        response = await connection.request(
            HTTP_METHOD_GET, url, params=params_norm
        )
        raise_for_status(response)
        return cast("dict[str, Any]", response.json())

    async def random(self) -> dict[str, Any]:
        connection = await self._get_connection()
        url = self._build_url(f"{self.endpoint}/{RANDOM_PATH}")
        response = await connection.request(HTTP_METHOD_GET, url)
        raise_for_status(response)
        return cast("dict[str, Any]", response.json())
