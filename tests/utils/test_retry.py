"""
Test retry and rate limiting utilities.
Tests retry logic, backoff strategies, and rate limiting behavior.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch


class TestRetryLogic:
    """Test retry mechanism behavior."""

    def test_retry_config_defaults(self):
        """Test default retry configuration."""
        from openalex.utils import RetryConfig

        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.initial_wait == 1.0
        assert config.max_wait == 60.0
        assert config.multiplier == 2.0
        assert config.jitter is True

    def test_retry_config_custom(self):
        """Test custom retry configuration."""
        from openalex.utils import RetryConfig

        config = RetryConfig(
            max_attempts=5,
            initial_wait=0.5,
            max_wait=30.0,
            multiplier=1.5,
            jitter=False,
        )

        assert config.max_attempts == 5
        assert config.initial_wait == 0.5
        assert config.max_wait == 30.0
        assert config.multiplier == 1.5
        assert config.jitter is False

    def test_is_retryable_error(self):
        """Test error classification for retry."""
        from openalex.utils import is_retryable_error
        from openalex.exceptions import (
            RateLimitError,
            ServerError,
            NetworkError,
            TimeoutError,
            NotFoundError,
            ValidationError,
        )

        # Retryable errors
        assert is_retryable_error(RateLimitError())
        assert is_retryable_error(ServerError("Server error", status_code=500))
        assert is_retryable_error(ServerError("Bad gateway", status_code=502))
        assert is_retryable_error(
            ServerError("Service unavailable", status_code=503)
        )
        assert is_retryable_error(NetworkError())
        assert is_retryable_error(TimeoutError())

        # Non-retryable errors
        assert not is_retryable_error(NotFoundError())
        assert not is_retryable_error(ValidationError("Invalid"))
        assert not is_retryable_error(ValueError("Bad value"))
        assert not is_retryable_error(Exception("Generic"))

    def test_retry_handler_calculate_wait(self):
        """Test wait time calculation with exponential backoff."""
        from openalex.utils import RetryHandler, RetryConfig

        config = RetryConfig(
            initial_wait=1.0,
            multiplier=2.0,
            max_wait=10.0,
            jitter=False,  # Disable jitter for predictable results
        )
        handler = RetryHandler(config)

        # Exponential backoff: 1, 2, 4, 8, 10 (capped)
        assert handler.calculate_wait(1) == 1.0
        assert handler.calculate_wait(2) == 2.0
        assert handler.calculate_wait(3) == 4.0
        assert handler.calculate_wait(4) == 8.0
        assert handler.calculate_wait(5) == 10.0  # Capped at max_wait

    def test_retry_handler_with_jitter(self):
        """Test wait time calculation with jitter."""
        from openalex.utils import RetryHandler, RetryConfig

        config = RetryConfig(initial_wait=1.0, jitter=True)
        handler = RetryHandler(config)

        # With jitter, wait time should vary
        wait_times = [handler.calculate_wait(1) for _ in range(10)]

        # All should be around 1.0 but with variation
        assert all(0.5 <= w <= 1.5 for w in wait_times)
        assert len(set(wait_times)) > 1  # Should have variation

    def test_with_retry_decorator_success(self):
        """Test retry decorator with eventual success."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import ServerError

        attempt_count = 0

        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ServerError("Temporary failure", status_code=503)
            return "success"

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = with_retry(flaky_function, config)

        result = wrapped()
        assert result == "success"
        assert attempt_count == 3

    def test_with_retry_decorator_exhausted(self):
        """Test retry decorator when all attempts fail."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import ServerError

        attempt_count = 0

        def always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise ServerError("Permanent failure", status_code=500)

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = with_retry(always_fails, config)

        with pytest.raises(ServerError):
            wrapped()

        assert attempt_count == 3

    def test_with_retry_non_retryable(self):
        """Test retry decorator with non-retryable error."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import NotFoundError

        attempt_count = 0

        def raises_not_found():
            nonlocal attempt_count
            attempt_count += 1
            raise NotFoundError()

        config = RetryConfig(max_attempts=3)
        wrapped = with_retry(raises_not_found, config)

        with pytest.raises(NotFoundError):
            wrapped()

        # Should not retry non-retryable errors
        assert attempt_count == 1

    def test_retry_with_rate_limit_header(self):
        """Test retry respects Retry-After header."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import RateLimitError

        attempt_times = []

        def rate_limited():
            attempt_times.append(time.time())
            if len(attempt_times) < 2:
                raise RateLimitError("Rate limited", retry_after=0.1)
            return "success"

        config = RetryConfig(max_attempts=3, initial_wait=1.0)
        wrapped = with_retry(rate_limited, config)

        result = wrapped()
        assert result == "success"

        # Should respect retry_after (0.1s) instead of initial_wait (1.0s)
        wait_time = attempt_times[1] - attempt_times[0]
        assert 0.09 <= wait_time <= 0.15  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_async_with_retry(self):
        """Test async retry decorator."""
        from openalex.utils import async_with_retry, RetryConfig
        from openalex.exceptions import NetworkError

        attempt_count = 0

        async def async_flaky():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise NetworkError("Connection failed")
            return "async success"

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = async_with_retry(async_flaky, config)

        result = await wrapped()
        assert result == "async success"
        assert attempt_count == 3


class TestRateLimiting:
    """Test rate limiting behavior."""

    def test_rate_limiter_basic(self):
        """Test basic rate limiter functionality."""
        from openalex.utils import RateLimiter

        # 10 requests per second, burst of 2
        limiter = RateLimiter(rate=10, burst=2)

        # First two should be immediate (burst)
        wait1 = limiter.acquire()
        wait2 = limiter.acquire()

        assert wait1 == 0
        assert wait2 == 0

        # Third should wait (~0.1s for 10/sec rate)
        wait3 = limiter.acquire()
        assert 0.05 <= wait3 <= 0.15

    def test_rate_limiter_try_acquire(self):
        """Test non-blocking acquire."""
        from openalex.utils import RateLimiter

        limiter = RateLimiter(rate=10, burst=1)

        # First should succeed
        assert limiter.try_acquire() is True

        # Second should fail (no capacity)
        assert limiter.try_acquire() is False

        # Wait for capacity
        time.sleep(0.15)
        assert limiter.try_acquire() is True

    def test_rate_limited_decorator(self):
        """Test rate limited function decorator."""
        from openalex.utils import rate_limited

        call_times = []

        @rate_limited(rate=5, burst=1)  # 5 per second
        def api_call(value):
            call_times.append(time.time())
            return value * 2

        # Make several calls
        results = [api_call(i) for i in range(3)]

        assert results == [0, 2, 4]

        # Check timing
        assert call_times[0] <= call_times[1]
        assert call_times[1] - call_times[0] >= 0.15  # ~0.2s for 5/sec

    @pytest.mark.asyncio
    async def test_async_rate_limiter(self):
        """Test async rate limiter."""
        from openalex.utils import AsyncRateLimiter

        limiter = AsyncRateLimiter(rate=10, burst=2)

        # Track acquisition times
        times = []

        async def acquire_and_track():
            wait = await limiter.acquire()
            times.append((time.time(), wait))

        # Make 3 concurrent requests
        await asyncio.gather(
            acquire_and_track(), acquire_and_track(), acquire_and_track()
        )

        # First 2 should have no wait (burst)
        no_wait = sum(1 for _, wait in times if wait == 0)
        assert no_wait == 2

    @pytest.mark.asyncio
    async def test_async_rate_limited_decorator(self):
        """Test async rate limited decorator."""
        from openalex.utils import async_rate_limited

        call_times = []

        @async_rate_limited(rate=5, burst=1)
        async def async_api_call():
            call_times.append(time.time())
            await asyncio.sleep(0.01)
            return "done"

        # Make concurrent calls
        results = await asyncio.gather(
            async_api_call(), async_api_call(), async_api_call()
        )

        assert all(r == "done" for r in results)

        # Should be rate limited
        assert call_times[1] - call_times[0] >= 0.15


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiter."""

    def test_sliding_window_basic(self):
        """Test sliding window rate limiting."""
        from openalex.utils import SlidingWindowRateLimiter

        # 2 requests per 0.2 second window
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.2)

        # First two should succeed
        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is True

        # Third should fail (window full)
        assert limiter.try_acquire() is False

        # Wait for window to slide
        time.sleep(0.25)

        # Should work again
        assert limiter.try_acquire() is True

    def test_sliding_window_acquire_blocking(self):
        """Test blocking acquire with sliding window."""
        from openalex.utils import SlidingWindowRateLimiter

        limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=0.1)

        # First should be immediate
        wait1 = limiter.acquire()
        assert wait1 == 0

        # Second should wait
        start = time.time()
        wait2 = limiter.acquire()
        elapsed = time.time() - start

        assert 0.08 <= elapsed <= 0.12
        assert 0.08 <= wait2 <= 0.12

    def test_sliding_window_cleanup(self):
        """Test old entries are cleaned up."""
        from openalex.utils import SlidingWindowRateLimiter

        limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=0.1)

        # Fill window
        for _ in range(10):
            limiter.try_acquire()

        # Check internal state has entries
        assert len(limiter._window) == 10

        # Wait for window to pass
        time.sleep(0.15)

        # Acquire again (should trigger cleanup)
        limiter.try_acquire()

        # Old entries should be cleaned
        assert len(limiter._window) <= 1


class TestRetryContext:
    """Test retry context manager."""

    def test_retry_context_manager(self):
        """Test retry as context manager."""
        from openalex.utils import RetryContext, RetryConfig
        from openalex.exceptions import ServerError

        attempt_count = 0
        config = RetryConfig(max_attempts=3, initial_wait=0.01)

        with RetryContext(config) as retry:
            while retry.should_retry():
                attempt_count += 1
                try:
                    if attempt_count < 3:
                        raise ServerError("Fail", status_code=503)
                    # Success on third attempt
                    break
                except ServerError as e:
                    retry.record_error(e)

        assert attempt_count == 3
        assert retry.succeeded

    def test_retry_context_failure(self):
        """Test retry context when all attempts fail."""
        from openalex.utils import RetryContext, RetryConfig
        from openalex.exceptions import ServerError

        config = RetryConfig(max_attempts=2, initial_wait=0.01)

        with pytest.raises(ServerError):
            with RetryContext(config) as retry:
                while retry.should_retry():
                    try:
                        raise ServerError("Always fails", status_code=500)
                    except ServerError as e:
                        retry.record_error(e)


class TestBackoffStrategies:
    """Test different backoff strategies."""

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        from openalex.utils import exponential_backoff

        assert exponential_backoff(1, initial=1.0, multiplier=2.0) == 1.0
        assert exponential_backoff(2, initial=1.0, multiplier=2.0) == 2.0
        assert exponential_backoff(3, initial=1.0, multiplier=2.0) == 4.0
        assert exponential_backoff(4, initial=1.0, multiplier=2.0) == 8.0

    def test_linear_backoff(self):
        """Test linear backoff calculation."""
        from openalex.utils import linear_backoff

        assert linear_backoff(1, initial=1.0, increment=0.5) == 1.0
        assert linear_backoff(2, initial=1.0, increment=0.5) == 1.5
        assert linear_backoff(3, initial=1.0, increment=0.5) == 2.0
        assert linear_backoff(4, initial=1.0, increment=0.5) == 2.5

    def test_constant_backoff(self):
        """Test constant backoff (no increase)."""
        from openalex.utils import constant_backoff

        assert constant_backoff(1, wait=1.0) == 1.0
        assert constant_backoff(2, wait=1.0) == 1.0
        assert constant_backoff(3, wait=1.0) == 1.0
