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
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_exponential_jitter,
)

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

    def get_wait_strategy(self) -> Any:
        """Return the appropriate tenacity wait strategy."""
        return (
            wait_exponential_jitter(
                initial=self.initial_wait,
                max=self.max_wait,
                exp_base=self.multiplier,
            )
            if self.jitter
            else wait_exponential(
                multiplier=self.initial_wait,
                max=self.max_wait,
                exp_base=self.multiplier,
            )
        )


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
        self = args[0]
        max_attempts = 5
        if hasattr(self, "config"):
            config = self.config
            if getattr(config, "retry_enabled", True):
                max_attempts = getattr(config, "retry_max_attempts", 5)
            else:
                max_attempts = 1
        attempt = 0

        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededError as e:
                attempt += 1
                if attempt >= max_attempts:
                    raise

                wait_time = e.retry_after or (2**attempt)
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

                wait_time = min(60, 2**attempt)
                logger.warning(
                    "server_error",
                    error=str(e),
                    wait_time=wait_time,
                    attempt=attempt,
                )
                time.sleep(wait_time)

        raise RuntimeError(RETRY_FAIL_MSG)

    return wrapper


def exponential_backoff(
    attempt: int,
    *,
    initial: float = 1.0,
    multiplier: float = 2.0,
    max_wait: float | None = None,
) -> float:
    """Calculate exponential backoff time."""
    wait = initial * (multiplier ** (attempt - 1))
    if max_wait is not None:
        wait = min(wait, max_wait)
    return wait


def linear_backoff(
    attempt: int,
    *,
    initial: float = 1.0,
    increment: float = 1.0,
    max_wait: float | None = None,
) -> float:
    """Calculate linear backoff time."""
    wait = initial + increment * (attempt - 1)
    if max_wait is not None:
        wait = min(wait, max_wait)
    return wait


def constant_backoff(_attempt: int, *, wait: float = 1.0) -> float:
    """Return a constant backoff regardless of ``attempt``."""
    return wait


class RetryContext:
    """Simple context manager to manually control retries."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        self.config = config or RetryConfig()
        self.attempt = 0
        self.last_error: BaseException | None = None
        self.succeeded = False

    def __enter__(self) -> RetryContext:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        if exc is not None:
            self.record_error(exc)
            return

        if not self.succeeded:
            if self.attempt >= self.config.max_attempts and self.last_error:
                raise self.last_error
            self.succeeded = True
        return

    def should_retry(self) -> bool:
        return self.attempt < self.config.max_attempts and not self.succeeded

    def record_error(self, error: BaseException) -> None:
        self.last_error = error
        self.attempt += 1
