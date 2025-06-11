"""Utility functions and classes for OpenAlex client."""

from ..constants import (
    DOI_URL_PREFIX,
    MAG_PREFIX,
    OPENALEX_ID_PREFIX,
    ORCID_URL_PREFIX,
    PMID_PREFIX,
)
from .common import (
    empty_list_result,
    ensure_prefix,
    is_openalex_id,
    strip_id_prefix,
)
from .pagination import AsyncPaginator, Paginator
from .params import normalize_params
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
    retry_on_error,
    retry_with_rate_limit,
)
from .text import invert_abstract

__all__ = [
    "DOI_URL_PREFIX",
    "MAG_PREFIX",
    "OPENALEX_ID_PREFIX",
    "ORCID_URL_PREFIX",
    "PMID_PREFIX",
    "AsyncPaginator",
    "AsyncRateLimiter",
    "Paginator",
    "RateLimiter",
    "RetryConfig",
    "RetryHandler",
    "SlidingWindowRateLimiter",
    "async_rate_limited",
    "async_with_retry",
    "empty_list_result",
    "ensure_prefix",
    "invert_abstract",
    "is_openalex_id",
    "is_retryable_error",
    "normalize_params",
    "rate_limited",
    "retry_on_error",
    "retry_with_rate_limit",
    "strip_id_prefix",
    "with_retry",
]
