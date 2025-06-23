"""
Test configuration behavior and its effects on client operations.
Tests how configuration affects behavior, not internal state.
"""

import pytest
from unittest.mock import Mock, patch
import os

from openalex.exceptions import ServerError, TemporaryError


class TestConfigurationBehavior:
    """Test how configuration affects client behavior."""

    def test_api_key_adds_authorization_header(self):
        """API key in config should add Authorization header to requests."""
        from openalex import Works, OpenAlexConfig

        config = OpenAlexConfig(api_key="sk-proj-abc123")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            works = Works(config=config)
            works.filter(is_oa=True).get()

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer sk-proj-abc123"

    def test_email_adds_user_agent_and_mailto(self):
        """Email in config should add to User-Agent and mailto param."""
        from openalex import Authors, OpenAlexConfig

        config = OpenAlexConfig(email="researcher@university.edu")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            authors = Authors(config=config)
            authors.search("climate change").get()

            _, kwargs = mock_request.call_args
            headers = kwargs.get("headers", {})
            params = kwargs.get("params", {})

            assert "researcher@university.edu" in headers.get("User-Agent", "")
            assert params.get("mailto") == "researcher@university.edu"

    def test_custom_user_agent_is_used(self):
        """Custom user agent should be included in requests."""
        from openalex import Institutions, OpenAlexConfig

        config = OpenAlexConfig(
            user_agent="MyResearchBot/1.0", email="bot@example.com"
        )

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            institutions = Institutions(config=config)
            institutions.get()

            _, kwargs = mock_request.call_args
            user_agent = kwargs.get("headers", {}).get("User-Agent", "")

            assert "MyResearchBot/1.0" in user_agent
            assert "bot@example.com" in user_agent

    def test_timeout_configuration(self):
        """Timeout config should set request timeout."""
        from openalex import Sources, OpenAlexConfig
        import httpx

        config = OpenAlexConfig(timeout=5.0)

        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            sources = Sources(config=config)
            sources.get()

            # Check client was created with timeout
            mock_client_class.assert_called()
            call_kwargs = mock_client_class.call_args[1]
            timeout = call_kwargs.get("timeout")

            assert isinstance(timeout, httpx.Timeout)
            assert timeout.connect == 5.0

    def test_retry_configuration_affects_retry_behavior(self):
        """Retry config should control retry attempts."""
        from openalex import Concepts, OpenAlexConfig

        config = OpenAlexConfig(max_retries=2)

        attempt_count = 0

        def mock_response(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            return Mock(
                status_code=503,
                json=Mock(return_value={"error": "Service unavailable"}),
                headers={},
            )

        with patch("httpx.Client.request", side_effect=mock_response):
            concepts = Concepts(config=config)

            with pytest.raises(TemporaryError):
                concepts.get("C123")

            # Should try initial + 2 retries = 3 total
            assert attempt_count == 3

    def test_cache_disabled_by_default(self):
        """Cache should be disabled by default."""
        from openalex import Publishers

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": "P123",
                        "display_name": "Test Publisher",
                    }
                ),
            )

            publishers = Publishers()  # No config = defaults

            # Multiple identical requests
            publishers.get("P123")
            publishers.get("P123")

            # Both should hit API (no caching)
            assert mock_request.call_count == 2

    def test_cache_enabled_reduces_api_calls(self):
        """Enabling cache should reduce duplicate API calls."""
        from openalex import Funders, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"id": "F123", "display_name": "NSF"}),
            )

            funders = Funders(config=config)

            # Multiple identical requests
            funder1 = funders.get("F123")
            funder2 = funders.get("F123")
            funder3 = funders.get("F123")

            # Only one API call (rest from cache)
            assert mock_request.call_count == 1
            assert (
                funder1.display_name
                == funder2.display_name
                == funder3.display_name
            )

    def test_cache_configuration_options(self):
        """Cache configuration should control cache behavior."""
        from openalex import Topics, OpenAlexConfig
        import time

        config = OpenAlexConfig(
            cache_enabled=True,
            cache_ttl=0.1,  # 100ms TTL
            cache_maxsize=2,  # Small cache
        )

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(
                        return_value={"id": "T1", "display_name": "Topic 1"}
                    ),
                ),
                Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "id": "T1",
                            "display_name": "Topic 1 Updated",
                        }
                    ),
                ),
            ]

            topics = Topics(config=config)

            # First call
            topic1 = topics.get("T1")
            assert topic1.display_name == "Topic 1"

            # Wait for TTL to expire
            time.sleep(0.2)

            # Second call (cache expired)
            topic2 = topics.get("T1")
            assert topic2.display_name == "Topic 1 Updated"

            assert mock_request.call_count == 2

    def test_base_url_configuration(self):
        """Custom base URL should be used for requests."""
        from openalex import Keywords, OpenAlexConfig

        config = OpenAlexConfig(base_url="https://api.staging.openalex.org")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            keywords = Keywords(config=config)
            keywords.search("machine learning").get()

            _, kwargs = mock_request.call_args
            url = kwargs.get("url", "")

            assert url.startswith("https://api.staging.openalex.org")

    def test_environment_variable_configuration(self):
        """Config should read from environment variables."""
        from openalex import OpenAlexConfig

        # Set environment variables
        with patch.dict(
            os.environ,
            {
                "OPENALEX_API_KEY": "env-key-123",
                "OPENALEX_EMAIL": "env@example.com",
            },
        ):
            config = OpenAlexConfig()

            assert config.api_key == "env-key-123"
            assert config.email == "env@example.com"

    def test_config_precedence(self):
        """Explicit config should override environment variables."""
        from openalex import OpenAlexConfig

        with patch.dict(
            os.environ,
            {
                "OPENALEX_API_KEY": "env-key",
                "OPENALEX_EMAIL": "env@example.com",
            },
        ):
            config = OpenAlexConfig(
                api_key="explicit-key",
                # email not set explicitly
            )

            assert config.api_key == "explicit-key"  # Explicit wins
            assert config.email == "env@example.com"  # Falls back to env

    def test_config_affects_all_entity_types(self):
        """Configuration should apply to all entity types."""
        from openalex import Works, Authors, Institutions, OpenAlexConfig

        config = OpenAlexConfig(api_key="shared-key")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            # Test different entity types
            Works(config=config).get()
            Authors(config=config).get()
            Institutions(config=config).get()

            # All should use the same API key
            for call in mock_request.call_args_list:
                _, kwargs = call
                assert kwargs["headers"]["Authorization"] == "Bearer shared-key"

    def test_config_validation(self):
        """Config should validate input values."""
        from openalex import OpenAlexConfig

        # Invalid timeout
        with pytest.raises(ValueError):
            OpenAlexConfig(timeout=-1)

        # Invalid cache TTL
        with pytest.raises(ValueError):
            OpenAlexConfig(cache_ttl=-1)

        # Invalid max retries
        with pytest.raises(ValueError):
            OpenAlexConfig(max_retries=-1)

    def test_config_immutability(self):
        """Config should not be modifiable after creation."""
        from openalex import OpenAlexConfig

        config = OpenAlexConfig(api_key="original-key")

        # Attempt to modify
        with pytest.raises(AttributeError):
            config.api_key = "new-key"

    def test_per_request_config_override(self):
        """Should be able to override config per request."""
        from openalex import Works, OpenAlexConfig

        default_config = OpenAlexConfig(api_key="default-key")
        special_config = OpenAlexConfig(api_key="special-key")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            works = Works(config=default_config)

            # Regular request uses default
            works.get()
            _, kwargs = mock_request.call_args
            assert kwargs["headers"]["Authorization"] == "Bearer default-key"

            # Can override for specific request
            works_special = Works(config=special_config)
            works_special.get()
            _, kwargs = mock_request.call_args
            assert kwargs["headers"]["Authorization"] == "Bearer special-key"
