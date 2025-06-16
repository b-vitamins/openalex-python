"""
Test OpenAlex client behavior based on expected API interactions.
Follows strict TDD principles - tests behavior, not implementation.
"""

import pytest
from unittest.mock import Mock, patch
import httpx


class TestOpenAlexClient:
    """Test the core client functionality with proper API mocking."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock HTTP response."""

        def _mock_response(json_data=None, status_code=200, headers=None):
            response = Mock(spec=httpx.Response)
            response.status_code = status_code
            response.json.return_value = json_data or {}
            response.headers = headers or {}
            response.text = ""
            return response

        return _mock_response

    def test_client_makes_authenticated_request_with_api_key(
        self, mock_response
    ):
        """Client should include API key in Authorization header when configured."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient

        config = OpenAlexConfig(api_key="test-key-123")
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response({"results": []})

            client.get("/works")

            mock_request.assert_called_once()
            _, kwargs = mock_request.call_args
            assert kwargs["headers"]["Authorization"] == "Bearer test-key-123"

    def test_client_includes_user_agent_with_email(self, mock_response):
        """Client should include email in User-Agent header for polite pool."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient

        config = OpenAlexConfig(email="researcher@university.edu")
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response({"results": []})

            client.get("/authors")

            mock_request.assert_called_once()
            _, kwargs = mock_request.call_args
            assert (
                "researcher@university.edu" in kwargs["headers"]["User-Agent"]
            )

    def test_client_handles_rate_limit_response(self, mock_response):
        """Client should raise RateLimitError with retry_after from headers."""
        from openalex.client import OpenAlexClient
        from openalex.exceptions import RateLimitError

        from openalex import OpenAlexConfig

        config = OpenAlexConfig(max_retries=1)
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"error": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "60"},
            )

            with pytest.raises(RateLimitError) as exc_info:
                client.get("/works")

            assert exc_info.value.retry_after == 60

    def test_client_handles_not_found_response(self, mock_response):
        """Client should raise NotFoundError for 404 responses."""
        from openalex.client import OpenAlexClient
        from openalex.exceptions import NotFoundError

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"error": "Entity not found"}, status_code=404
            )

            with pytest.raises(NotFoundError) as exc_info:
                client.get("/works/W99999999")

            assert "Entity not found" in str(exc_info.value)

    def test_client_handles_server_error_response(self, mock_response):
        """Client should raise ServerError for 5xx responses."""
        from openalex.client import OpenAlexClient
        from openalex.exceptions import ServerError

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"error": "Internal server error"}, status_code=500
            )

            with pytest.raises(ServerError):
                client.get("/works")

    def test_client_handles_network_timeout(self):
        """Client should raise TimeoutError on request timeout."""
        from openalex.client import OpenAlexClient
        from openalex.exceptions import TimeoutError

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException(
                "Request timed out"
            )

            with pytest.raises(TimeoutError):
                client.get("/works")

    def test_client_retries_on_temporary_errors(self, mock_response):
        """Client should retry requests on temporary server errors."""
        from openalex.client import OpenAlexClient

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            # First two calls fail, third succeeds
            mock_request.side_effect = [
                mock_response({"error": "Server error"}, status_code=503),
                mock_response({"error": "Server error"}, status_code=503),
                mock_response({"results": [{"id": "W123"}]}, status_code=200),
            ]

            response = client.get("/works")

            assert mock_request.call_count == 3
            assert response["results"][0]["id"] == "W123"

    def test_client_respects_retry_limit(self, mock_response):
        """Client should stop retrying after max attempts."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient
        from openalex.exceptions import ServerError

        config = OpenAlexConfig(max_retries=2)
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"error": "Server error"}, status_code=503
            )

            with pytest.raises(ServerError):
                client.get("/works")

            assert mock_request.call_count == 3

    def test_client_follows_cursor_pagination(self, mock_response):
        """Client should follow cursor-based pagination."""
        from openalex.client import OpenAlexClient

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                mock_response(
                    {
                        "results": [{"id": "W1"}, {"id": "W2"}],
                        "meta": {"next_cursor": "cursor123"},
                    }
                ),
                mock_response(
                    {"results": [{"id": "W3"}], "meta": {"next_cursor": None}}
                ),
            ]

            # Simulate paginated request
            pages = []
            params = {}

            while True:
                response = client.get("/works", params=params)
                pages.append(response)

                if not response["meta"].get("next_cursor"):
                    break

                params["cursor"] = response["meta"]["next_cursor"]

            assert len(pages) == 2
            assert pages[0]["results"][0]["id"] == "W1"
            assert pages[1]["results"][0]["id"] == "W3"

    def test_client_caches_responses_when_enabled(self, mock_response):
        """Client should cache GET requests when caching is enabled."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient

        config = OpenAlexConfig(cache_enabled=True)
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"id": "W123", "title": "Cached Work"}
            )

            # First request
            response1 = client.get("/works/W123")

            # Second request (should be cached)
            response2 = client.get("/works/W123")

            # Only one actual HTTP request
            assert mock_request.call_count == 1
            assert response1 == response2
            assert response1["title"] == "Cached Work"

    def test_client_respects_cache_ttl(self, mock_response):
        """Client should respect cache TTL and refetch after expiration."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient
        import time

        config = OpenAlexConfig(cache_enabled=True, cache_ttl=0.1)  # 100ms TTL
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                mock_response({"version": 1}),
                mock_response({"version": 2}),
            ]

            # First request
            response1 = client.get("/works/W123")
            assert response1["version"] == 1

            # Wait for cache to expire
            time.sleep(0.2)

            # Second request (cache expired)
            response2 = client.get("/works/W123")
            assert response2["version"] == 2

            assert mock_request.call_count == 2

    def test_client_normalizes_entity_ids(self, mock_response):
        """Client should accept various ID formats and normalize them."""
        from openalex.client import OpenAlexClient

        client = OpenAlexClient()

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"id": "https://openalex.org/W123"}
            )

            # Test various ID formats
            for id_format in [
                "W123",
                "https://openalex.org/W123",
                "w123",
                "W123 ",
            ]:
                client.get(f"/works/{id_format}")

            # All should normalize to the same endpoint
            calls = mock_request.call_args_list
            assert all(call[0][1].endswith("/works/W123") for call in calls)

    def test_retry_counts_correctly(self, mock_response):
        """Verify exactly N+1 attempts are made for N retries."""
        from openalex import OpenAlexConfig
        from openalex.client import OpenAlexClient
        from openalex.exceptions import ServerError

        config = OpenAlexConfig(max_retries=2)
        client = OpenAlexClient(config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = mock_response(
                {"error": "Server error"}, status_code=503
            )

            with pytest.raises(ServerError):
                client.get("/works")

            assert mock_request.call_count == 3

    def test_enhanced_validation_error(self):
        """Check new error fields are populated correctly."""
        from openalex.exceptions import ValidationError

        err = ValidationError(
            "bad value",
            field_path=["works", "year"],
            invalid_value="abc",
            expected_type="int",
        )

        assert err.field_path == ["works", "year"]
        assert err.invalid_value == "abc"
        assert err.expected_type == "int"
