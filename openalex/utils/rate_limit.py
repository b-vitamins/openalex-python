"""Rate limiting utilities for OpenAlex API."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from threading import Lock
from typing import TYPE_CHECKING, Any, Final, TypeVar

from structlog import get_logger

DEFAULT_BUFFER: Final = 0.1

__all__ = [
    "DEFAULT_BUFFER",
    "AsyncRateLimiter",
    "RateLimiter",
    "SlidingWindowRateLimiter",
    "async_rate_limited",
    "rate_limited",
]

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger(__name__)

T = TypeVar("T")


class RateLimiter:
    """Token bucket rate limiter."""

    __slots__ = (
        "burst",
        "last_update",
        "lock",
        "rate",
        "tokens",
    )

    def __init__(
        self,
        rate: float,
        burst: int | None = None,
        buffer: float = DEFAULT_BUFFER,
    ) -> None:
        """Initialize rate limiter.

        Args:
            rate: Requests per second
            burst: Maximum burst size (defaults to rate)
            buffer: Safety buffer (0-1) to avoid hitting limits
        """
        self.rate = rate * (1 - buffer)  # Apply buffer
        self.burst = burst or int(rate)
        self.tokens = float(self.burst)
        self.last_update = time.monotonic()
        self.lock = Lock()

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update

        # Add tokens based on elapsed time
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now

    def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, blocking if necessary.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Wait time in seconds (0 if tokens were available)
        """
        with self.lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0

            # Calculate wait time
            deficit = tokens - self.tokens
            wait_time = deficit / self.rate

            # Reserve the tokens
            self.tokens = 0

            return wait_time

    def try_acquire(self, tokens: int = 1) -> bool:
        """Attempt to acquire ``tokens`` without blocking."""
        with self.lock:
            self._refill_tokens()
            if self.tokens < tokens:
                return False
            self.tokens -= tokens
            return True

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<RateLimiter rate={self.rate} burst={self.burst}>"

    def __enter__(self) -> RateLimiter:
        """Context manager entry."""
        wait_time = self.acquire()
        if wait_time > 0:
            time.sleep(wait_time)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context manager."""
        return


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""

    __slots__ = (
        "_window",
        "lock",
        "max_requests",
        "window_seconds",
    )

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        _buffer: float = DEFAULT_BUFFER,
    ) -> None:
        """Initialize sliding window rate limiter.

        Args:
            max_requests: Maximum requests in window
            window_seconds: Window size in seconds
            _buffer: Safety buffer (0-1)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._window: deque[float] = deque()
        self.lock = Lock()

    def _clean_window(self) -> None:
        """Remove expired requests from window."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        while self._window and self._window[0] < cutoff:
            self._window.popleft()

    def acquire(self) -> float:
        """Acquire permission to make a request.

        Returns:
            Wait time in seconds (0 if request allowed)
        """
        with self.lock:
            now = time.monotonic()
            self._clean_window()

            if len(self._window) < self.max_requests:
                self._window.append(now)
                return 0.0

            oldest = self._window[0]
            wait_time = self.window_seconds - (now - oldest)

        if wait_time > 0:
            time.sleep(wait_time)

        with self.lock:
            self._clean_window()
            self._window.append(time.monotonic())

        return max(0.0, wait_time)

    def try_acquire(self) -> bool:
        """Try to acquire permission without blocking.

        Returns:
            True if request allowed, False otherwise
        """
        with self.lock:
            self._clean_window()
            if len(self._window) >= self.max_requests:
                return False
            self._window.append(time.monotonic())
            return True

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<SlidingWindowRateLimiter max={self.max_requests} window={self.window_seconds}>"

    def __enter__(self) -> SlidingWindowRateLimiter:
        """Context manager entry."""
        wait_time = self.acquire()
        if wait_time > 0:
            time.sleep(wait_time)
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        return


class AsyncRateLimiter:
    """Async token bucket rate limiter."""

    __slots__ = (
        "burst",
        "last_update",
        "lock",
        "rate",
        "tokens",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<AsyncRateLimiter rate={self.rate} burst={self.burst}>"

    def __init__(
        self,
        rate: float,
        burst: int | None = None,
        buffer: float = DEFAULT_BUFFER,
    ) -> None:
        """Initialize async rate limiter."""
        self.rate = rate * (1 - buffer)
        self.burst = burst or int(rate)
        self.tokens = float(self.burst)
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update

        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now

    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, blocking if necessary."""
        async with self.lock:
            await self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0

            deficit = tokens - self.tokens
            wait_time = deficit / self.rate
            self.tokens = 0

            return wait_time

    async def __aenter__(self) -> AsyncRateLimiter:
        """Context manager entry."""
        wait_time = await self.acquire()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit the async context manager."""
        return


def rate_limited(
    rate: float,
    burst: int | None = None,
    buffer: float = DEFAULT_BUFFER,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to rate limit function calls.

    Args:
        rate: Requests per second
        burst: Maximum burst size
        buffer: Safety buffer (0-1)

    Returns:
        Decorated function
    """
    limiter = RateLimiter(rate, burst, buffer)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            wait_time = limiter.acquire()
            if wait_time > 0:
                logger.debug("Rate limit: waiting %.2fs", wait_time)
                time.sleep(wait_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def async_rate_limited(
    rate: float,
    burst: int | None = None,
    buffer: float = DEFAULT_BUFFER,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Async decorator to rate limit function calls."""
    limiter = AsyncRateLimiter(rate, burst, buffer)

    def decorator(
        func: Callable[..., Awaitable[T]],
    ) -> Callable[..., Awaitable[T]]:
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            wait_time = await limiter.acquire()
            if wait_time > 0:
                logger.debug("Rate limit: waiting %.2fs", wait_time)
                await asyncio.sleep(wait_time)
            return await func(*args, **kwargs)

        return wrapper

    return decorator
