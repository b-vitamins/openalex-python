"""Tests for Publishers resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from openalex.models import Publisher

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncPublishersResource, PublishersResource


class TestPublishersResource(BaseResourceTest[Publisher]):
    """Test Publishers resource functionality."""

    resource_name: ClassVar[str] = "publishers"
    entity_class: ClassVar[type[Publisher]] = Publisher
    sample_id: ClassVar[str] = "P4310320990"
    sample_ids: ClassVar[list[str]] = [
        "P4310320990",
        "P4310319965",
        "P4310319909",
    ]

    def get_resource(self, client: OpenAlex) -> PublishersResource:
        """Get publishers resource."""
        return client.publishers

    def get_async_resource(
        self, client: AsyncOpenAlex
    ) -> AsyncPublishersResource:
        """Get async publishers resource."""
        return client.publishers

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample publisher data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "display_name": "Elsevier BV",
            "alternate_titles": [
                "Elsevier",
                "Elsevier Science",
                "Reed Elsevier",
            ],
            "country_codes": ["NL", "GB", "US"],
            "hierarchy_level": 0,
            "parent_publisher": None,
            "works_count": 20000000,
            "cited_by_count": 400000000,
            "summary_stats": {
                "2yr_mean_citedness": 4.2,
                "h_index": 800,
                "i10_index": 15000000,
            },
            "image_url": "https://example.com/elsevier-logo.png",
            "image_thumbnail_url": "https://example.com/elsevier-logo-thumb.png",
            "homepage_url": "https://www.elsevier.com",
            "wikidata": "https://www.wikidata.org/wiki/Q746413",
            "counts_by_year": [
                {
                    "year": 2023,
                    "works_count": 500000,
                    "cited_by_count": 20000000,
                },
                {
                    "year": 2022,
                    "works_count": 480000,
                    "cited_by_count": 19000000,
                },
            ],
            "roles": [
                {
                    "role": "publisher",
                    "id": "https://openalex.org/P4310320990",
                    "works_count": 20000000,
                },
                {
                    "role": "institution",
                    "id": "https://openalex.org/I4210145622",
                    "works_count": 5000,
                },
            ],
            "sources_api_url": f"https://api.openalex.org/sources?filter=host_organization.id:{self.sample_id}",
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Publisher-specific tests
    def test_publisher_hierarchy(self) -> None:
        """Test publisher hierarchy relationships."""
        parent_data = self.get_sample_entity()
        publisher = Publisher(**parent_data)

        assert publisher.is_parent_publisher is True
        assert publisher.has_parent() is False
        assert publisher.parent_publisher is None
        assert publisher.hierarchy_level == 0

    def test_filter_by_parent_publisher(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering publishers by parent."""
        child_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/publishers?filter=parent_publisher%3A{self.sample_id}&mailto=test%40example.com",
            json=child_response,
        )

        child_publishers = client.publishers.list(
            filter={"parent_publisher": self.sample_id}
        )
        assert child_publishers.meta.count == 50

    def test_filter_by_country(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering publishers by country."""
        us_response = self.get_list_response(count=1000)

        httpx_mock.add_response(
            url="https://api.openalex.org/publishers?filter=country_codes%3AUS&mailto=test%40example.com",
            json=us_response,
        )

        us_publishers = client.publishers.list(filter={"country_codes": "US"})
        assert us_publishers.meta.count == 1000

    def test_publisher_roles(self) -> None:
        """Test publisher role functionality."""
        publisher_data = self.get_sample_entity()
        publisher = Publisher(**publisher_data)

        assert len(publisher.roles) == 2
        publisher_role = next(
            r for r in publisher.roles if r.role == "publisher"
        )
        assert publisher_role.works_count == 20000000

        institution_role = next(
            r for r in publisher.roles if r.role == "institution"
        )
        assert institution_role.works_count == 5000

    def test_publisher_countries(self) -> None:
        """Test publisher country properties."""
        publisher_data = self.get_sample_entity()
        publisher = Publisher(**publisher_data)

        countries = publisher.countries
        assert "NL" in countries
        assert "GB" in countries
        assert "US" in countries
        assert len(countries) == 3

    def test_top_level_publishers(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for top-level publishers."""
        parent_response = self.get_list_response(count=200)

        httpx_mock.add_response(
            url="https://api.openalex.org/publishers?filter=hierarchy_level%3A0&mailto=test%40example.com",
            json=parent_response,
        )

        parent_publishers = client.publishers.list(
            filter={"hierarchy_level": 0}
        )
        assert parent_publishers.meta.count == 200

    def test_publisher_with_sources(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting sources for a publisher."""
        sources_response = self.get_list_response(count=1500)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/sources?filter=host_organization.id%3A{self.sample_id}&mailto=test%40example.com",
            json=sources_response,
        )

        # This would typically be accessed via sources API
        sources = client.sources.list(
            filter={"host_organization.id": self.sample_id}
        )
        assert sources.meta.count == 1500

    def test_sort_by_works_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sorting publishers by works count."""
        sorted_response = self.get_list_response()

        httpx_mock.add_response(
            url="https://api.openalex.org/publishers?sort=works_count%3Adesc&mailto=test%40example.com",
            json=sorted_response,
        )

        result = client.publishers.list(sort="works_count:desc")
        assert result.meta.count == 100

    def test_academic_publishers(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for academic publishers."""
        # This might use a combination of filters
        academic_response = self.get_list_response(count=500)

        httpx_mock.add_response(
            url="https://api.openalex.org/publishers?filter=works_count%3A%3E10000%2Csummary_stats.h_index%3A%3E50&mailto=test%40example.com",
            json=academic_response,
        )

        academic_publishers = client.publishers.list(
            filter={
                "works_count": ">10000",
                "summary_stats.h_index": ">50",
            }
        )
        assert academic_publishers.meta.count == 500
