"""Utility functions and classes for OpenAlex client."""

from .common import normalize_params, strip_id_prefix
from .pagination import AsyncPaginator, Paginator
from .rate_limit import (
    AsyncRateLimiter,
    RateLimiter,
    SlidingWindowRateLimiter,
    async_rate_limited,
    rate_limited,
)
from .retry import (
    RetryConfig,
    RetryHandler,
    async_with_retry,
    is_retryable_error,
    with_retry,
)

__all__ = [
    "AsyncPaginator",
    "AsyncRateLimiter",
    "Paginator",
    "RateLimiter",
    "RetryConfig",
    "RetryHandler",
    "SlidingWindowRateLimiter",
    "async_rate_limited",
    "async_with_retry",
    "is_retryable_error",
    "normalize_params",
    "rate_limited",
    "strip_id_prefix",
    "with_retry",
]
