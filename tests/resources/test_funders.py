import pytest
from openalex.models import Funder


def test_by_ror(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/funders/https://ror.org/12345?mailto=test%40example.com",
        json={"id": "https://openalex.org/F123"},
    )
    funder = client.funders.by_ror("12345")
    assert funder.id == "https://openalex.org/F123"


@pytest.mark.asyncio
async def test_async_by_ror(async_client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/funders/https://ror.org/67890?mailto=test%40example.com",
        json={"id": "https://openalex.org/F678"},
    )
    funder = await async_client.funders.by_ror("67890")
    assert isinstance(funder, Funder)
