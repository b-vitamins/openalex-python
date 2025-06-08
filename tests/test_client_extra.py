import asyncio
from typing import Any

import httpx
import pytest

from openalex import AsyncOpenAlex, OpenAlex
from openalex.models import ListResult, Meta
from openalex.resources.base import BaseResource


@pytest.fixture
def sync_client(config):
    c = OpenAlex(config=config)
    yield c
    c.close()


@pytest.mark.asyncio
async def test_async_client_api_key_override(config):
    client = AsyncOpenAlex(config=config, api_key="abc")
    try:
        assert client.config.api_key == "abc"
        assert "Authorization" in client.config.headers
    finally:
        await client.close()


def test_request_retry(monkeypatch, sync_client):
    calls = {"wait_sync": [], "attempts": 0}

    def fake_acquire() -> float:
        return 0.1

    def fake_wait_sync(seconds: float) -> None:
        calls["wait_sync"].append(seconds)

    def fake_get_wait_time(err: Exception, attempt: int) -> float:
        return 0.0

    def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        if calls["attempts"] == 1:
            raise httpx.TimeoutException("timeout")
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(sync_client.rate_limiter, "acquire", fake_acquire)
    monkeypatch.setattr(sync_client.retry_handler, "wait_sync", fake_wait_sync)
    monkeypatch.setattr(sync_client.retry_handler, "get_wait_time", fake_get_wait_time)
    monkeypatch.setattr(sync_client._client, "request", fake_request)

    resp = sync_client._request("GET", "https://api.openalex.org/test")
    assert resp.status_code == 200
    assert calls["attempts"] == 2
    assert calls["wait_sync"]


def test_search_all_error(monkeypatch, sync_client):
    result = ListResult(
        meta=Meta(count=1, db_response_time_ms=1, page=1, per_page=25, groups_count=0, next_cursor=None),
        results=[],
    )

    def stub_search(self, query: str, **params: Any) -> ListResult:
        return result

    monkeypatch.setattr(BaseResource, "search", stub_search)

    def fail_search(query: str, **params: Any) -> ListResult:
        raise ValueError("boom")

    monkeypatch.setattr(sync_client.authors, "search", fail_search)

    res = sync_client.search_all("foo")
    assert res["authors"].meta.count == 0
    assert res["works"].meta.count == 1


@pytest.mark.asyncio
async def test_async_request_retry(monkeypatch, config):
    client = AsyncOpenAlex(config=config)
    calls = {"attempts": 0}

    async def fake_request(method: str, url: str, params=None, **kwargs):
        calls["attempts"] += 1
        if calls["attempts"] == 1:
            raise httpx.NetworkError("net")
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
async def test_async_autocomplete_entity(httpx_mock, config, mock_autocomplete_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/autocomplete/works?q=ml&mailto=test%40example.com",
        json=mock_autocomplete_response,
    )
    async with AsyncOpenAlex(config=config) as client:
        res = await client.autocomplete("ml", entity_type="works")
        assert len(res.results) == 2


@pytest.mark.asyncio
async def test_async_search_all_error(monkeypatch, config):
    client = AsyncOpenAlex(config=config)
    async_result = ListResult(
        meta=Meta(count=1, db_response_time_ms=1, page=1, per_page=25, groups_count=0, next_cursor=None),
        results=[],
    )

    async def stub_search(self, query: str, **params: Any):
        return async_result

    async def fail_search(query: str, **params: Any):
        raise ValueError("fail")

    from openalex.resources.base import AsyncBaseResource

    monkeypatch.setattr(BaseResource, "search", stub_search)
    monkeypatch.setattr(AsyncBaseResource, "search", stub_search)
    monkeypatch.setattr(client.authors, "search", fail_search)

    results = await client.search_all("q")
    assert results["authors"].meta.count == 0
    assert results["works"].meta.count == 1
    await client.close()
