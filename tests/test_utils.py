import asyncio
import random
import time
from typing import Any

import pytest

from openalex.exceptions import APIError, RateLimitError
from openalex.models import ListResult, Meta, Work
from openalex.utils import (
    AsyncPaginator,
    AsyncRateLimiter,
    Paginator,
    RateLimiter,
    RetryConfig,
    RetryHandler,
    async_rate_limited,
    async_with_retry,
    rate_limited,
    with_retry,
)


def _make_page(start: int, per_page: int, total: int, cursor: str | None = None) -> ListResult[Work]:
    meta = Meta(
        count=total,
        db_response_time_ms=1,
        page=start // per_page + 1,
        per_page=per_page,
        next_cursor=cursor,
    )
    results = [Work(id=f"W{i}", display_name=f"Work {i}") for i in range(start, start + per_page)]
    return ListResult(meta=meta, results=results)


def test_paginator_iteration() -> None:
    total = 5

    def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        next_cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, next_cursor)

    paginator = Paginator(fetch, per_page=2)
    items = list(paginator)
    assert [w.id for w in items] == ["W0", "W1", "W2", "W3", "W4"]
    assert paginator.first().id == "W0"
    assert paginator.count() == total


@pytest.mark.asyncio
async def test_async_paginator_gather() -> None:
    total = 5

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        page = int(params.get("page", 1))
        per_page = int(params.get("per-page", 2))
        start = (page - 1) * per_page
        cursor = "next" if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=2)
    results = await paginator.gather()
    assert len(results) == total
    assert results[0].id == "W0"


def test_rate_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = RateLimiter(rate=1, burst=1, buffer=0)
    assert limiter.acquire() == 0
    wait = limiter.acquire()
    assert wait > 0
    assert not limiter.try_acquire()


@pytest.mark.asyncio
async def test_async_rate_limiter() -> None:
    limiter = AsyncRateLimiter(rate=1, burst=1, buffer=0)
    assert await limiter.acquire() == 0
    wait = await limiter.acquire()
    assert wait > 0


def test_rate_limited_decorator(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    @rate_limited(1, burst=1, buffer=0)
    def func() -> str:
        return "ok"

    assert func() == "ok"
    assert func() == "ok"
    # second call should have waited
    assert calls
    assert calls[0] > 0


@pytest.mark.asyncio
async def test_async_rate_limited_decorator(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    @async_rate_limited(1, burst=1, buffer=0)
    async def func() -> str:
        return "ok"

    assert await func() == "ok"
    assert await func() == "ok"
    assert calls
    assert calls[0] > 0


def test_with_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    def func() -> str:
        attempts.append(1)
        if len(attempts) < 3:
            raise RateLimitError(retry_after=0)
        return "done"

    monkeypatch.setattr(time, "sleep", lambda x: None)
    wrapped = with_retry(func, RetryConfig(max_attempts=3, initial_wait=0))
    assert wrapped() == "done"
    assert len(attempts) == 3


@pytest.mark.asyncio
async def test_async_with_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    async def func() -> str:
        attempts.append(1)
        if len(attempts) < 3:
            raise RateLimitError(retry_after=0)
        return "done"

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    wrapped = async_with_retry(func, RetryConfig(max_attempts=3, initial_wait=0))
    assert await wrapped() == "done"
    assert len(attempts) == 3


def test_retry_handler_wait_time(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = RetryHandler(RetryConfig(jitter=False, initial_wait=1, exponential_base=2))
    err = RateLimitError(retry_after=5)
    assert handler.get_wait_time(err, 1) == 5

    monkeypatch.setattr(random, "uniform", lambda a, b: 0)
    err2 = APIError("server", status_code=500)
    assert handler.get_wait_time(err2, 2) == 2

