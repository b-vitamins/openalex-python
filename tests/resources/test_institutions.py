import pytest

from openalex.models import Institution


def test_by_ror(client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/institutions/https://ror.org/03vek6s52?mailto=test%40example.com",
        json={"id": "https://openalex.org/I123"},
    )
    institution = client.institutions.by_ror("03vek6s52")
    assert isinstance(institution, Institution)


@pytest.mark.asyncio
async def test_async_by_ror(async_client, httpx_mock):
    httpx_mock.add_response(
        url="https://api.openalex.org/institutions/https://ror.org/03abc9876?mailto=test%40example.com",
        json={"id": "https://openalex.org/I456"},
    )
    institution = await async_client.institutions.by_ror("03abc9876")
    assert institution.id == "https://openalex.org/I456"
