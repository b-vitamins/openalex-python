"""Retry logic for OpenAlex API requests."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Final, TypeVar, cast

from structlog import get_logger

from ..exceptions import (
    APIError,
    NetworkError,
    RateLimitError,
    RateLimitExceededError,
    RetryableError,
    TimeoutError,
)

RETRY_FAIL_MSG: Final = "Retry logic failed unexpectedly"

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger(__name__)

JITTER_FACTOR: Final = 0.25

T = TypeVar("T")

__all__ = [
    "RetryConfig",
    "RetryContext",
    "RetryHandler",
    "async_with_retry",
    "constant_backoff",
    "exponential_backoff",
    "is_retryable_error",
    "linear_backoff",
    "retry_on_error",
    "retry_with_rate_limit",
    "with_retry",
]


def is_retryable_error(error: BaseException) -> bool:
    """Return ``True`` if ``error`` should trigger a retry."""
    if isinstance(
        error, RateLimitError | NetworkError | TimeoutError | RetryableError
    ):
        return True
    if isinstance(error, APIError):
        return error.status_code is not None and error.status_code >= 500
    return False


@dataclass(slots=True)
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_wait: float = 1.0
    max_wait: float = 60.0
    multiplier: float = 2.0
    jitter: bool = True


def with_retry(
    func: Callable[..., T], config: RetryConfig | None = None
) -> Callable[..., T]:
    """Decorator to add retry logic to a function."""

    handler = RetryHandler(config)

    def wrapper(*args: Any, **kwargs: Any) -> T:
        attempt = 1
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if not handler.should_retry(exc, attempt):
                    raise
                wait_time = handler.get_wait_time(exc, attempt)
                handler.wait_sync(wait_time)
                attempt += 1

    return wrapper


def async_with_retry(
    func: Callable[..., Awaitable[T]],
    config: RetryConfig | None = None,
) -> Callable[..., Awaitable[T]]:
    """Async decorator to add retry logic to a function.

    Args:
        func: Async function to retry
        config: Retry configuration

    Returns:
        Wrapped async function with retry logic
    """
    if config is None:
        config = RetryConfig()
    handler = RetryHandler(config)

    async def wrapper(*args: Any, **kwargs: Any) -> T:
        attempt = 1
        while True:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                if not handler.should_retry(exc, attempt):
                    raise
                wait_time = handler.get_wait_time(exc, attempt)
                await handler.wait(wait_time)
                attempt += 1

    return wrapper


class RetryHandler:
    """Handler for retry logic with rate limit awareness."""

    __slots__ = ("_rate_limit_reset", "config")

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize retry handler."""
        self.config = config or RetryConfig()
        self._rate_limit_reset: float | None = None

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if request should be retried."""
        if attempt >= self.config.max_attempts:
            return False

        return is_retryable_error(error)

    def calculate_wait(self, attempt: int) -> float:
        """Calculate base wait time for ``attempt``."""
        base_wait = self.config.initial_wait * (
            self.config.multiplier ** (attempt - 1)
        )
        wait_time = min(base_wait, self.config.max_wait)

        if self.config.jitter:
            jitter = wait_time * JITTER_FACTOR
            wait_time += random.uniform(-jitter, jitter)

        return max(0.0, wait_time)

    def get_wait_time(self, error: Exception, attempt: int) -> float:
        """Calculate wait time before next retry."""
        if isinstance(error, RateLimitError) and error.retry_after:
            return float(error.retry_after)

        return self.calculate_wait(attempt)

    async def wait(self, seconds: float) -> None:
        """Wait for specified seconds."""
        logger.debug("Waiting %.2f seconds before retry", seconds)
        await asyncio.sleep(seconds)

    def wait_sync(self, seconds: float) -> None:
        """Synchronous wait for specified seconds."""
        logger.debug("Waiting %.2f seconds before retry", seconds)
        time.sleep(seconds)


# ---------------------------------------------------------------------------
# Additional retry utilities used for connection-level retries
# ---------------------------------------------------------------------------


def is_retryable_error_simple(exception: Exception) -> bool:
    """Check if an error should trigger a retry based on class hierarchy."""
    return isinstance(exception, RetryableError)


def get_retry_after(exception: Exception) -> int | None:
    """Extract retry-after value from exception."""
    if isinstance(exception, RateLimitExceededError):
        return exception.retry_after
    return None


def before_retry_log(retry_state: Any) -> None:
    """Log before retry attempt."""
    attempt = retry_state.attempt_number
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    wait_time = retry_state.next_action.sleep if retry_state.next_action else 0

    logger.warning(
        "retrying_request",
        attempt=attempt,
        exception_type=type(exception).__name__ if exception else None,
        exception_message=str(exception) if exception else "",
        wait_seconds=wait_time,
    )






class RetryContext:
    """Context manager for retry operations."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize retry context."""
        self.config = config or RetryConfig()
        self.handler = RetryHandler(self.config)
        self.attempt = 0

    def __enter__(self) -> RetryContext:
        """Enter retry context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        """Handle exception in retry context."""
        if exc_type is None:
            return False

        self.attempt += 1
        if not self.handler.should_retry(cast("Exception", exc_val), self.attempt):
            return False

        wait_time = self.handler.get_wait_time(cast("Exception", exc_val), self.attempt)
        self.handler.wait_sync(wait_time)
        return True  # Suppress exception to retry

    async def __aenter__(self) -> RetryContext:
        """Enter async retry context."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        """Handle exception in async retry context."""
        if exc_type is None:
            return False

        self.attempt += 1
        if not self.handler.should_retry(cast("Exception", exc_val), self.attempt):
            return False

        wait_time = self.handler.get_wait_time(cast("Exception", exc_val), self.attempt)
        await self.handler.wait(wait_time)
        return True  # Suppress exception to retry


def retry_on_error(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 60.0,
    *,
    jitter: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Simplified decorator for retry logic.

    Args:
        retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        jitter: Whether to add random jitter

    Returns:
        Decorated function with retry logic
    """
    config = RetryConfig(
        max_attempts=retries,
        initial_wait=delay,
        multiplier=backoff,
        max_wait=max_delay,
        jitter=jitter,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return with_retry(func, config)

    return decorator


def retry_with_rate_limit(
    func: Callable[..., T],
    max_attempts: int | None = None,
    *,
    respect_retry_after: bool = True,
) -> Callable[..., T]:
    """Decorator specifically for handling rate limits.

    Args:
        func: Function to wrap
        max_attempts: Maximum retry attempts
        respect_retry_after: Whether to respect Retry-After headers

    Returns:
        Wrapped function with rate limit handling
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        self_obj = args[0] if args else None
        if max_attempts is None and hasattr(self_obj, "config"):
            cfg = self_obj.config
            attempts = cfg.retry_max_attempts if cfg.retry_enabled else 1
        else:
            attempts = max_attempts or 1

        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                last_error = e
                if attempt >= attempts:
                    raise

                wait_time = float(e.retry_after) if e.retry_after and respect_retry_after else 60.0
                logger.warning(
                    "rate_limit_hit",
                    attempt=attempt,
                    max_attempts=attempts,
                    wait_time=wait_time,
                )
                time.sleep(wait_time)
            except Exception as e:
                if not is_retryable_error(e):
                    raise
                last_error = e
                if attempt >= attempts:
                    raise

                wait_time = min(2 ** (attempt - 1), 60)
                time.sleep(wait_time)

        raise last_error or RuntimeError("Retry failed")

    return wrapper


# Backoff strategies for convenience
def constant_backoff(delay: float = 1.0) -> RetryConfig:
    """Create config for constant backoff."""
    return RetryConfig(initial_wait=delay, multiplier=1.0, jitter=False)


def linear_backoff(initial: float = 1.0, increment: float = 1.0) -> RetryConfig:
    """Create config for linear backoff."""
    return RetryConfig(initial_wait=initial, multiplier=1.0 + increment, jitter=False)


def exponential_backoff(initial: float = 1.0, base: float = 2.0, max_wait: float = 60.0) -> RetryConfig:
    """Create config for exponential backoff."""
    return RetryConfig(initial_wait=initial, multiplier=base, max_wait=max_wait)
