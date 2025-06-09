"""Retry logic for OpenAlex API requests."""

from __future__ import annotations

import asyncio
import random
import time
from typing import TYPE_CHECKING, Any, TypeVar

from structlog import get_logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    wait_exponential_jitter,
)

from ..exceptions import APIError, NetworkError, RateLimitError, TimeoutError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger(__name__)

T = TypeVar("T")

__all__ = [
    "RetryConfig",
    "RetryHandler",
    "async_with_retry",
    "is_retryable_error",
    "with_retry",
]


def is_retryable_error(error: BaseException) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, RateLimitError):
        return True

    if isinstance(error, NetworkError | TimeoutError):
        return True

    if isinstance(error, APIError):
        # Retry on server errors
        return error.status_code is not None and error.status_code >= 500

    return False


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_wait: float = 1.0,
        max_wait: float = 60.0,
        exponential_base: float = 2.0,
        *,
        jitter: bool = True,
    ) -> None:
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of attempts
            initial_wait: Initial wait time in seconds
            max_wait: Maximum wait time in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add jitter to wait times
        """
        self.max_attempts = max_attempts
        self.initial_wait = initial_wait
        self.max_wait = max_wait
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_wait_strategy(self) -> Any:
        """Get tenacity wait strategy."""
        if self.jitter:
            return wait_exponential_jitter(
                initial=self.initial_wait,
                max=self.max_wait,
                exp_base=self.exponential_base,
            )
        return wait_exponential(
            multiplier=self.initial_wait,
            max=self.max_wait,
            exp_base=self.exponential_base,
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
                raise e.last_attempt.result() from e
            raise

        _msg = "Unreachable"
        raise AssertionError(_msg)

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
                raise e.last_attempt.result() from e
            raise

        _msg = "Unreachable"
        raise AssertionError(_msg)

    return wrapper


class RetryHandler:
    """Handler for retry logic with rate limit awareness."""

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
            # Add jitter (±25%)
            jitter = wait_time * 0.25
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
