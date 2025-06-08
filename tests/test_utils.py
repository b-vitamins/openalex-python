import asyncio
import random
import time
from typing import Any

import pytest

from openalex.exceptions import APIError, NetworkError, RateLimitError
from openalex.models import ListResult, Meta, Work
from openalex.utils import (
    AsyncPaginator,
    AsyncRateLimiter,
    Paginator,
    RateLimiter,
    RetryConfig,
    RetryHandler,
    SlidingWindowRateLimiter,
    async_rate_limited,
    async_with_retry,
    is_retryable_error,
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


def test_paginator_pages_and_max_results() -> None:
    total = 6

    def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = Paginator(fetch, per_page=2, max_results=3)
    items = list(paginator)
    assert len(items) == 3

    paginator2 = Paginator(fetch, per_page=2)
    pages = list(paginator2.pages())
    assert len(pages) == 3


def test_paginator_error() -> None:
    def fetch(_: dict[str, Any]) -> ListResult[Work]:
        raise APIError("oops", status_code=500)

    paginator = Paginator(fetch)
    with pytest.raises(APIError):
        list(paginator)


@pytest.mark.asyncio
async def test_async_paginator_pages_first_all() -> None:
    total = 5

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=2)
    pages = []
    async for p in paginator.pages():
        pages.append(p)
    assert len(pages) == 3
    assert await paginator.first()
    results = await paginator.all()
    assert len(results) == total


@pytest.mark.asyncio
async def test_async_paginator_error() -> None:
    async def fetch(_: dict[str, Any]) -> ListResult[Work]:
        raise APIError("bad", status_code=500)

    paginator = AsyncPaginator(fetch)
    with pytest.raises(APIError):
        async for _ in paginator:
            pass


@pytest.mark.asyncio
async def test_async_paginator_gather_max_results() -> None:
    total = 10

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        page = int(params.get("page", 1))
        per_page = int(params.get("per-page", 3))
        start = (page - 1) * per_page
        cursor = "next" if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=3, concurrency=2)
    results = await paginator.gather(pages=2)
    assert len(results) == 6


def test_rate_limiter_try_acquire_success() -> None:
    limiter = RateLimiter(rate=1, burst=2, buffer=0)
    assert limiter.try_acquire()
    assert limiter.try_acquire()
    assert not limiter.try_acquire()


def test_sliding_window_rate_limiter() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.1, buffer=0)
    assert limiter.try_acquire()
    assert limiter.try_acquire()
    assert not limiter.try_acquire()
    wait = limiter.acquire()
    assert wait > 0


@pytest.mark.asyncio
async def test_async_rate_limiter_context(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    limiter = AsyncRateLimiter(rate=1, burst=1, buffer=0)
    await limiter.acquire()
    async with limiter:
        pass
    assert calls


def test_is_retryable_error() -> None:
    assert is_retryable_error(RateLimitError())
    assert is_retryable_error(NetworkError())
    assert is_retryable_error(APIError("server", status_code=500))
    assert not is_retryable_error(APIError("client", status_code=400))
    assert not is_retryable_error(Exception("boom"))


def test_retry_config_wait_strategy() -> None:
    config = RetryConfig(jitter=False)
    strategy = config.get_wait_strategy()
    from tenacity import wait_exponential

    assert isinstance(strategy, type(wait_exponential()))


@pytest.mark.asyncio
async def test_retry_handler_should_retry_and_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = RetryHandler(RetryConfig(max_attempts=2))
    assert handler.should_retry(APIError("server", status_code=500), 1)
    assert not handler.should_retry(APIError("server", status_code=500), 2)

    async_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        async_calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    await handler.wait(1)
    assert async_calls == [1]

    sync_calls: list[float] = []

    def fake_sleep_sync(seconds: float) -> None:
        sync_calls.append(seconds)

    monkeypatch.setattr(time, "sleep", fake_sleep_sync)
    handler.wait_sync(2)
    assert sync_calls == [2]


