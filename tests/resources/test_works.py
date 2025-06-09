"""Tests for Works resource."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, ClassVar

import pytest

from openalex import OpenAlex
from openalex.exceptions import ValidationError
from openalex.models import Work, WorksFilter
from openalex.models import work as legacy
from openalex.resources import WorksResource

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex
    from openalex.resources import AsyncWorksResource


class TestWorksResource(BaseResourceTest[Work]):
    """Test Works resource functionality."""

    resource_name: ClassVar[str] = "works"
    entity_class: ClassVar[type[Work]] = Work
    sample_id: ClassVar[str] = "W2741809807"
    sample_ids: ClassVar[list[str]] = [
        "W2741809807",
        "W2755950973",
        "W2128224298",
    ]

    def get_resource(self, client: OpenAlex) -> WorksResource:
        """Get works resource."""
        return client.works

    def get_async_resource(self, client: AsyncOpenAlex) -> AsyncWorksResource:
        """Get async works resource."""
        return client.works

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample work data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "doi": "https://doi.org/10.1103/physrevlett.77.3865",
            "title": "Generalized Gradient Approximation Made Simple",
            "display_name": "Generalized Gradient Approximation Made Simple",
            "publication_year": 1996,
            "publication_date": "1996-10-28",
            "type": "article",
            "cited_by_count": 50000,
            "is_retracted": False,
            "is_paratext": False,
            "cited_by_api_url": f"https://api.openalex.org/works?filter=cites:{self.sample_id}",
            "abstract_inverted_index": {
                "We": [0],
                "present": [1],
                "a": [2, 8],
                "simple": [3],
                "derivation": [4],
                "of": [5],
                "the": [6],
                "Perdew-Burke-Ernzerhof": [7],
                "generalized": [9],
                "gradient": [10],
                "approximation.": [11],
            },
            "authorships": [
                {
                    "author_position": "first",
                    "author": {
                        "id": "https://openalex.org/A5023888391",
                        "display_name": "John P. Perdew",
                        "orcid": "https://orcid.org/0000-0003-4237-824X",
                    },
                    "institutions": [
                        {
                            "id": "https://openalex.org/I1174212",
                            "display_name": "Tulane University",
                            "ror": "https://ror.org/04v7hvq31",
                            "country_code": "US",
                            "type": "education",
                        }
                    ],
                    "countries": ["US"],
                    "is_corresponding": True,
                },
            ],
            "primary_location": {
                "is_oa": True,
                "landing_page_url": "https://doi.org/10.1103/physrevlett.77.3865",
                "source": {
                    "id": "https://openalex.org/S4210194219",
                    "display_name": "Physical Review Letters",
                    "type": "journal",
                },
            },
            "open_access": {
                "is_oa": True,
                "oa_status": "bronze",
                "oa_url": "https://example.com/paper.pdf",
            },
            "referenced_works": [
                "https://openalex.org/W2000000001",
                "https://openalex.org/W2000000002",
            ],
            "related_works": [
                "https://openalex.org/W2000000003",
                "https://openalex.org/W2000000004",
            ],
        }

    # Work-specific tests
    def test_get_by_doi(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting work by DOI."""
        doi = "10.1103/physrevlett.77.3865"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=test%40example.com",
            json=entity_data,
        )

        work = client.works.by_doi(doi)
        assert work.id == entity_data["id"]

    def test_get_by_pmid(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting work by PubMed ID."""
        pmid = "10062328"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works/pmid:{pmid}?mailto=test%40example.com",
            json=entity_data,
        )

        work = client.works.by_pmid(pmid)
        assert work.id == entity_data["id"]

    def test_get_cited_by_works(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting works that cite a work."""
        cited_response = self.get_list_response(count=382)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=cites%3A{self.sample_id}&mailto=test%40example.com",
            json=cited_response,
        )

        cited_works = client.works.cited_by(self.sample_id)
        result = cited_works.list()
        assert result.meta.count == 382

    def test_get_references(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting references of a work."""
        refs_response = self.get_list_response(count=25)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=cited_by%3A{self.sample_id}&mailto=test%40example.com",
            json=refs_response,
        )

        references = client.works.references(self.sample_id)
        result = references.list()
        assert result.meta.count == 25

    def test_get_related_works(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting related works."""
        related_response = self.get_list_response(count=10)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=related_to%3A{self.sample_id}&mailto=test%40example.com",
            json=related_response,
        )

        related = client.works.related_to(self.sample_id)
        result = related.list()
        assert result.meta.count == 10

    def test_filter_by_author(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering works by author."""
        author_id = "A5023888391"
        author_response = self.get_list_response(count=150)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=authorships.author.id%3A{author_id}&mailto=test%40example.com",
            json=author_response,
        )

        author_works = client.works.by_author(author_id)
        result = author_works.list()
        assert result.meta.count == 150

    def test_filter_by_institution(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering works by institution."""
        institution_id = "I1174212"
        inst_response = self.get_list_response(count=5000)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=authorships.institutions.id%3A{institution_id}&mailto=test%40example.com",
            json=inst_response,
        )

        inst_works = client.works.by_institution(institution_id)
        result = inst_works.list()
        assert result.meta.count == 5000

    def test_filter_by_concept(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering works by concept."""
        concept_id = "C41008148"  # Computer Science
        concept_response = self.get_list_response(count=10000)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter=concepts.id%3A{concept_id}&mailto=test%40example.com",
            json=concept_response,
        )

        concept_works = client.works.by_concept(concept_id)
        result = concept_works.list()
        assert result.meta.count == 10000

    def test_chained_filters(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test chaining multiple filter methods."""
        complex_filter_str = "authorships.author.id:A5023888391,publication_year:2020-2023,type:article,is_oa:true"

        chained_response = self.get_list_response(count=15)
        httpx_mock.add_response(
            url=f"https://api.openalex.org/works?filter={complex_filter_str}&mailto=test%40example.com",
            json=chained_response,
        )

        chained = (
            client.works.by_author("A5023888391")
            .filter(publication_year=[2020, 2021, 2022, 2023])
            .filter(type="article")
            .filter(is_oa=True)
        )
        result = chained.list()
        assert result.meta.count == 15

    def test_title_and_abstract_search(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching in title and abstract."""
        search_response = self.get_list_response(count=200)

        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=title_and_abstract.search%3Amachine+learning&mailto=test%40example.com",
            json=search_response,
        )

        result = client.works.list(
            filter={"title_and_abstract.search": "machine learning"}
        )
        assert result.meta.count == 200

    def test_abstract_reconstruction(self) -> None:
        """Test abstract reconstruction from inverted index."""
        work_data = self.get_sample_entity()
        work = Work(**work_data)

        expected = "We present a simple derivation of the Perdew-Burke-Ernzerhof a generalized gradient approximation."
        assert work.abstract == expected

    def test_sort_by_publication_date(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sorting by publication date."""
        sorted_response = self.get_list_response()

        httpx_mock.add_response(
            url="https://api.openalex.org/works?sort=publication_date%3Adesc&mailto=test%40example.com",
            json=sorted_response,
        )

        result = client.works.list(sort="publication_date:desc")
        assert result.meta.count == 100

    def test_get_n_grams(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting n-grams for a work (if API supports it)."""
        # Note: This is a placeholder - adjust based on actual API
        ngram_response = {
            "meta": {"count": 50},
            "ngrams": [
                {"ngram": "machine learning", "count": 5},
                {"ngram": "gradient approximation", "count": 3},
            ],
        }

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works/{self.sample_id}/ngrams?mailto=test%40example.com",
            json=ngram_response,
        )

        # Assuming n-grams method exists
        # ngrams = client.works.get_ngrams(self.sample_id)
        # assert len(ngrams) == 2

    def test_premium_filters(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test premium filters (requires API key)."""
        # Test from_created_date filter
        premium_client = OpenAlex(email="test@example.com", api_key="test-key")

        premium_response = self.get_list_response(count=50)
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=from_created_date%3A2024-01-01&mailto=test%40example.com&api_key=test-key",
            json=premium_response,
        )

        result = premium_client.works.list(
            filter={"from_created_date": "2024-01-01"}
        )
        assert result.meta.count == 50
        premium_client.close()

    def test_malformed_response_handling(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test handling of malformed API responses."""
        # Missing required fields
        malformed_data = {
            "id": f"https://openalex.org/{self.sample_id}",
            # Missing display_name and other required fields
            "title": None,
            "publication_year": "invalid",  # Should be int
        }

        httpx_mock.add_response(
            url=f"https://api.openalex.org/works/{self.sample_id}?mailto=test%40example.com",
            json=malformed_data,
        )

        # Should handle gracefully with model_construct fallback
        work = client.works.get(self.sample_id)
        assert work.id == malformed_data["id"]

    def test_filter_range_normalization(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=cited_by_count%3A1-4&mailto=test%40example.com",
            json=mock_list_response,
        )

        resource = client.works.filter(cited_by_count=[1, 2, 3, 4])
        assert isinstance(resource, WorksResource)
        result = resource.list()
        assert result.meta.count == 100

    def test_filter_non_contiguous_range(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """List with non-contiguous int list should not collapse to range."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=cited_by_count%3A1%7C3%7C5&mailto=test%40example.com",
            json=mock_list_response,
        )

        resource = client.works.filter(cited_by_count=[1, 3, 5])
        result = resource.list()
        assert result.meta.count == 100

    def test_open_access_false(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """WorksResource open_access with explicit False."""
        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=is_oa%3Afalse&mailto=test%40example.com",
            json=mock_list_response,
        )

        result = client.works.open_access(False).list()
        assert result.meta.count == 100

    def test_clone_with_default_filter(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        default = WorksFilter().with_open_access(is_oa=True)
        resource = WorksResource(client, default_filter=default)

        httpx_mock.add_response(
            url="https://api.openalex.org/works?filter=is_oa%3Atrue%2Cauthorships.author.id%3AA123&mailto=test%40example.com",
            json=mock_list_response,
        )

        result = resource.by_author("A123").list()
        assert result.meta.count == 100


def test_legacy_basefilter_validation() -> None:
    with pytest.raises(ValueError, match="string or dictionary"):
        legacy.BaseFilter(filter=123)
    with pytest.raises(ValueError, match="list of strings"):
        legacy.BaseFilter(select=123)


def test_legacy_basefilter_to_params() -> None:
    bf = legacy.BaseFilter(
        filter={"is_oa": True, "created": date(2024, 1, 1)},
        select=["id", "title"],
        per_page=50,
    )
    params = bf.to_params()
    assert params["filter"] == "is_oa:true,created:2024-01-01"
    assert params["select"] == "id,title"
    assert params["per-page"] == 50


def test_legacy_worksfilter_methods() -> None:
    wf = (
        legacy.WorksFilter()
        .with_publication_year(2023)
        .with_type("article")
        .with_open_access(True)
    )
    params = wf.to_params()
    filter_str = params["filter"]
    assert "publication_year:2023" in filter_str
    assert "type:article" in filter_str
    assert "is_oa:true" in filter_str

def test_filter_returns_filter_instance(client: OpenAlex) -> None:
    resource = client.works.filter(page=2)
    assert isinstance(resource, WorksFilter)
    assert resource.page == 2


def test_apply_filter_params(client: OpenAlex) -> None:
    res = WorksResource(client)
    params = res._apply_filter_params({}, {"is_oa": True, "page": 2})
    assert params["page"] == 2
    assert params["filter"] == "is_oa:true"

    wf = WorksFilter().with_open_access()
    params2 = res._apply_filter_params({}, wf)
    assert params2["filter"] == "is_oa:true"

def test_filter_no_params_returns_filter(client: OpenAlex) -> None:
    wf = client.works.filter()
    assert isinstance(wf, WorksFilter)
    assert wf.filter is None


def test_clone_with_merges_default_filter(client: OpenAlex) -> None:
    default = WorksFilter(filter="is_oa:true")
    resource = WorksResource(client, default_filter=default)
    new_res = resource.by_author("A123")
    assert isinstance(new_res, WorksResource)
    assert new_res._default_filter.filter["raw"] == "is_oa:true"
    assert new_res._default_filter.filter["authorships.author.id"] == "A123"

@pytest.mark.asyncio
async def test_async_by_doi(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    doi = "10.1103/physrevlett.77.3865"
    entity_data = TestWorksResource().get_sample_entity()
    httpx_mock.add_response(
        url=f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=test%40example.com",
        json=entity_data,
    )
    work = await async_client.works.by_doi(doi)
    assert work.id == entity_data["id"]

@pytest.mark.asyncio
async def test_async_by_pmid(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    pmid = "10062328"
    entity_data = TestWorksResource().get_sample_entity()
    httpx_mock.add_response(
        url=f"https://api.openalex.org/works/pmid:{pmid}?mailto=test%40example.com",
        json=entity_data,
    )
    work = await async_client.works.by_pmid(pmid)
    assert work.id == entity_data["id"]

@pytest.mark.asyncio
async def test_async_open_access_list(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    list_response = TestWorksResource().get_list_response(count=2)
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=is_oa%3Atrue&mailto=test%40example.com",
        json=list_response,
    )
    resource = await async_client.works.open_access()
    result = await resource.list()
    assert result.meta.count == 2


@pytest.mark.asyncio
async def test_async_work_helpers(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    data = TestWorksResource().get_list_response()
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=cites%3AW2741809807&mailto=test%40example.com",
        json=data,
    )
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=cited_by%3AW2741809807&mailto=test%40example.com",
        json=data,
    )
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=authorships.author.id%3AA123&mailto=test%40example.com",
        json=data,
    )
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=concepts.id%3AC41008148&mailto=test%40example.com",
        json=data,
    )
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=authorships.institutions.id%3AI1174212&mailto=test%40example.com",
        json=data,
    )
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=related_to%3AW2741809807&mailto=test%40example.com",
        json=data,
    )

    assert (await (await async_client.works.cited_by("W2741809807")).list()).meta.count == 100
    assert (await (await async_client.works.references("W2741809807")).list()).meta.count == 100
    assert (await (await async_client.works.by_author("A123")).list()).meta.count == 100
    assert (await (await async_client.works.by_concept("C41008148")).list()).meta.count == 100
    assert (await (await async_client.works.by_institution("I1174212")).list()).meta.count == 100
    assert (await (await async_client.works.related_to("W2741809807")).list()).meta.count == 100


@pytest.mark.asyncio
async def test_async_search_with_default_filter(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    data = TestWorksResource().get_list_response(count=1)
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=is_oa%3Atrue&search=test&mailto=test%40example.com",
        json=data,
    )
    result = await (await async_client.works.open_access()).search("test")
    assert result.meta.count == 1

def test_parse_list_response_error(client: OpenAlex) -> None:
    resource = WorksResource(client)
    bad_data = {"meta": {"foo": "bar"}, "results": [{"bad": "data"}]}
    with pytest.raises(ValidationError):
        resource._parse_list_response(bad_data)

@pytest.mark.asyncio
async def test_async_apply_filter_params(async_client: AsyncOpenAlex, httpx_mock: HTTPXMock) -> None:
    data = TestWorksResource().get_list_response(count=1)
    httpx_mock.add_response(
        url="https://api.openalex.org/works?filter=is_oa%3Atrue&page=2&mailto=test%40example.com",
        json=data,
    )
    result = await async_client.works.list(filter={"is_oa": True, "page": 2})
    assert result.meta.count == 1


@pytest.mark.asyncio
async def test_async_parse_list_response_error(async_client: AsyncOpenAlex) -> None:
    resource = async_client.works
    bad_data = {"meta": {"foo": "bar"}, "results": [{"bad": "data"}]}
    with pytest.raises(ValidationError):
        resource._parse_list_response(bad_data)

@pytest.mark.asyncio
async def test_async_filter_builder(async_client: AsyncOpenAlex) -> None:
    filt = async_client.works.filter(page=3)
    assert isinstance(filt, WorksFilter)
    assert filt.page == 3

