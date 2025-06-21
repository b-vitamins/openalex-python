"""Tests for the network blocking plugin."""

from __future__ import annotations

import asyncio
import httpx
import pytest
import requests

from openalex import Works
from tests.conftest import NetworkAccessError


@pytest.mark.skip(reason="Network blocking tests need special setup")
def test_requests_blocked() -> None:
    """Test that requests library is blocked by network isolation."""
    with pytest.raises(NetworkAccessError):
        requests.get("https://example.com")


@pytest.mark.skip(reason="Network blocking tests need special setup")
def test_httpx_sync_blocked() -> None:
    """Test that httpx sync client is blocked by network isolation."""
    client = httpx.Client()
    with pytest.raises(NetworkAccessError):
        client.get("https://example.com")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Network blocking tests need special setup")
async def test_httpx_async_blocked() -> None:
    """Test that httpx async client is blocked by network isolation."""
    client = httpx.AsyncClient()
    with pytest.raises(NetworkAccessError):
        await client.get("https://example.com")
    await client.aclose()


@pytest.mark.skip(reason="Network blocking tests need special setup")
def test_openalex_client_blocked() -> None:
    """Test that OpenAlex client is blocked by network isolation."""
    works = Works()
    with pytest.raises(NetworkAccessError):
        works.get("W0")
