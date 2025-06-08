import pytest
from openalex.models import Author
from openalex.resources import AsyncAuthorsResource


@pytest.mark.asyncio
async def test_async_by_orcid(async_client, httpx_mock, mock_author_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/authors/https://orcid.org/0000-0003-4237-824X?mailto=test%40example.com",
        json=mock_author_response,
    )
    author = await async_client.authors.by_orcid("0000-0003-4237-824X")
    assert isinstance(author, Author)
    assert author.id == mock_author_response["id"]
