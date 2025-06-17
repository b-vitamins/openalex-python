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
    """Configuration for retry behavior.

    IMPORTANT: max_attempts is the TOTAL number of attempts including the first try.
    So max_attempts=3 means: 1 initial attempt + 2 retries.
    """

    max_attempts: int = 3
    initial_wait: float = 1.0
    max_wait: float = 60.0
    multiplier: float = 2.0
    jitter: bool = True

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_attempts < 1:
            msg = "max_attempts must be at least 1"
            raise ValueError(msg)
        if self.initial_wait < 0:
            msg = "initial_wait must be non-negative"
            raise ValueError(msg)
        if self.max_wait < self.initial_wait:
            msg = "max_wait must be >= initial_wait"
            raise ValueError(msg)
        if self.multiplier < 1.0:
            msg = "multiplier must be >= 1.0"
            raise ValueError(msg)


class RetryHandler:
    """Handler for retry logic with rate limit awareness."""

    __slots__ = ("_rate_limit_reset", "config")

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize retry handler."""
        self.config = config or RetryConfig()
        self._rate_limit_reset: float | None = None

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if request should be retried.

        Args:
            error: The exception that occurred
            attempt: Current attempt number (1-based)

        Returns:
            True if should retry, False otherwise
        """
        # CRITICAL: Check >= not > to prevent off-by-one error
        if attempt >= self.config.max_attempts:
            logger.debug(
                "max_attempts_reached",
                attempt=attempt,
                max_attempts=self.config.max_attempts,
            )
            return False

        should_retry = is_retryable_error(error)
        logger.debug(
            "retry_decision",
            attempt=attempt,
            max_attempts=self.config.max_attempts,
            error_type=type(error).__name__,
            should_retry=should_retry,
        )
        return should_retry

    def calculate_wait(self, attempt: int) -> float:
        """Calculate base wait time for ``attempt``."""
        # attempt is 1-based, so subtract 1 for exponential calculation
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
        logger.debug("retry_wait_async", seconds=seconds)
        await asyncio.sleep(seconds)

    def wait_sync(self, seconds: float) -> None:
        """Synchronous wait for specified seconds."""
        logger.debug("retry_wait_sync", seconds=seconds)
        time.sleep(seconds)


def with_retry(
    func: Callable[..., T], config: RetryConfig | None = None
) -> Callable[..., T]:
    """Decorator to add retry logic to a function.

    CRITICAL: This properly tracks attempts to avoid infinite loops.
    """
    if config is None:
        config = RetryConfig()

    handler = RetryHandler(config)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_error: Exception | None = None

        # CRITICAL: Start at attempt 1, not 0
        for attempt in range(1, config.max_attempts + 1):
            try:
                logger.debug(
                    "retry_attempt",
                    attempt=attempt,
                    max_attempts=config.max_attempts,
                    func=func.__name__,
                )
                return func(*args, **kwargs)
            except Exception as exc:
                last_error = exc

                # Check if we should retry BEFORE waiting
                if not handler.should_retry(exc, attempt):
                    logger.debug(
                        "retry_exhausted",
                        attempt=attempt,
                        error_type=type(exc).__name__,
                    )
                    raise

                # Only wait if we're not on the last attempt
                if attempt < config.max_attempts:
                    wait_time = handler.get_wait_time(exc, attempt)
                    handler.wait_sync(wait_time)

        # This should never be reached due to the logic above
        raise last_error or RuntimeError("Retry logic error")

    return wrapper


def async_with_retry(
    func: Callable[..., Awaitable[T]],
    config: RetryConfig | None = None,
) -> Callable[..., Awaitable[T]]:
    """Async decorator to add retry logic to a function."""
    if config is None:
        config = RetryConfig()

    handler = RetryHandler(config)

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        last_error: Exception | None = None

        # CRITICAL: Start at attempt 1, not 0
        for attempt in range(1, config.max_attempts + 1):
            try:
                logger.debug(
                    "retry_attempt_async",
                    attempt=attempt,
                    max_attempts=config.max_attempts,
                    func=func.__name__,
                )
                return await func(*args, **kwargs)
            except Exception as exc:
                last_error = exc

                # Check if we should retry BEFORE waiting
                if not handler.should_retry(exc, attempt):
                    logger.debug(
                        "retry_exhausted_async",
                        attempt=attempt,
                        error_type=type(exc).__name__,
                    )
                    raise

                # Only wait if we're not on the last attempt
                if attempt < config.max_attempts:
                    wait_time = handler.get_wait_time(exc, attempt)
                    await handler.wait(wait_time)

        # This should never be reached
        raise last_error or RuntimeError("Retry logic error")

    return wrapper


class RetryContext:
    """Context manager for retry operations with explicit attempt tracking."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize retry context."""
        self.config = config or RetryConfig()
        self.handler = RetryHandler(self.config)
        self.attempt = 0
        self.last_error: BaseException | None = None
        self.succeeded = False
        self._entered = False

    def __enter__(self) -> RetryContext:
        """Enter retry context."""
        self._entered = True
        self.attempt = 0
        self.last_error = None
        self.succeeded = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        """Handle exception in retry context."""
        if exc_val is not None:
            self.record_error(exc_val)
            if not self.should_retry():
                return False
            wait_time = self.handler.get_wait_time(cast(Exception, exc_val), self.attempt)
            self.handler.wait_sync(wait_time)
            return True

        if not self.succeeded:
            if self.attempt >= self.config.max_attempts and self.last_error:
                raise self.last_error
            self.succeeded = True
        return False

    async def __aenter__(self) -> RetryContext:
        """Enter async retry context."""
        self._entered = True
        self.attempt = 0
        self.last_error = None
        self.succeeded = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        """Handle exception in async retry context."""
        if exc_val is not None:
            self.record_error(exc_val)
            if not self.should_retry():
                return False
            wait_time = self.handler.get_wait_time(cast(Exception, exc_val), self.attempt)
            await self.handler.wait(wait_time)
            return True

        if not self.succeeded:
            if self.attempt >= self.config.max_attempts and self.last_error:
                raise self.last_error
            self.succeeded = True
        return False

    def should_retry(self) -> bool:
        """Return ``True`` if another attempt should be made."""
        return self.attempt < self.config.max_attempts and not self.succeeded

    def record_error(self, error: BaseException) -> None:
        """Record an error and increment attempt counter."""
        self.last_error = error
        self.attempt += 1


# Convenience decorators

def retry_on_error(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 60.0,
    *,
    jitter: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Simplified decorator for retry logic."""
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
    max_attempts: int = 3,
    *,
    respect_retry_after: bool = True,
) -> Callable[..., T]:
    """Decorator specifically for handling rate limits."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_error: Exception | None = None

        attempts = max_attempts
        if args:
            self_obj = args[0]
            cfg = getattr(self_obj, "config", None)
            if cfg is not None:
                if getattr(cfg, "retry_enabled", True):
                    attempts = getattr(cfg, "retry_max_attempts", attempts - 1) + 1
                else:
                    attempts = 1

        for attempt in range(1, attempts + 1):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                last_error = e
                if attempt >= max_attempts:
                    raise

                wait_time = (
                    float(e.retry_after) if e.retry_after and respect_retry_after else 60.0
                )
                logger.warning(
                    "rate_limit_hit",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    wait_time=wait_time,
                )
                time.sleep(wait_time)
            except Exception as e:
                if not is_retryable_error(e):
                    raise
                last_error = e
                if attempt >= max_attempts:
                    raise

                wait_time = min(2 ** (attempt - 1), 60)
                time.sleep(wait_time)

        raise last_error or RuntimeError("Retry failed")

    return wrapper


# Backoff strategies

def constant_backoff(delay: float = 1.0) -> RetryConfig:
    """Create config for constant backoff."""
    return RetryConfig(initial_wait=delay, multiplier=1.0, jitter=False)


def linear_backoff(initial: float = 1.0, increment: float = 1.0) -> RetryConfig:
    """Create config for linear backoff."""
    return RetryConfig(initial_wait=initial, multiplier=1.0 + increment, jitter=False)


def exponential_backoff(initial: float = 1.0, base: float = 2.0, max_wait: float = 60.0) -> RetryConfig:
    """Create config for exponential backoff."""
    return RetryConfig(initial_wait=initial, multiplier=base, max_wait=max_wait)
