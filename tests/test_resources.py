"""Tests for OpenAlex resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from openalex.models import Author, Institution, Work
from openalex.utils import Paginator

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex


class TestWorksResource:
    """Test works resource."""

    def test_get_work(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_work_response: dict[str, Any],
    ) -> None:
        """Test getting a single work."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works/W2741809807?mailto=test%40example.com",
            json=mock_work_response,
        )

        work = client.works.get("W2741809807")
        assert isinstance(work, Work)
        assert work.title == "Generalized Gradient Approximation Made Simple"
        assert work.publication_year == 1996

    def test_get_work_with_full_url(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_work_response: dict[str, Any],
    ) -> None:
        """Test getting a work with full URL."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works/W2741809807?mailto=test%40example.com",
            json=mock_work_response,
        )

        work = client.works.get("https://openalex.org/W2741809807")
        assert work.id == "https://openalex.org/W2741809807"

    def test_list_works(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test listing works."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?mailto=test%40example.com",
            json=mock_list_response,
        )

        result = client.works.list()
        assert result.meta.count == 100
        assert len(result.results) == 1

    def test_search_works(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test searching works."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?search=machine+learning&mailto=test%40example.com",
            json=mock_list_response,
        )

        result = client.works.search("machine learning")
        assert result.meta.count == 100

    def test_filter_works(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test filtering works."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=is_oa%3Atrue%2Cpublication_year%3A2020%7C2021&mailto=test%40example.com",
            json=mock_list_response,
        )

        filter_obj = client.works.filter(
            filter={
                "is_oa": True,
                "publication_year": [2020, 2021],
            }
        )
        result = client.works.list(filter=filter_obj)
        assert result.meta.count == 100

    def test_works_filter_builder(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test works filter builder methods."""
        httpx_mock.add_response(
            method="GET",
            json=mock_list_response,
        )

        filter_obj = (
            client.works.filter()
            .with_publication_year([2020, 2021])
            .with_type("article")
            .with_open_access(True)
        )

        params = filter_obj.to_params()
        assert "publication_year:2020|2021" in params["filter"]
        assert "type:article" in params["filter"]
        assert "is_oa:true" in params["filter"]

    def test_works_pagination(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test works pagination."""
        # Mock first page
        httpx_mock.add_response(
            url="https://api.openalex.org/works?per-page=25&page=1&mailto=test%40example.com",
            json=mock_list_response,
        )

        paginator = client.works.paginate(per_page=25)
        assert isinstance(paginator, Paginator)

        # Get first item
        first_work = paginator.first()
        assert first_work is not None
        assert (
            first_work.title == "Generalized Gradient Approximation Made Simple"
        )

    def test_random_work(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_work_response: dict[str, Any],
    ) -> None:
        """Test getting random work."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works/random?mailto=test%40example.com",
            json=mock_work_response,
        )

        work = client.works.random()
        assert isinstance(work, Work)

    def test_cited_by(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test getting works that cite a work."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=cites%3AW123&mailto=test%40example.com",
            json=mock_list_response,
        )

        client.works.cited_by("W123").list()

    def test_references(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test getting works referenced by a work."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=cited_by%3AW123&mailto=test%40example.com",
            json=mock_list_response,
        )

        client.works.references("W123").list()

    def test_by_author(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test getting works by author."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=authorships.author.id%3AA123&mailto=test%40example.com",
            json=mock_list_response,
        )

        client.works.by_author("A123").list()

    def test_by_institution(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test getting works by institution."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=authorships.institutions.id%3AI123&mailto=test%40example.com",
            json=mock_list_response,
        )

        client.works.by_institution("I123").list()


class TestAuthorsResource:
    """Test authors resource."""

    def test_get_author(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_author_response: dict[str, Any],
    ) -> None:
        """Test getting a single author."""
        httpx_mock.add_response(
            url="https://api.openalex.org/authors/A123456?mailto=test%40example.com",
            json=mock_author_response,
        )

        author = client.authors.get("A123456")
        assert isinstance(author, Author)
        assert author.display_name == "John P. Perdew"

    def test_get_author_by_orcid(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_author_response: dict[str, Any],
    ) -> None:
        """Test getting author by ORCID."""
        httpx_mock.add_response(
            url="https://api.openalex.org/authors/https://orcid.org/0000-0003-4237-824X?mailto=test%40example.com",
            json=mock_author_response,
        )

        # With full URL
        author = client.authors.by_orcid(
            "https://orcid.org/0000-0003-4237-824X"
        )
        assert author.display_name == "John P. Perdew"

    def test_get_author_by_orcid_short(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_author_response: dict[str, Any],
    ) -> None:
        """Test getting author by ORCID without URL prefix."""
        httpx_mock.add_response(
            url="https://api.openalex.org/authors/https://orcid.org/0000-0003-4237-824X?mailto=test%40example.com",
            json=mock_author_response,
        )

        # Without URL prefix
        author = client.authors.by_orcid("0000-0003-4237-824X")
        assert author.display_name == "John P. Perdew"

    def test_autocomplete_authors(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_autocomplete_response: dict[str, Any],
    ) -> None:
        """Test author autocomplete."""
        httpx_mock.add_response(
            url="https://api.openalex.org/autocomplete/authors?q=perdew&mailto=test%40example.com",
            json=mock_autocomplete_response,
        )

        results = client.authors.autocomplete("perdew")
        assert len(results.results) == 2


class TestInstitutionsResource:
    """Test institutions resource."""

    def test_get_institution(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single institution."""
        mock_response = {
            "id": "https://openalex.org/I123",
            "display_name": "Harvard University",
            "type": "education",
            "country_code": "US",
            "works_count": 100000,
            "cited_by_count": 5000000,
        }

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions/I123?mailto=test%40example.com",
            json=mock_response,
        )

        institution = client.institutions.get("I123")
        assert isinstance(institution, Institution)
        assert institution.display_name == "Harvard University"

    def test_get_institution_by_ror(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting institution by ROR."""
        mock_response = {
            "id": "https://openalex.org/I123",
            "display_name": "Harvard University",
            "ror": "https://ror.org/03vek6s52",
        }

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions/https://ror.org/03vek6s52?mailto=test%40example.com",
            json=mock_response,
        )

        institution = client.institutions.by_ror("03vek6s52")
        assert institution.display_name == "Harvard University"

    def test_filter_institutions_by_country(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test filtering institutions by country."""
        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=country_code%3AUS%7CCA&mailto=test%40example.com",
            json=mock_list_response,
        )

        filter_obj = client.institutions.filter().with_country(["US", "CA"])
        result = client.institutions.list(filter=filter_obj)
        assert result.meta.count == 100

    def test_filter_institutions_by_type(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test filtering institutions by type."""
        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=type%3Aeducation&mailto=test%40example.com",
            json=mock_list_response,
        )

        filter_obj = client.institutions.filter().with_type("education")
        result = client.institutions.list(filter=filter_obj)
        assert result.meta.count == 100


class TestPaginationIntegration:
    """Test pagination with resources."""

    def test_paginate_through_results(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test paginating through multiple pages."""
        # Mock page 1
        page1_response = {
            "meta": {
                "count": 50,
                "db_response_time_ms": 25,
                "page": 1,
                "per_page": 25,
            },
            "results": [
                {
                    "id": f"https://openalex.org/W{i}",
                    "display_name": f"Work {i}",
                }
                for i in range(25)
            ],
        }

        # Mock page 2
        page2_response = {
            "meta": {
                "count": 50,
                "db_response_time_ms": 25,
                "page": 2,
                "per_page": 25,
            },
            "results": [
                {
                    "id": f"https://openalex.org/W{i}",
                    "display_name": f"Work {i}",
                }
                for i in range(25, 50)
            ],
        }

        httpx_mock.add_response(
            url="https://api.openalex.org/works?per-page=25&page=1&mailto=test%40example.com",
            json=page1_response,
        )
        httpx_mock.add_response(
            url="https://api.openalex.org/works?per-page=25&page=2&mailto=test%40example.com",
            json=page2_response,
        )

        paginator = client.works.paginate(per_page=25)
        all_works = list(paginator)

        assert len(all_works) == 50
        assert all_works[0].display_name == "Work 0"
        assert all_works[49].display_name == "Work 49"

    def test_paginate_with_max_results(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Test pagination with max results limit."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?per-page=200&page=1&mailto=test%40example.com",
            json=mock_list_response,
        )

        paginator = client.works.paginate(max_results=10)
        works = list(paginator)

        assert len(works) <= 10

    def test_open_access_shortcut(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Ensure open_access filter clones resource."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=is_oa%3Atrue&mailto=test%40example.com",
            json=mock_list_response,
        )

        result = client.works.open_access().list()
        assert result.meta.count == 100

    @pytest.mark.asyncio
    async def test_async_open_access_shortcut(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Async open_access filter."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=is_oa%3Atrue&mailto=test%40example.com",
            json=mock_list_response,
        )

        resource = await async_client.works.open_access()
        result = await resource.list()
        assert result.meta.count == 100
