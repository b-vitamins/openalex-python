"""Test retry logic."""

import pytest
from unittest.mock import Mock, patch
import time

from openalex.exceptions import (
    RateLimitExceeded,
    ServerError,
    TemporaryError,
    NetworkError,
)
from openalex.utils.retry import retry_on_error, retry_with_rate_limit


class TestRetryLogic:
    """Test retry decorators."""

    def test_retry_on_server_error(self):
        """Test retry on server errors."""
        mock_func = Mock()
        mock_func.side_effect = [
            ServerError("Server error"),
            ServerError("Server error"),
            "success",
        ]

        @retry_on_error
        def func():
            return mock_func()

        result = func()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_exhausted(self):
        """Test when all retries are exhausted."""
        mock_func = Mock()
        mock_func.side_effect = ServerError("Server error")

        @retry_on_error
        def func():
            return mock_func()

        with pytest.raises(ServerError):
            func()

        assert mock_func.call_count == 3  # Default max attempts

    def test_rate_limit_retry(self):
        """Test rate limit retry with header."""
        mock_func = Mock()
        mock_func.side_effect = [
            RateLimitExceeded("Rate limited", retry_after=1),
            "success",
        ]

        @retry_with_rate_limit
        def func():
            return mock_func()

        start_time = time.time()
        result = func()
        elapsed = time.time() - start_time

        assert result == "success"
        assert mock_func.call_count == 2
        assert elapsed >= 1.0  # Should wait at least 1 second

    def test_no_retry_on_non_retryable(self):
        """Test no retry on non-retryable errors."""
        mock_func = Mock()
        mock_func.side_effect = ValueError("Not retryable")

        @retry_on_error
        def func():
            return mock_func()

        with pytest.raises(ValueError):
            func()

        assert mock_func.call_count == 1  # No retry
