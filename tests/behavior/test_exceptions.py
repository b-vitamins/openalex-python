"""
Test exception handling behavior based on API responses.
Tests what exceptions should be raised in different scenarios.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
import httpx


class TestExceptionBehavior:
    """Test exception handling based on API responses."""

    def test_rate_limit_error_includes_retry_after(self):
        """Rate limit errors should include retry-after time."""
        from openalex import Works
        from openalex.exceptions import RateLimitError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=429,
                json=Mock(
                    return_value={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests",
                    }
                ),
                headers={"Retry-After": "60"},
            )

            works = Works()

            with pytest.raises(RateLimitError) as exc_info:
                works.get("W123")

            assert exc_info.value.retry_after == 60
            assert "Rate limit exceeded" in str(exc_info.value)

    def test_not_found_error_for_missing_entities(self):
        """404 responses should raise NotFoundError."""
        from openalex import Authors
        from openalex.exceptions import NotFoundError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=404,
                json=Mock(
                    return_value={
                        "error": "Not Found",
                        "message": "Author with ID A99999999 not found",
                    }
                ),
            )

            authors = Authors()

            with pytest.raises(NotFoundError) as exc_info:
                authors.get("A99999999")

            assert "A99999999 not found" in str(exc_info.value)

    def test_authentication_error_for_invalid_api_key(self):
        """401 responses should raise AuthenticationError."""
        from openalex import Institutions, OpenAlexConfig
        from openalex.exceptions import AuthenticationError

        config = OpenAlexConfig(api_key="invalid-key")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=401,
                json=Mock(
                    return_value={
                        "error": "Unauthorized",
                        "message": "Invalid API key",
                    }
                ),
            )

            institutions = Institutions(config=config)

            with pytest.raises(AuthenticationError) as exc_info:
                institutions.get("I123")

            assert "Invalid API key" in str(exc_info.value)

    def test_validation_error_for_bad_parameters(self):
        """400 responses should raise ValidationError with details."""
        from openalex import Works
        from openalex.exceptions import ValidationError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=400,
                json=Mock(
                    return_value={
                        "error": "Bad Request",
                        "message": "Invalid filter: 'invalid_field' is not a valid filter",
                    }
                ),
            )

            works = Works()

            with pytest.raises(ValidationError) as exc_info:
                works.filter(invalid_field="value").get()

            assert "invalid_field" in str(exc_info.value)
            assert "not a valid filter" in str(exc_info.value)

    def test_server_error_for_5xx_responses(self):
        """5xx responses should raise ServerError."""
        from openalex import Sources
        from openalex.exceptions import ServerError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=500,
                json=Mock(
                    return_value={
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred",
                    }
                ),
            )

            sources = Sources()

            with pytest.raises(ServerError) as exc_info:
                sources.get("S123")

            assert exc_info.value.status_code == 500

    def test_timeout_error_on_request_timeout(self):
        """Request timeouts should raise TimeoutError."""
        from openalex import Concepts
        from openalex.exceptions import TimeoutError

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException(
                "Request timed out"
            )

            concepts = Concepts()

            with pytest.raises(TimeoutError) as exc_info:
                concepts.get("C123")

            assert "Request timed out" in str(exc_info.value)

    def test_network_error_on_connection_failure(self):
        """Connection failures should raise NetworkError."""
        from openalex import Publishers
        from openalex.exceptions import NetworkError

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection refused")

            publishers = Publishers()

            with pytest.raises(NetworkError) as exc_info:
                publishers.get("P123")

            assert "Connection refused" in str(exc_info.value)

    def test_temporary_error_for_503_responses(self):
        """503 Service Unavailable should raise TemporaryError."""
        from openalex import Funders
        from openalex.exceptions import TemporaryError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=503,
                json=Mock(
                    return_value={
                        "error": "Service Unavailable",
                        "message": "Service temporarily unavailable",
                    }
                ),
                headers={"Retry-After": "30"},
            )

            funders = Funders()

            with pytest.raises(TemporaryError) as exc_info:
                funders.get("F123")

            assert exc_info.value.status_code == 503
            assert exc_info.value.retry_after == 30

    def test_api_error_base_class_attributes(self):
        """APIError should have standard attributes."""
        from openalex import Topics
        from openalex.exceptions import APIError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=400,
                json=Mock(
                    return_value={
                        "error": "Bad Request",
                        "message": "Invalid request",
                        "details": {
                            "field": "page",
                            "issue": "must be positive",
                        },
                    }
                ),
            )

            topics = Topics()

            with pytest.raises(APIError) as exc_info:
                topics.get(page=-1)

            error = exc_info.value
            assert error.status_code == 400
            assert error.message == "Invalid request"
            assert error.details == {
                "field": "page",
                "issue": "must be positive",
            }

    def test_non_json_error_response_handling(self):
        """Non-JSON error responses should be handled gracefully."""
        from openalex import Works
        from openalex.exceptions import ServerError

        with patch("httpx.Client.request") as mock_request:
            # HTML error page
            mock_request.return_value = Mock(
                status_code=502,
                json=Mock(side_effect=ValueError("Not JSON")),
                text="<html><body>502 Bad Gateway</body></html>",
                headers={"Content-Type": "text/html"},
            )

            works = Works()

            with pytest.raises(ServerError) as exc_info:
                works.get("W123")

            assert exc_info.value.status_code == 502
            assert "Bad Gateway" in str(
                exc_info.value
            ) or "Server error" in str(exc_info.value)

    def test_retry_after_header_parsing(self):
        """Retry-After header should be parsed correctly."""
        from openalex import Authors
        from openalex.exceptions import RateLimitError

        with patch("time.sleep") as mock_sleep:  # Mock sleep to avoid waiting
            with patch("httpx.Client.request") as mock_request:
                # Test numeric seconds
                mock_request.return_value = Mock(
                    status_code=429,
                    json=Mock(return_value={"error": "Rate limited"}),
                    headers={"Retry-After": "120"},
                )
                authors = Authors()
                with pytest.raises(RateLimitError) as exc_info:
                    authors.get("A123")
                assert exc_info.value.retry_after == 120
                # Test HTTP date format
                future_date = "Wed, 21 Oct 2025 07:28:00 GMT"
                mock_request.return_value.headers = {"Retry-After": future_date}
                with pytest.raises(RateLimitError) as exc_info:
                    authors.get("A456")
                # Should parse date and return seconds
                assert exc_info.value.retry_after > 0

    def test_error_context_preserved(self):
        """Error context should include request details."""
        from openalex import Institutions
        from openalex.exceptions import ValidationError

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=400,
                json=Mock(
                    return_value={
                        "error": "Invalid filter combination",
                        "message": "Cannot use 'search' with 'filter.display_name.search'",
                    }
                ),
            )

            institutions = Institutions()

            with pytest.raises(ValidationError) as exc_info:
                institutions.search("MIT").search_filter(
                    display_name="MIT"
                ).get()

            error = exc_info.value
            assert "search" in str(error)
            assert "filter.display_name.search" in str(error)

    def test_chained_exceptions_preserve_original(self):
        """Network errors should preserve original exception."""
        from openalex import Keywords
        from openalex.exceptions import NetworkError
        import ssl

        with patch("httpx.Client.request") as mock_request:
            # Create chained exception properly
            ssl_error = ssl.SSLError("SSL handshake failed")
            connect_error = httpx.ConnectError("SSL error")
            # In Python 3, we can simulate the chain by setting __cause__
            connect_error.__cause__ = ssl_error
            mock_request.side_effect = connect_error

            keywords = Keywords()

            with pytest.raises(NetworkError) as exc_info:
                keywords.get("machine-learning")

            # Should have reference to original error
            assert "SSL" in str(exc_info.value)

    def test_connection_timeout_handling(self):
        """Test proper timeout error handling with operation context."""
        from openalex import Works, OpenAlexConfig
        from openalex.exceptions import TimeoutError
        import httpx

        config = OpenAlexConfig(timeout=0.5)

        from openalex.api import _connection_pool
        _connection_pool.clear()

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            works = Works(config=config)

            with pytest.raises(TimeoutError):
                works.search("machine learning").get()

    def test_async_connection_lifecycle(self):
        """Test async connection open/close lifecycle."""
        from openalex.connection import AsyncConnection
        from openalex import OpenAlexConfig

        @pytest.mark.asyncio
        async def run_test():
            config = OpenAlexConfig()
            conn = AsyncConnection(config)

            async with conn:
                assert conn._client is not None

            assert conn._client is None

        asyncio.run(run_test())

    def test_operation_specific_timeouts(self):
        """Test different timeouts for different operations."""
        from openalex import Works, OpenAlexConfig

        config = OpenAlexConfig(
            operation_timeouts={
                "get": 5.0,
                "list": 10.0,
                "search": 15.0,
                "autocomplete": 2.0,
            }
        )

        test_cases = [
            ("get", lambda w: w.get("W123"), 5.0),
            ("list", lambda w: w.list(), 10.0),
            ("search", lambda w: w.search("test").get(), 15.0),
            ("autocomplete", lambda w: w.autocomplete("test"), 2.0),
        ]

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": []}),
            )

            works = Works(config=config)

            for _operation, func, expected_timeout in test_cases:
                func(works)
                assert isinstance(mock_request.call_args.kwargs["timeout"], httpx.Timeout)
                assert mock_request.call_args.kwargs["timeout"].read == expected_timeout
