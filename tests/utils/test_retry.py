from __future__ import annotations

import asyncio
import random
import time

import pytest

from openalex.exceptions import APIError, NetworkError, RateLimitError
from openalex.utils import (
    RetryConfig,
    RetryHandler,
    async_with_retry,
    is_retryable_error,
    with_retry,
)


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
    wrapped = async_with_retry(
        func, RetryConfig(max_attempts=3, initial_wait=0)
    )
    assert await wrapped() == "done"
    assert len(attempts) == 3


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
async def test_retry_handler_should_retry_and_wait(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_with_retry_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts: list[int] = []

    def func() -> None:
        attempts.append(1)
        msg = "err"
        raise APIError(msg, status_code=500)

    monkeypatch.setattr(time, "sleep", lambda _: None)
    wrapped = with_retry(func, RetryConfig(max_attempts=2, initial_wait=0))
    with pytest.raises(APIError):
        wrapped()
    assert len(attempts) == 2


@pytest.mark.asyncio
async def test_async_with_retry_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts: list[int] = []

    async def func() -> None:
        attempts.append(1)
        msg = "err"
        raise APIError(msg, status_code=500)

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    wrapped = async_with_retry(
        func, RetryConfig(max_attempts=2, initial_wait=0)
    )
    with pytest.raises(APIError):
        await wrapped()
    assert len(attempts) == 2


def test_with_retry_default_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure default config is used when none is provided."""
    attempts: list[int] = []

    def func() -> str:
        attempts.append(1)
        if len(attempts) < 2:
            raise RateLimitError(retry_after=0)
        return "ok"

    monkeypatch.setattr(time, "sleep", lambda _: None)
    wrapped = with_retry(func)
    assert wrapped() == "ok"
    assert len(attempts) == 2


@pytest.mark.asyncio
async def test_async_with_retry_default_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Async version uses default config when not provided."""
    attempts: list[int] = []

    async def func() -> str:
        attempts.append(1)
        if len(attempts) < 2:
            raise RateLimitError(retry_after=0)
        return "ok"

    async def fake_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    wrapped = async_with_retry(func)
    assert await wrapped() == "ok"
    assert len(attempts) == 2


def test_retry_handler_get_wait_time(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = RetryHandler(RetryConfig(jitter=False))
    err = RateLimitError(retry_after=5)
    assert handler.get_wait_time(err, 1) == 5.0

    handler_jitter = RetryHandler(RetryConfig(jitter=True))
    monkeypatch.setattr(random, "uniform", lambda a, b: 0)
    wait = handler_jitter.get_wait_time(NetworkError(), 2)
    assert (
        wait
        == handler_jitter.config.initial_wait
        * handler_jitter.config.exponential_base
    )
