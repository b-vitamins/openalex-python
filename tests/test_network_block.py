"""Tests for the network blocking plugin."""

from __future__ import annotations

import asyncio
import httpx
import pytest
import requests

from openalex import Works
from tests.plugins.network import NetworkAccessError


def test_requests_blocked(no_network: None) -> None:
    with pytest.raises(NetworkAccessError):
        requests.get("https://example.com")


def test_httpx_sync_blocked(no_network: None) -> None:
    client = httpx.Client()
    with pytest.raises(NetworkAccessError):
        client.get("https://example.com")


@pytest.mark.asyncio
async def test_httpx_async_blocked(no_network: None) -> None:
    client = httpx.AsyncClient()
    with pytest.raises(NetworkAccessError):
        await client.get("https://example.com")
    await client.aclose()


def test_openalex_client_blocked(no_network: None) -> None:
    works = Works()
    with pytest.raises(NetworkAccessError):
        works.get("W0")
