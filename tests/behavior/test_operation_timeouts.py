import pytest
from unittest.mock import patch, Mock
import httpx

from openalex import Works, OpenAlexConfig


class TestOperationTimeouts:
    def test_get_uses_get_timeout(self):
        """Single entity fetch should use 'get' timeout."""
        config = OpenAlexConfig(
            operation_timeouts={
                "get": 5.0,
                "list": 30.0,
            }
        )
        works = Works(config=config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"id": "W123"})
            )

            works.get("W123")

            _, kwargs = mock_request.call_args
            timeout = kwargs.get("timeout")
            assert timeout.connect == 5.0

    def test_search_uses_search_timeout(self):
        """Search operations should use 'search' timeout."""
        config = OpenAlexConfig(
            operation_timeouts={
                "search": 20.0,
                "list": 30.0,
            }
        )
        works = Works(config=config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value={"results": []})
            )

            works.search("machine learning").get()

            _, kwargs = mock_request.call_args
            timeout = kwargs.get("timeout")
            assert timeout.connect == 20.0
