import pytest

from openalex.models import Concept


def test_by_wikidata_formats(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/concepts/https://www.wikidata.org/entity/Q123?mailto=test%40example.com",
        json={"id": "https://openalex.org/C123"},
    )
    concept = client.concepts.by_wikidata("Q123")
    assert isinstance(concept, Concept)

    httpx_mock.add_response(
        url="https://api.openalex.org/concepts/https://www.wikidata.org/entity/Q456?mailto=test%40example.com",
        json={"id": "https://openalex.org/C456"},
    )
    concept = client.concepts.by_wikidata("456")
    assert concept.id == "https://openalex.org/C456"


@pytest.mark.asyncio()
async def test_async_by_wikidata(async_client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/concepts/https://www.wikidata.org/entity/Q789?mailto=test%40example.com",
        json={"id": "https://openalex.org/C789"},
    )
    concept = await async_client.concepts.by_wikidata("789")
    assert concept.id == "https://openalex.org/C789"
