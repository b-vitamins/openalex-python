"""Tests for OpenAlex client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
import pytest

from openalex import AsyncOpenAlex, OpenAlex, OpenAlexConfig
from openalex.exceptions import NetworkError, NotFoundError, RateLimitError
from openalex.models import ListResult, Meta
from openalex.resources.base import AsyncBaseResource, BaseResource
from openalex.utils import RetryConfig, RetryHandler

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

    def test_text_aboutness(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test tagging free text."""
        aboutness = {"meta": {"title": "foo"}, "topics": []}
        httpx_mock.add_response(
            url="https://api.openalex.org/text?mailto=test%40example.com&title=foo",
            json=aboutness,
        )

        result = client.text_aboutness(title="foo")
        assert result["meta"]["title"] == "foo"

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
    async def test_async_text_aboutness(
        self,
        httpx_mock: HTTPXMock,
    ) -> None:
        aboutness = {"meta": {"title": "bar"}, "topics": []}
        httpx_mock.add_response(
            url="https://api.openalex.org/text?mailto=test%40example.com&title=bar",
            json=aboutness,
        )
        async with AsyncOpenAlex(email="test@example.com") as client:
            result = await client.text_aboutness(title="bar")
            assert result["meta"]["title"] == "bar"

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


@pytest.mark.asyncio
async def test_async_client_api_key_override(config: OpenAlexConfig) -> None:
    client = AsyncOpenAlex(config=config, api_key="abc")
    try:
        assert client.config.api_key == "abc"
        assert "Authorization" in client.config.headers
    finally:
        await client.close()


def test_request_retry(
    monkeypatch: pytest.MonkeyPatch, client: OpenAlex
) -> None:
    calls: dict[str, Any] = {"wait_sync": [], "attempts": 0}

    def fake_acquire() -> float:
        return 0.1

    def fake_wait_sync(seconds: float) -> None:
        calls["wait_sync"].append(seconds)

    def fake_get_wait_time(err: Exception, attempt: int) -> float:
        return 0.0

    def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        if calls["attempts"] == 1:
            message = "timeout"
            raise httpx.TimeoutException(message)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client.rate_limiter, "acquire", fake_acquire)
    monkeypatch.setattr(client.retry_handler, "wait_sync", fake_wait_sync)
    monkeypatch.setattr(
        client.retry_handler, "get_wait_time", fake_get_wait_time
    )
    monkeypatch.setattr(client._client, "request", fake_request)

    resp = client._request("GET", "https://api.openalex.org/test")
    assert resp.status_code == 200
    assert calls["attempts"] == 2
    assert calls["wait_sync"]


def test_request_non_retryable(
    monkeypatch: pytest.MonkeyPatch, client: OpenAlex
) -> None:
    """Non-retryable errors are raised immediately."""
    def fake_request(method: str, url: str, params=None, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(client._client, "request", fake_request)
    monkeypatch.setattr(client.retry_handler, "should_retry", lambda e, a: False)

    with pytest.raises(ValueError):
        client._request("GET", "https://api.openalex.org/test")


def test_search_all_error(
    monkeypatch: pytest.MonkeyPatch, client: OpenAlex
) -> None:
    result = ListResult(
        meta=Meta(
            count=1,
            db_response_time_ms=1,
            page=1,
            per_page=25,
            groups_count=0,
            next_cursor=None,
        ),
        results=[],
    )

    def stub_search(self, query: str, **params: Any) -> ListResult:
        return result

    monkeypatch.setattr(BaseResource, "search", stub_search)

    def fail_search(query: str, **params: Any) -> ListResult:
        msg = "boom"
        raise ValueError(msg)

    monkeypatch.setattr(client.authors, "search", fail_search)

    res = client.search_all("foo")
    assert res["authors"].meta.count == 0
    assert res["works"].meta.count == 1


@pytest.mark.asyncio
async def test_async_request_retry(
    monkeypatch: pytest.MonkeyPatch, config: OpenAlexConfig
) -> None:
    client = AsyncOpenAlex(config=config)
    calls = {"attempts": 0}

    async def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        if calls["attempts"] == 1:
            message = "net"
            raise httpx.NetworkError(message)
        return httpx.Response(200, json={"ok": True})

    async def fake_wait(seconds: float) -> None:
        return None

    async def acquire_zero() -> int:
        return 0

    monkeypatch.setattr(client.rate_limiter, "acquire", acquire_zero)
    monkeypatch.setattr(client.retry_handler, "wait", fake_wait)
    monkeypatch.setattr(client.retry_handler, "get_wait_time", lambda e, a: 0)
    monkeypatch.setattr(client._client, "request", fake_request)

    resp = await client._request("GET", "https://api.openalex.org/test")
    assert resp.status_code == 200
    assert calls["attempts"] == 2
    await client.close()


@pytest.mark.asyncio
async def test_async_autocomplete_entity(
    httpx_mock: HTTPXMock,
    config: OpenAlexConfig,
    mock_autocomplete_response: dict[str, Any],
) -> None:
    httpx_mock.add_response(
        url="https://api.openalex.org/autocomplete/works?q=ml&mailto=test%40example.com",
        json=mock_autocomplete_response,
    )
    async with AsyncOpenAlex(config=config) as client:
        res = await client.autocomplete("ml", entity_type="works")
        assert len(res.results) == 2


@pytest.mark.asyncio
async def test_async_search_all_error(
    monkeypatch: pytest.MonkeyPatch, config: OpenAlexConfig
) -> None:
    client = AsyncOpenAlex(config=config)
    async_result = ListResult(
        meta=Meta(
            count=1,
            db_response_time_ms=1,
            page=1,
            per_page=25,
            groups_count=0,
            next_cursor=None,
        ),
        results=[],
    )

    async def stub_search(self, query: str, **params: Any):
        return async_result

    async def fail_search(query: str, **params: Any):
        msg = "fail"
        raise ValueError(msg)

    monkeypatch.setattr(BaseResource, "search", stub_search)
    monkeypatch.setattr(AsyncBaseResource, "search", stub_search)
    monkeypatch.setattr(client.authors, "search", fail_search)

    results = await client.search_all("q")
    assert results["authors"].meta.count == 0
    assert results["works"].meta.count == 1
    await client.close()


def test_text_aboutness_with_abstract_and_type(client: OpenAlex, httpx_mock: HTTPXMock) -> None:
    aboutness = {"meta": {"title": "foo"}}
    httpx_mock.add_response(
        url="https://api.openalex.org/text/works?mailto=test%40example.com&title=foo&abstract=bar",
        json=aboutness,
    )
    result = client.text_aboutness(title="foo", abstract="bar", entity_type="works")
    assert result["meta"]["title"] == "foo"


def test_request_all_fail(monkeypatch: pytest.MonkeyPatch, client: OpenAlex) -> None:
    calls = {"attempts": 0}

    def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        msg = "boom"
        raise httpx.NetworkError(msg)

    monkeypatch.setattr(client._client, "request", fake_request)
    monkeypatch.setattr(client.retry_handler, "get_wait_time", lambda e, a: 0)
    monkeypatch.setattr(client.retry_handler, "wait_sync", lambda s: None)
    client.retry_config = RetryConfig(max_attempts=2, initial_wait=0)
    client.retry_handler = RetryHandler(client.retry_config)
    with pytest.raises(NetworkError):
        client._request("GET", "https://api.openalex.org/test")
    assert calls["attempts"] == 2



@pytest.mark.asyncio
async def test_async_text_aboutness_with_abstract_and_type(httpx_mock: HTTPXMock, config: OpenAlexConfig) -> None:
    aboutness = {"meta": {"title": "foo"}}
    httpx_mock.add_response(
        url="https://api.openalex.org/text/works?mailto=test%40example.com&title=foo&abstract=bar",
        json=aboutness,
    )
    async with AsyncOpenAlex(config=config) as client:
        result = await client.text_aboutness(title="foo", abstract="bar", entity_type="works")
        assert result["meta"]["title"] == "foo"


@pytest.mark.asyncio
async def test_async_request_all_fail(monkeypatch: pytest.MonkeyPatch, config: OpenAlexConfig) -> None:
    client = AsyncOpenAlex(config=config)
    calls = {"attempts": 0}

    async def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        msg = "boom"
        raise httpx.NetworkError(msg)

    monkeypatch.setattr(client._client, "request", fake_request)
    async def acquire_zero():
        return 0
    monkeypatch.setattr(client.rate_limiter, "acquire", acquire_zero)
    async def fake_wait(seconds: float) -> None:
        return None
    monkeypatch.setattr(client.retry_handler, "wait", fake_wait)
    monkeypatch.setattr(client.retry_handler, "get_wait_time", lambda e, a: 0)
    client.retry_config = RetryConfig(max_attempts=2, initial_wait=0)
    client.retry_handler = RetryHandler(client.retry_config)
    with pytest.raises(NetworkError):
        await client._request("GET", "https://api.openalex.org/test")
    assert calls["attempts"] == 2
    await client.close()

