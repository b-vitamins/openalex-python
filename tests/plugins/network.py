from __future__ import annotations

from typing import Any

import httpx
import pytest
import requests


class NetworkAccessError(RuntimeError):
    """Raised when a test attempts to access the real network."""


# Synchronous and asynchronous blockers ---------------------------------------

def _fail(*_args: Any, **_kwargs: Any) -> None:
    raise NetworkAccessError("Network access blocked during tests")


async def _async_fail(*_args: Any, **_kwargs: Any) -> None:
    raise NetworkAccessError("Network access blocked during tests")


# Pytest fixture ---------------------------------------------------------------

@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Disable outbound network access unless a test uses ``requires_api``."""

    if "requires_api" in request.keywords:
        yield
        return

    monkeypatch.setattr(requests, "get", _fail)
    monkeypatch.setattr(requests, "post", _fail)
    monkeypatch.setattr(httpx.Client, "request", _fail)
    monkeypatch.setattr(httpx.Client, "send", _fail)
    monkeypatch.setattr(httpx.AsyncClient, "request", _async_fail)
    monkeypatch.setattr(httpx.AsyncClient, "send", _async_fail)
    yield
