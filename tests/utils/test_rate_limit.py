from __future__ import annotations

import asyncio
import time

import pytest

from openalex.utils import (
    AsyncRateLimiter,
    RateLimiter,
    SlidingWindowRateLimiter,
    async_rate_limited,
    rate_limited,
)


def test_rate_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    limiter = RateLimiter(rate=1, burst=1, buffer=0)
    assert limiter.acquire() == 0
    wait = limiter.acquire()
    assert wait > 0
    assert not limiter.try_acquire()


@pytest.mark.asyncio()
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
    assert calls
    assert calls[0] > 0


@pytest.mark.asyncio()
async def test_async_rate_limited_decorator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_rate_limiter_try_acquire_success() -> None:
    limiter = RateLimiter(rate=1, burst=2, buffer=0)
    assert limiter.try_acquire()
    assert limiter.try_acquire()
    assert not limiter.try_acquire()


def test_sliding_window_rate_limiter() -> None:
    limiter = SlidingWindowRateLimiter(
        max_requests=2, window_seconds=0.1, buffer=0
    )
    assert limiter.try_acquire()
    assert limiter.try_acquire()
    assert not limiter.try_acquire()
    wait = limiter.acquire()
    assert wait > 0


def test_sliding_window_rate_limiter_clean(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Old entries are removed when acquiring after the window."""
    orig = time.monotonic()
    monkeypatch.setattr(time, "monotonic", lambda: orig)
    limiter = SlidingWindowRateLimiter(
        max_requests=1, window_seconds=0.1, buffer=0
    )
    assert limiter.acquire() == 0.0

    wait = limiter.acquire()
    assert wait > 0

    monkeypatch.setattr(time, "monotonic", lambda: orig + 0.2)
    wait_after = limiter.acquire()
    assert wait_after == 0.0


@pytest.mark.asyncio()
async def test_async_rate_limiter_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    limiter = AsyncRateLimiter(rate=1, burst=1, buffer=0)
    await limiter.acquire()
    async with limiter:
        pass
    assert calls
