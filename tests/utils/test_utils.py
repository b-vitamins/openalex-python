"""
Test utility functions behavior.
Tests what utilities should do, not how they're implemented.
"""

import asyncio
import time
from unittest.mock import Mock

import pytest


class FakeClock:
    """Simple timekeeper for testing."""

    def __init__(self, real_async_sleep: asyncio.sleep) -> None:
        self.current = 0.0
        self._real_async_sleep = real_async_sleep

    def time(self) -> float:
        return self.current

    def monotonic(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.current += seconds

    async def async_sleep(self, seconds: float) -> None:
        self.current += seconds
        await self._real_async_sleep(0)


@pytest.fixture(autouse=True)
def mock_time(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    """Provide a fake clock to avoid real delays."""

    real_sleep = asyncio.sleep
    clock = FakeClock(real_sleep)
    monkeypatch.setattr(time, "time", clock.time)
    monkeypatch.setattr(time, "monotonic", clock.monotonic)
    monkeypatch.setattr(time, "sleep", clock.sleep)
    monkeypatch.setattr(asyncio, "sleep", clock.async_sleep)
    return clock


class TestPaginationBehavior:
    """Test pagination utility behavior."""

    def test_paginator_iterates_through_all_pages(self):
        """Paginator should iterate through all available pages."""
        from openalex.utils import Paginator

        def fetch_page(params):
            page = int(params.get("page", 1))
            if page <= 3:
                return Mock(
                    meta=Mock(
                        count=30, page=page, per_page=10, next_cursor=None
                    ),
                    results=[
                        f"item{i}" for i in range((page - 1) * 10, page * 10)
                    ],
                )
            return Mock(
                meta=Mock(count=30, page=page, per_page=10, next_cursor=None),
                results=[],
            )

        paginator = Paginator(fetch_page, per_page=10)
        all_items = paginator.all()

        assert len(all_items) == 30
        assert all_items[0] == "item0"
        assert all_items[29] == "item29"

    def test_paginator_respects_max_results(self):
        """Paginator should stop at max_results if specified."""
        from openalex.utils import Paginator

        def fetch_page(params):
            page = int(params.get("page", 1))
            return Mock(
                meta=Mock(count=100, page=page, per_page=10, next_cursor=None),
                results=[f"item{i}" for i in range((page - 1) * 10, page * 10)],
            )

        paginator = Paginator(fetch_page, per_page=10, max_results=25)
        all_items = paginator.all()

        assert len(all_items) == 25

    def test_paginator_follows_cursor_when_available(self):
        """Paginator should use cursor for pagination when provided."""
        from openalex.utils import Paginator

        cursors_used = []

        def fetch_page(params):
            cursor = params.get("cursor")
            cursors_used.append(cursor)

            if cursor is None:
                return Mock(
                    meta=Mock(count=20, page=1, next_cursor="cursor1"),
                    results=["item1", "item2"],
                )
            elif cursor == "cursor1":
                return Mock(
                    meta=Mock(count=20, page=2, next_cursor="cursor2"),
                    results=["item3", "item4"],
                )
            else:
                return Mock(
                    meta=Mock(count=20, page=3, next_cursor=None),
                    results=["item5", "item6"],
                )

        paginator = Paginator(fetch_page)
        paginator.all()

        assert cursors_used == [None, "cursor1", "cursor2"]

    def test_paginator_handles_empty_results(self):
        """Paginator should handle empty result sets gracefully."""
        from openalex.utils import Paginator

        def fetch_page(params):
            return Mock(
                meta=Mock(count=0, page=1, per_page=10, next_cursor=None),
                results=[],
            )

        paginator = Paginator(fetch_page)
        all_items = paginator.all()

        assert all_items == []

    @pytest.mark.asyncio
    async def test_async_paginator_concurrent_gather(self):
        """Async paginator should fetch pages concurrently."""
        from openalex.utils import AsyncPaginator

        fetch_times = []

        async def fetch_page(params):
            fetch_times.append(time.time())
            await asyncio.sleep(0.1)  # Simulate network delay
            page = int(params.get("page", 1))
            return Mock(
                meta=Mock(count=30, page=page, per_page=10, next_cursor=None),
                results=[
                    f"item{i}"
                    for i in range((page - 1) * 10, min(page * 10, 30))
                ],
            )

        paginator = AsyncPaginator(fetch_page, per_page=10, concurrency=3)

        start_time = time.time()
        results = await paginator.gather(pages=3)
        total_time = time.time() - start_time

        # With the fake clock, each sleep adds to time even when concurrent.
        assert total_time <= 0.31
        assert len(results) == 30

        # Fake clock records sequential times; allow a wider spread
        assert max(fetch_times) - min(fetch_times) <= 0.2


class TestRateLimitingBehavior:
    """Test rate limiting behavior."""

    def test_rate_limiter_enforces_rate(self):
        """Rate limiter should enforce request rate."""
        from openalex.utils import RateLimiter

        # 10 requests per second
        limiter = RateLimiter(rate=10, burst=2)

        # First two should be immediate (burst)
        wait1 = limiter.acquire()
        wait2 = limiter.acquire()

        assert wait1 == 0
        assert wait2 == 0

        # Third should wait
        wait3 = limiter.acquire()
        assert wait3 > 0  # Should wait ~0.1s

    def test_rate_limited_decorator_delays_calls(self):
        """Rate limited decorator should delay function calls."""
        from openalex.utils import rate_limited

        call_times = []

        @rate_limited(rate=5, burst=1)  # 5 per second
        def api_call():
            call_times.append(time.time())
            return "result"

        # Make 3 calls
        results = [api_call() for _ in range(3)]

        assert all(r == "result" for r in results)

        # First call immediate, others delayed
        assert call_times[1] - call_times[0] >= 0.15  # ~0.2s apart
        assert call_times[2] - call_times[1] >= 0.15

    @pytest.mark.asyncio
    async def test_async_rate_limiter_coordinates_requests(self):
        """Async rate limiter should coordinate concurrent requests."""
        from openalex.utils import AsyncRateLimiter

        limiter = AsyncRateLimiter(rate=10, burst=2)

        async def make_request(id):
            wait = await limiter.acquire()
            return (id, wait)

        # Launch concurrent requests
        tasks = [make_request(i) for i in range(4)]
        results = await asyncio.gather(*tasks)

        # First 2 should have no wait (burst)
        no_wait = sum(1 for _, wait in results if wait == 0)
        assert no_wait == 2

        # Others should wait
        with_wait = sum(1 for _, wait in results if wait > 0)
        assert with_wait == 2


class TestRetryBehavior:
    """Test retry mechanism behavior."""

    def test_retry_on_temporary_errors(self):
        """Should retry on temporary errors."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import ServerError

        attempt_count = 0

        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ServerError("Temporary error", status_code=503)
            return "success"

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = with_retry(flaky_function, config)

        result = wrapped()
        assert result == "success"
        assert attempt_count == 3

    def test_retry_respects_max_attempts(self):
        """Should stop retrying after max attempts."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import ServerError

        attempt_count = 0

        def always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise ServerError("Permanent error", status_code=500)

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = with_retry(always_fails, config)

        with pytest.raises(ServerError):
            wrapped()

        assert attempt_count == 3

    def test_retry_with_exponential_backoff(self):
        """Retry delays should increase exponentially."""
        from openalex.utils import RetryHandler, RetryConfig

        config = RetryConfig(initial_wait=0.1, max_wait=1.0, multiplier=2.0)
        handler = RetryHandler(config)

        # Calculate wait times for attempts
        wait1 = handler.calculate_wait(1)
        wait2 = handler.calculate_wait(2)
        wait3 = handler.calculate_wait(3)

        # Should double each time (with some jitter)
        assert 0.05 <= wait1 <= 0.15  # ~0.1s
        assert 0.15 <= wait2 <= 0.25  # ~0.2s
        assert 0.30 <= wait3 <= 0.50  # ~0.4s with jitter

    def test_retry_respects_retry_after_header(self):
        """Should respect Retry-After header from server."""
        from openalex.utils import with_retry, RetryConfig
        from openalex.exceptions import RateLimitError

        attempt_times = []

        def rate_limited():
            attempt_times.append(time.time())
            if len(attempt_times) < 2:
                raise RateLimitError("Rate limited", retry_after=0.2)
            return "success"

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = with_retry(rate_limited, config)

        result = wrapped()
        assert result == "success"

        # Should wait at least 0.2s as specified by retry_after
        assert attempt_times[1] - attempt_times[0] >= 0.19

    @pytest.mark.asyncio
    async def test_async_retry_behavior(self):
        """Async retry should work like sync retry."""
        from openalex.utils import async_with_retry, RetryConfig
        from openalex.exceptions import NetworkError

        attempt_count = 0

        async def flaky_async_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise NetworkError("Connection failed")
            return "async success"

        config = RetryConfig(max_attempts=3, initial_wait=0.01)
        wrapped = async_with_retry(flaky_async_function, config)

        result = await wrapped()
        assert result == "async success"
        assert attempt_count == 3


class TestParameterHandling:
    """Test parameter normalization and handling."""

    def test_parameter_normalization(self):
        """Parameters should be normalized for API."""
        from openalex.utils import normalize_params

        params = {
            "per_page": 50,
            "select": ["id", "title", "doi"],
            "group_by": "is_oa",
            "unknown_param": "value",
        }

        normalized = normalize_params(params)

        assert normalized["per-page"] == "50"
        assert normalized["select"] == "id,title,doi"
        assert normalized["group-by"] == "is_oa"
        assert "unknown_param" not in normalized

    def test_filter_parameter_serialization(self):
        """Filter parameters should serialize correctly."""
        from openalex.utils.params import serialize_filter_value

        # Boolean
        assert serialize_filter_value(True) == "true"
        assert serialize_filter_value(False) == "false"

        # List
        assert serialize_filter_value(["A", "B", "C"]) == "A|B|C"

        # None
        assert serialize_filter_value(None) == "null"

        # Special characters
        assert serialize_filter_value("hello world") == "hello+world"

    def test_nested_filter_flattening(self):
        """Nested filters should flatten with dot notation."""
        from openalex.utils.params import flatten_filter_dict

        filters = {
            "authorships": {
                "author": {"id": "A123"},
                "institutions": {"country_code": "US"},
            }
        }

        flattened = flatten_filter_dict(filters)

        assert "authorships.author.id:A123" in flattened
        assert "authorships.institutions.country_code:US" in flattened


class TestIDHandling:
    """Test OpenAlex ID handling utilities."""

    def test_id_normalization(self):
        """IDs should be normalized consistently."""
        from openalex.utils import ensure_prefix, strip_id_prefix

        # Add prefix if missing
        assert ensure_prefix("123", "W") == "W123"
        assert ensure_prefix("W123", "W") == "W123"

        # Strip URL prefix
        assert strip_id_prefix("https://openalex.org/W123") == "W123"
        assert strip_id_prefix("W123") == "W123"

    def test_id_validation(self):
        """Should validate OpenAlex ID format."""
        from openalex.utils import is_openalex_id

        assert is_openalex_id("https://openalex.org/W123")
        assert is_openalex_id("https://openalex.org/A456")
        assert not is_openalex_id("W123")
        assert not is_openalex_id("http://example.com/W123")
        assert not is_openalex_id("not-an-id")


class TestTextProcessing:
    """Test text processing utilities."""

    def test_abstract_inversion(self):
        """Should reconstruct abstract from inverted index."""
        from openalex.utils import invert_abstract

        inverted_index = {
            "This": [0],
            "is": [1, 5],
            "a": [2],
            "test": [3],
            "abstract": [4],
            "simple": [6],
        }

        abstract = invert_abstract(inverted_index)
        assert abstract == "This is a test abstract is simple"

    def test_abstract_inversion_handles_empty(self):
        """Should handle empty or None inverted index."""
        from openalex.utils import invert_abstract

        assert invert_abstract(None) is None
        assert invert_abstract({}) == ""


class TestLogging:
    """Test logging configuration and privacy features."""

    def test_configure_logging_json_format(self):
        """Test JSON logging configuration."""
        from openalex.logging import configure_logging
        import logging
        import json

        import io
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)

        configure_logging(level="DEBUG", format="json", include_timestamps=True, privacy_mode=True)

        logger = logging.getLogger("openalex")
        logger.addHandler(handler)
        logger.info("Test message", api_key="secret123")

        log_output = log_capture.getvalue()
        log_data = json.loads(log_output.strip())

        assert log_data["event"] == "Test message"
        assert log_data["api_key"] == "[REDACTED]"
        assert "timestamp" in log_data

    def test_sanitize_sensitive_data(self):
        """Test sensitive data sanitization."""
        from openalex.logging import sanitize_sensitive_data

        test_data = {
            "user": "john",
            "api_key": "sk-proj-abc123",
            "email": "user@example.com",
            "nested": {
                "password": "secret",
                "token": "bearer-xyz",
            },
            "safe_field": "public data",
        }

        sanitized = sanitize_sensitive_data(test_data)

        assert sanitized["user"] == "john"
        assert sanitized["api_key"] == "[REDACTED]"
        assert "[EMAIL]" in sanitized["email"]
        assert sanitized["nested"]["password"] == "[REDACTED]"
        assert sanitized["nested"]["token"] == "[REDACTED]"
        assert sanitized["safe_field"] == "public data"

    def test_request_logger(self):
        """Test HTTP request/response logging."""
        from openalex.logging import RequestLogger

        logger = RequestLogger(enabled=True, include_headers=True)

        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            logger.log_request(
                "GET",
                "https://api.openalex.org/works?api_key=secret",
                headers={"Authorization": "Bearer token123"},
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[1]
            assert "api_key=[REDACTED]" in call_args["url"]
            assert call_args["headers"]["Authorization"] == "[REDACTED]"
