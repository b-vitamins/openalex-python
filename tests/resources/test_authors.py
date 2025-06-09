"""Tests for Authors resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import pytest
from openalex.models import Author, AuthorsFilter
from openalex.resources import AuthorsResource, AsyncAuthorsResource

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncAuthorsResource, AuthorsResource


class TestAuthorsResource(BaseResourceTest[Author]):
    """Test Authors resource functionality."""

    resource_name: ClassVar[str] = "authors"
    entity_class: ClassVar[type[Author]] = Author
    sample_id: ClassVar[str] = "A5023888391"
    sample_ids: ClassVar[list[str]] = [
        "A5023888391",
        "A5014077037",
        "A5030593938",
    ]

    def get_resource(self, client: OpenAlex) -> AuthorsResource:
        """Get authors resource."""
        return client.authors

    def get_async_resource(self, client: AsyncOpenAlex) -> AsyncAuthorsResource:
        """Get async authors resource."""
        return client.authors

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample author data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "orcid": "https://orcid.org/0000-0003-4237-824X",
            "display_name": "John P. Perdew",
            "display_name_alternatives": [
                "J. P. Perdew",
                "John Perdew",
                "J Perdew",
            ],
            "works_count": 500,
            "cited_by_count": 100000,
            "most_cited_work": "https://openalex.org/W2741809807",
            "summary_stats": {
                "2yr_mean_citedness": 5.2,
                "h_index": 120,
                "i10_index": 450,
            },
            "affiliations": [
                {
                    "institution": {
                        "id": "https://openalex.org/I1174212",
                        "display_name": "Tulane University",
                        "ror": "https://ror.org/04v7hvq31",
                        "country_code": "US",
                        "type": "education",
                    },
                    "years": [2018, 2019, 2020, 2021, 2022, 2023],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I1302918504",
                        "display_name": "Temple University",
                        "ror": "https://ror.org/00jge9k46",
                        "country_code": "US",
                        "type": "education",
                    },
                    "years": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017],
                },
            ],
            "counts_by_year": [
                {"year": 2023, "works_count": 10, "cited_by_count": 5000},
                {"year": 2022, "works_count": 8, "cited_by_count": 4800},
                {"year": 2021, "works_count": 12, "cited_by_count": 4500},
            ],
            "x_concepts": [
                {
                    "id": "https://openalex.org/C121332964",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 98.5,
                },
                {
                    "id": "https://openalex.org/C33923547",
                    "display_name": "Theoretical physics",
                    "level": 1,
                    "score": 95.2,
                },
            ],
            "works_api_url": f"https://api.openalex.org/works?filter=authorships.author.id:{self.sample_id}",
            "created_date": "2023-01-01",
            "updated_date": "2024-01-01",
        }

    # Author-specific tests
    def test_get_by_orcid(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting author by ORCID."""
        orcid = "0000-0003-4237-824X"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors/https://orcid.org/{orcid}?mailto=test%40example.com",
            json=entity_data,
        )

        author = client.authors.by_orcid(orcid)
        assert author.id == entity_data["id"]
        assert str(author.orcid) == f"https://orcid.org/{orcid}"

    def test_get_by_orcid_with_prefix(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting author by ORCID with full URL."""
        orcid_url = "https://orcid.org/0000-0003-4237-824X"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors/{orcid_url}?mailto=test%40example.com",
            json=entity_data,
        )

        author = client.authors.by_orcid(orcid_url)
        assert author.id == entity_data["id"]

    def test_get_by_mag_id(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting author by Microsoft Academic Graph ID."""
        mag_id = "2133337193"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors/mag:{mag_id}?mailto=test%40example.com",
            json=entity_data,
        )

        author = client.authors.by_mag(mag_id)
        assert author.id == entity_data["id"]

    def test_filter_by_institution(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering authors by institution."""
        institution_id = "I1174212"
        inst_response = self.get_list_response(count=250)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors?filter=affiliations.institution.id%3A{institution_id}&mailto=test%40example.com",
            json=inst_response,
        )

        inst_authors = client.authors.by_institution(institution_id)
        result = inst_authors.list()
        assert result.meta.count == 250

    def test_filter_by_works_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering authors by works count."""
        prolific_response = self.get_list_response(count=1000)

        httpx_mock.add_response(
            url="https://api.openalex.org/authors?filter=works_count%3A%3E100&mailto=test%40example.com",
            json=prolific_response,
        )

        prolific_authors = client.authors.list(filter={"works_count": ">100"})
        assert prolific_authors.meta.count == 1000

    def test_filter_by_h_index(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering authors by h-index."""
        high_impact_response = self.get_list_response(count=500)

        httpx_mock.add_response(
            url="https://api.openalex.org/authors?filter=summary_stats.h_index%3A%3E50&mailto=test%40example.com",
            json=high_impact_response,
        )

        high_impact = client.authors.list(
            filter={"summary_stats.h_index": ">50"}
        )
        assert high_impact.meta.count == 500

    def test_search_with_affiliations(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching authors with affiliation information."""
        search_response = self.get_list_response(count=25)
        complex_filter = (
            "search=physics&filter=affiliations.institution.country_code:US"
        )

        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors?{complex_filter}&mailto=test%40example.com",
            json=search_response,
        )

        result = client.authors.search(
            "physics", filter={"affiliations.institution.country_code": "US"}
        )
        assert result.meta.count == 25

    def test_author_metrics_computation(self) -> None:
        """Test author metric computations."""
        author_data = self.get_sample_entity()
        author = Author(**author_data)

        # Test computed properties
        assert author.h_index == 120
        assert author.i10_index == 450
        assert author.two_year_mean_citedness == 5.2

        # Test yearly metrics
        assert author.works_in_year(2023) == 10
        assert author.citations_in_year(2023) == 5000

        # Test active years
        active_years = author.active_years()
        assert 2023 in active_years
        assert 2022 in active_years

        # Test institution extraction
        institutions = author.institution_names()
        assert "Tulane University" in institutions
        assert "Temple University" in institutions

    def test_author_name_alternatives(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test handling of author name alternatives."""
        author_data = self.get_sample_entity()
        author = Author(**author_data)

        assert "J. P. Perdew" in author.display_name_alternatives
        assert "John Perdew" in author.display_name_alternatives
        assert len(author.display_name_alternatives) == 3

    def test_sort_by_citations(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sorting authors by citation count."""
        sorted_response = self.get_list_response()

        httpx_mock.add_response(
            url="https://api.openalex.org/authors?sort=cited_by_count%3Adesc&mailto=test%40example.com",
            json=sorted_response,
        )

        result = client.authors.list(sort="cited_by_count:desc")
        assert result.meta.count == 100

    def test_coauthor_network(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting coauthors of an author."""
        # This would require a complex filter to find all coauthors
        coauthor_response = self.get_list_response(count=150)

        # Simulate finding coauthors through shared works
        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors?filter=works.authorships.author.id%3A{self.sample_id}&mailto=test%40example.com",
            json=coauthor_response,
        )

        # Note: Actual implementation would need more sophisticated filtering
        result = client.authors.list(
            filter={"works.authorships.author.id": self.sample_id}
        )
        assert result.meta.count == 150

    def test_recent_authors(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering authors by recent activity."""
        recent_response = self.get_list_response(count=1000)

        httpx_mock.add_response(
            url="https://api.openalex.org/authors?filter=works_count%3A%3E0%2Clast_known_affiliation.updated_date%3A%3E2023-01-01&mailto=test%40example.com",
            json=recent_response,
        )

        result = client.authors.list(
            filter={
                "works_count": ">0",
                "last_known_affiliation.updated_date": ">2023-01-01",
            }
        )
        assert result.meta.count == 1000

    @pytest.mark.asyncio
    async def test_async_by_mag(
        self, async_client: AsyncOpenAlex, httpx_mock: HTTPXMock
    ) -> None:
        mag_id = "2133337193"
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors/mag:{mag_id}?mailto=test%40example.com",
            json=entity_data,
        )
        author = await async_client.authors.by_mag(mag_id)
        assert author.id == entity_data["id"]

    @pytest.mark.asyncio
    async def test_async_by_orcid(
        self, async_client: AsyncOpenAlex, httpx_mock: HTTPXMock
    ) -> None:
        orcid = "0000-0003-4237-824X"
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/authors/https://orcid.org/{orcid}?mailto=test%40example.com",
            json=entity_data,
        )
        author = await async_client.authors.by_orcid(orcid)
        assert author.id == entity_data["id"]

    def test_clone_with_raw_filter(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        """Ensure _clone_with handles string filters."""
        default = AuthorsFilter(filter="is_oa:true")
        resource = AuthorsResource(client, default_filter=default)
        httpx_mock.add_response(
            url="https://api.openalex.org/authors?filter=raw%3Ais_oa%3Atrue%2Caffiliations.institution.id%3AI123&mailto=test%40example.com",
            json=mock_list_response,
        )
        result = resource.by_institution("I123").list()
        assert result.meta.count == 100

    @pytest.mark.asyncio
    async def test_async_clone_with_raw_filter(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
        mock_list_response: dict[str, Any],
    ) -> None:
        default = AuthorsFilter(filter="is_oa:true")
        resource = AsyncAuthorsResource(async_client, default_filter=default)
        httpx_mock.add_response(
            url="https://api.openalex.org/authors?filter=raw%3Ais_oa%3Atrue%2Caffiliations.institution.id%3AI123&mailto=test%40example.com",
            json=mock_list_response,
        )
        new_res = await resource.by_institution("I123")
        result = await new_res.list()
        assert result.meta.count == 100
