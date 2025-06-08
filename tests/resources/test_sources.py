import pytest

from openalex.models import Source


def test_by_issn(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/sources/issn:12345678?mailto=test%40example.com",
        json={"id": "https://openalex.org/S123"},
    )
    source = client.sources.by_issn("1234-5678")
    assert source.id == "https://openalex.org/S123"


@pytest.mark.asyncio
async def test_async_by_issn(async_client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/sources/issn:87654321?mailto=test%40example.com",
        json={"id": "https://openalex.org/S876"},
    )
    source = await async_client.sources.by_issn("8765-4321")
    assert isinstance(source, Source)
