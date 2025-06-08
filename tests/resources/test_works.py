import pytest

from openalex.models import Work
from openalex.models.filters import WorksFilter
from openalex.resources import WorksResource


def test_clone_with_raw_filter(client):
    res = WorksResource(client, default_filter=WorksFilter(filter="type:article"))
    clone = res.cited_by("https://openalex.org/W1")
    assert clone._default_filter.filter["raw"] == "type:article"
    assert clone._default_filter.filter["cites"] == "W1"


def test_cited_by_full_url(client, httpx_mock, mock_list_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=authorships.institutions.id%3AI123&mailto=test%40example.com",
        json=mock_list_response,
    )
    resource = client.works.by_institution("https://openalex.org/I123")
    result = resource.list()
    assert result.meta.count == 100


@pytest.mark.asyncio
async def test_async_methods(async_client, httpx_mock, mock_list_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=authorships.author.id%3AA1&mailto=test%40example.com",
        json=mock_list_response,
    )
    resource = await async_client.works.by_author("https://openalex.org/A1")
    await resource.list()
    httpx_mock.add_response(
        url="https://api.openalex.org/works?per-page=200&page=1&mailto=test%40example.com",
        json=mock_list_response,
    )
    paginator = async_client.works.paginate(max_results=1)
    async for item in paginator:
        assert isinstance(item, Work)
        break
