"""Retry logic for OpenAlex API requests."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Final, TypeVar

from structlog import get_logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_exponential_jitter,
)

from ..constants import UNREACHABLE_MSG
from ..exceptions import (
    APIError,
    NetworkError,
    RateLimitError,
    RateLimitExceededError,
    RetryableError,
    ServerError,
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
    "RetryHandler",
    "async_with_retry",
    "is_retryable_error",
    "retry_on_error",
    "retry_with_rate_limit",
    "with_retry",
]


def is_retryable_error(error: BaseException) -> bool:
    """Return ``True`` if ``error`` should trigger a retry."""
    if isinstance(error, RateLimitError | NetworkError | TimeoutError):
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
    exponential_base: float = 2.0
    jitter: bool = True

    def get_wait_strategy(self) -> Any:
        """Return the appropriate tenacity wait strategy."""
        return (
            wait_exponential_jitter(
                initial=self.initial_wait,
                max=self.max_wait,
                exp_base=self.exponential_base,
            )
            if self.jitter
            else wait_exponential(
                multiplier=self.initial_wait,
                max=self.max_wait,
                exp_base=self.exponential_base,
            )
        )


def with_retry(
    func: Callable[..., T],
    config: RetryConfig | None = None,
) -> Callable[..., T]:
    """Decorator to add retry logic to a function.

    Args:
        func: Function to retry
        config: Retry configuration

    Returns:
        Wrapped function with retry logic
    """
    if config is None:
        config = RetryConfig()

    def wrapper(*args: Any, **kwargs: Any) -> T:
        """Wrapper with retry logic."""
        retrying = Retrying(
            stop=stop_after_attempt(config.max_attempts),
            wait=config.get_wait_strategy(),
            retry=retry_if_exception(is_retryable_error),
            before_sleep=lambda retry_state: logger.info(
                "Retrying request",
                attempt=retry_state.attempt_number,
                wait=retry_state.next_action.sleep
                if retry_state.next_action
                else 0,
            ),
        )

        try:
            for attempt in retrying:
                with attempt:
                    return func(*args, **kwargs)
        except RetryError as e:
            if e.last_attempt.failed:
                exc = e.last_attempt.result()
                raise exc from e
            raise

        raise AssertionError(UNREACHABLE_MSG)

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

    async def wrapper(*args: Any, **kwargs: Any) -> T:
        """Async wrapper with retry logic."""
        retrying = AsyncRetrying(
            stop=stop_after_attempt(config.max_attempts),
            wait=config.get_wait_strategy(),
            retry=retry_if_exception(is_retryable_error),
            before_sleep=lambda retry_state: logger.info(
                "Retrying request",
                attempt=retry_state.attempt_number,
                wait=retry_state.next_action.sleep
                if retry_state.next_action
                else 0,
            ),
        )

        try:
            async for attempt in retrying:
                with attempt:
                    return await func(*args, **kwargs)
        except RetryError as e:
            if e.last_attempt.failed:
                exc = e.last_attempt.result()
                raise exc from e
            raise

        raise AssertionError(UNREACHABLE_MSG)

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

    def get_wait_time(self, error: Exception, attempt: int) -> float:
        """Calculate wait time before next retry."""
        # Handle rate limit errors specially
        if isinstance(error, RateLimitError) and error.retry_after:
            return float(error.retry_after)

        # Exponential backoff with jitter
        base_wait = self.config.initial_wait * (
            self.config.exponential_base ** (attempt - 1)
        )
        wait_time = min(base_wait, self.config.max_wait)

        if self.config.jitter:
            jitter = wait_time * JITTER_FACTOR
            wait_time += random.uniform(-jitter, jitter)

        return max(0, wait_time)

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


def create_retry_decorator(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a retry decorator with configurable parameters."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            retry_instance = Retrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=initial_wait,
                    max=max_wait,
                    exp_base=exponential_base,
                ),
                retry=retry_if_exception_type(RetryableError),
                before=before_retry_log,
                reraise=True,
            )

            try:
                for attempt in retry_instance:
                    with attempt:
                        return func(*args, **kwargs)
            except RetryError as e:
                exc = e.last_attempt.exception()
                if isinstance(exc, BaseException):
                    raise exc from None
                raise RuntimeError(RETRY_FAIL_MSG) from None

            raise RuntimeError(RETRY_FAIL_MSG)

        return wrapper

    return decorator


# Default retry decorator
retry_on_error = create_retry_decorator()


def retry_with_rate_limit(func: Callable[..., T]) -> Callable[..., T]:
    """Retry decorator that respects rate limit headers."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededError as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise

                wait_time = e.retry_after or (2 ** attempt)
                logger.warning(
                    "rate_limit_hit",
                    retry_after=e.retry_after,
                    wait_time=wait_time,
                    attempt=attempt,
                )
                time.sleep(wait_time)
            except ServerError as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise

                wait_time = min(60, 2 ** attempt)
                logger.warning(
                    "server_error",
                    error=str(e),
                    wait_time=wait_time,
                    attempt=attempt,
                )
                time.sleep(wait_time)

        raise RuntimeError(RETRY_FAIL_MSG)

    return wrapper

