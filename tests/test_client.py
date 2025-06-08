"""Tests for OpenAlex client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from openalex import AsyncOpenAlex, OpenAlex, OpenAlexConfig
from openalex.exceptions import NotFoundError, RateLimitError

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


class TestOpenAlexClient:
    """Test synchronous OpenAlex client."""

    def test_initialization(self) -> None:
        """Test client initialization."""
        client = OpenAlex(email="test@example.com")
        assert client.config.email == "test@example.com"
        assert client.works is not None
        assert client.authors is not None
        client.close()

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with OpenAlex(email="test@example.com") as client:
            assert client.config.email == "test@example.com"

    def test_config_override(self) -> None:
        """Test config parameter override."""
        config = OpenAlexConfig(email="config@example.com", timeout=10.0)
        client = OpenAlex(config=config, email="override@example.com")
        assert client.config.email == "override@example.com"
        assert client.config.timeout == 10.0
        client.close()

    def test_headers(self) -> None:
        """Test request headers."""
        client = OpenAlex(email="test@example.com", api_key="test-key")
        headers = client.config.headers
        assert "test@example.com" in headers["User-Agent"]
        assert headers["Authorization"] == "Bearer test-key"
        client.close()

    def test_autocomplete(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_autocomplete_response: dict[str, Any],
    ) -> None:
        """Test autocomplete functionality."""
        httpx_mock.add_response(
            url="https://api.openalex.org/autocomplete?q=machine+learning&mailto=test%40example.com",
            json=mock_autocomplete_response,
        )

        results = client.autocomplete("machine learning")
        assert len(results.results) == 2
        assert (
            results.results[0].display_name
            == "Generalized Gradient Approximation Made Simple"
        )
        assert results.results[0].entity_type == "work"

    def test_autocomplete_with_entity_type(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_autocomplete_response: dict[str, Any],
    ) -> None:
        """Test autocomplete with entity type filter."""
        httpx_mock.add_response(
            url="https://api.openalex.org/autocomplete/works?q=machine&mailto=test%40example.com",
            json=mock_autocomplete_response,
        )

        results = client.autocomplete("machine", entity_type="works")
        assert len(results.results) == 2

    def test_search_all(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test search across all entities."""
        # Mock responses for each entity type
        for entity_type in [
            "works",
            "authors",
            "institutions",
            "sources",
            "concepts",
            "topics",
            "publishers",
            "funders",
            "keywords",
        ]:
            httpx_mock.add_response(
                url=f"https://api.openalex.org/{entity_type}?search=test&mailto=test%40example.com",
                json=mock_list_response,
            )

        results = client.search_all("test")
        assert "works" in results
        assert "authors" in results
        assert len(results["works"].results) == 1

    def test_rate_limit_error(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test rate limit error handling."""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "60"},
            json={"error": "Rate limit exceeded"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.works.get("W123456")

        assert exc_info.value.retry_after == 60

    def test_not_found_error(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test not found error handling."""
        httpx_mock.add_response(
            status_code=404,
            json={"error": "Not found", "message": "Work not found"},
        )

        with pytest.raises(NotFoundError):
            client.works.get("W123456")


class TestAsyncOpenAlexClient:
    """Test asynchronous OpenAlex client."""

    @pytest.mark.asyncio
    async def test_initialization(self) -> None:
        """Test async client initialization."""
        client = AsyncOpenAlex(email="test@example.com")
        assert client.config.email == "test@example.com"
        assert client.works is not None
        assert client.authors is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test async client as context manager."""
        async with AsyncOpenAlex(email="test@example.com") as client:
            assert client.config.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_autocomplete(
        self,
        httpx_mock: HTTPXMock,
        mock_autocomplete_response: dict[str, Any],
    ) -> None:
        """Test async autocomplete functionality."""
        httpx_mock.add_response(
            url="https://api.openalex.org/autocomplete?q=machine+learning&mailto=test%40example.com",
            json=mock_autocomplete_response,
        )

        async with AsyncOpenAlex(email="test@example.com") as client:
            results = await client.autocomplete("machine learning")
            assert len(results.results) == 2
            assert results.results[0].entity_type == "work"

    @pytest.mark.asyncio
    async def test_search_all(
        self,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test async search across all entities."""
        # Mock responses for each entity type
        for entity_type in [
            "works",
            "authors",
            "institutions",
            "sources",
            "concepts",
            "topics",
            "publishers",
            "funders",
            "keywords",
        ]:
            httpx_mock.add_response(
                url=f"https://api.openalex.org/{entity_type}?search=test&mailto=test%40example.com",
                json=mock_list_response,
            )

        async with AsyncOpenAlex(email="test@example.com") as client:
            results = await client.search_all("test")
            assert "works" in results
            assert "authors" in results
            assert len(results["works"].results) == 1


class TestClientHelpers:
    """Test client helper functions."""

    def test_client_helper(
        self,
        httpx_mock: HTTPXMock,
        mock_work_response: dict[str, Any],
    ) -> None:
        """Test client helper function."""
        from openalex import client

        httpx_mock.add_response(
            url="https://api.openalex.org/works/W2741809807?mailto=test%40example.com",
            json=mock_work_response,
        )

        with client(email="test@example.com") as c:
            work = c.works.get("W2741809807")
            assert (
                work.title == "Generalized Gradient Approximation Made Simple"
            )

    @pytest.mark.asyncio
    async def test_async_client_helper(
        self,
        httpx_mock: HTTPXMock,
        mock_work_response: dict[str, Any],
    ) -> None:
        """Test async client helper function."""
        from openalex import async_client

        httpx_mock.add_response(
            url="https://api.openalex.org/works/W2741809807?mailto=test%40example.com",
            json=mock_work_response,
        )

        async with async_client(email="test@example.com") as c:
            work = await c.works.get("W2741809807")
            assert (
                work.title == "Generalized Gradient Approximation Made Simple"
            )
