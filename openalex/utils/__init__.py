"""Utility functions and classes for OpenAlex client."""

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
    # Pagination
    "Paginator",
    # Rate limiting
    "RateLimiter",
    # Retry
    "RetryConfig",
    "RetryHandler",
    "SlidingWindowRateLimiter",
    "async_rate_limited",
    "async_with_retry",
    "is_retryable_error",
    "rate_limited",
    "with_retry",
]
