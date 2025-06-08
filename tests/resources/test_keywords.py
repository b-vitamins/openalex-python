"""Tests for Keywords resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from openalex.models import Keyword

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncKeywordsResource, KeywordsResource


class TestKeywordsResource(BaseResourceTest[Keyword]):
    """Test Keywords resource functionality."""

    resource_name: ClassVar[str] = "keywords"
    entity_class: ClassVar[type[Keyword]] = Keyword
    sample_id: ClassVar[str] = "K123456789"
    sample_ids: ClassVar[list[str]] = ["K123456789", "K987654321", "K555555555"]

    def get_resource(self, client: OpenAlex) -> KeywordsResource:
        """Get keywords resource."""
        return client.keywords

    def get_async_resource(
        self, client: AsyncOpenAlex
    ) -> AsyncKeywordsResource:
        """Get async keywords resource."""
        return client.keywords

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample keyword data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "display_name": "machine learning",
            "works_count": 100000,
            "cited_by_count": 5000000,
            "counts_by_year": [
                {"year": 2023, "works_count": 10000, "cited_by_count": 500000},
                {"year": 2022, "works_count": 9000, "cited_by_count": 450000},
            ],
            "works_api_url": f"https://api.openalex.org/works?filter=keywords.id:{self.sample_id}",
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Keyword-specific tests
    def test_keyword_popularity(self) -> None:
        """Test keyword popularity metrics."""
        keyword_data = self.get_sample_entity()
        keyword = Keyword(**keyword_data)

        # Calculate average citations per work
        avg_citations = keyword.average_citations_per_work
        assert avg_citations == 50.0  # 5M citations / 100K works

        # Test popularity threshold
        assert keyword.is_popular(threshold=40) is True
        assert keyword.is_popular(threshold=60) is False

    def test_filter_by_works_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering keywords by works count."""
        popular_response = self.get_list_response(count=1000)

        httpx_mock.add_response(
            url="https://api.openalex.org/keywords?filter=works_count%3A%3E10000&mailto=test%40example.com",
            json=popular_response,
        )

        popular_keywords = client.keywords.list(
            filter={"works_count": ">10000"}
        )
        assert popular_keywords.meta.count == 1000

    def test_search_keywords(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching keywords."""
        search_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url="https://api.openalex.org/keywords?search=learning&mailto=test%40example.com",
            json=search_response,
        )

        learning_keywords = client.keywords.search("learning")
        assert learning_keywords.meta.count == 50

    def test_trending_keywords(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test finding trending keywords."""
        # Keywords with high recent growth
        trending_response = self.get_list_response(count=100)

        # This would need a complex filter based on counts_by_year growth
        httpx_mock.add_response(
            url="https://api.openalex.org/keywords?filter=works_count%3A%3E1000&sort=works_count%3Adesc&mailto=test%40example.com",
            json=trending_response,
        )

        # Simplified version - in reality would need growth calculation
        trending = client.keywords.list(
            filter={"works_count": ">1000"},
            sort="works_count:desc",
        )
        assert trending.meta.count == 100

    def test_keyword_yearly_growth(self) -> None:
        """Test keyword yearly growth calculation."""
        keyword_data = self.get_sample_entity()
        keyword = Keyword(**keyword_data)

        # Calculate growth rate
        if len(keyword.counts_by_year) >= 2:
            recent = keyword.counts_by_year[0].works_count
            previous = keyword.counts_by_year[1].works_count
            growth_rate = (recent - previous) / previous * 100
            assert growth_rate > 0  # Positive growth

    def test_compound_keywords(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test handling of compound keywords."""
        compound_data = self.get_sample_entity()
        compound_data["display_name"] = "natural language processing"

        keyword = Keyword(**compound_data)
        # Test that multi-word keywords are handled correctly
        assert " " in keyword.display_name
        assert len(keyword.display_name.split()) == 3

    def test_case_insensitive_search(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test case-insensitive keyword search."""
        # API should handle case insensitivity
        search_response = self.get_list_response(count=10)

        httpx_mock.add_response(
            url="https://api.openalex.org/keywords?search=MACHINE+LEARNING&mailto=test%40example.com",
            json=search_response,
        )

        results = client.keywords.search("MACHINE LEARNING")
        assert results.meta.count == 10

    def test_zero_works_keywords(self) -> None:
        """Test keywords with no associated works."""
        keyword_data = self.get_sample_entity()
        keyword_data["works_count"] = 0
        keyword_data["cited_by_count"] = 0

        keyword = Keyword(**keyword_data)
        assert keyword.average_citations_per_work is None
        assert keyword.is_popular(threshold=1) is False

    def test_sort_by_cited_by_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sorting keywords by citation count."""
        sorted_response = self.get_list_response()

        httpx_mock.add_response(
            url="https://api.openalex.org/keywords?sort=cited_by_count%3Adesc&mailto=test%40example.com",
            json=sorted_response,
        )

        result = client.keywords.list(sort="cited_by_count:desc")
        assert result.meta.count == 100
