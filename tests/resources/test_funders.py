"""Tests for Funders resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from openalex.models import Funder

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncFundersResource, FundersResource


class TestFundersResource(BaseResourceTest[Funder]):
    """Test Funders resource functionality."""

    resource_name: ClassVar[str] = "funders"
    entity_class: ClassVar[type[Funder]] = Funder
    sample_id: ClassVar[str] = "F4320306076"
    sample_ids: ClassVar[list[str]] = [
        "F4320306076",
        "F4320332161",
        "F4320321001",
    ]

    def get_resource(self, client: OpenAlex) -> FundersResource:
        """Get funders resource."""
        return client.funders

    def get_async_resource(self, client: AsyncOpenAlex) -> AsyncFundersResource:
        """Get async funders resource."""
        return client.funders

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample funder data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "display_name": "National Science Foundation",
            "ror": "https://ror.org/021nxhr62",
            "wikidata": "https://www.wikidata.org/wiki/Q270150",
            "country_code": "US",
            "type": "government",
            "description": "The National Science Foundation (NSF) is an independent agency...",
            "homepage_url": "https://www.nsf.gov",
            "image_url": "https://example.com/nsf-logo.png",
            "image_thumbnail_url": "https://example.com/nsf-logo-thumb.png",
            "grants_count": 100000,
            "works_count": 500000,
            "cited_by_count": 10000000,
            "summary_stats": {
                "2yr_mean_citedness": 6.5,
                "h_index": 400,
                "i10_index": 300000,
            },
            "alternate_titles": [
                "NSF",
                "US National Science Foundation",
            ],
            "counts_by_year": [
                {"year": 2023, "works_count": 15000, "cited_by_count": 500000},
                {"year": 2022, "works_count": 14000, "cited_by_count": 480000},
            ],
            "roles": [
                {
                    "role": "funder",
                    "id": "https://openalex.org/F4320306076",
                    "works_count": 500000,
                },
                {
                    "role": "institution",
                    "id": "https://openalex.org/I1338517721",
                    "works_count": 2000,
                },
            ],
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Funder-specific tests
    def test_get_by_ror(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting funder by ROR ID."""
        ror = "021nxhr62"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/funders/https://ror.org/{ror}?mailto=test%40example.com",
            json=entity_data,
        )

        funder = client.funders.by_ror(ror)
        assert funder.id == entity_data["id"]
        assert str(funder.ror) == f"https://ror.org/{ror}"

    def test_filter_by_type(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering funders by type."""
        government_response = self.get_list_response(count=200)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=type%3Agovernment&mailto=test%40example.com",
            json=government_response,
        )

        government_funders = client.funders.list(filter={"type": "government"})
        assert government_funders.meta.count == 200

    def test_filter_by_country(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering funders by country."""
        us_response = self.get_list_response(count=150)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=country_code%3AUS&mailto=test%40example.com",
            json=us_response,
        )

        us_funders = client.funders.list(filter={"country_code": "US"})
        assert us_funders.meta.count == 150

    def test_funder_metrics(self) -> None:
        """Test funder metric calculations."""
        funder_data = self.get_sample_entity()
        funder = Funder(**funder_data)

        # Test funding per work calculation
        assert funder.grants_count == 100000
        assert funder.works_count == 500000
        assert funder.funding_per_work == 0.2

        # Test government funder detection
        assert funder.is_government_funder() is True

    def test_private_funders(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for private funders."""
        private_response = self.get_list_response(count=500)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=type%3Anonprofit%7Cother&mailto=test%40example.com",
            json=private_response,
        )

        private_funders = client.funders.list(
            filter={"type": ["nonprofit", "other"]}
        )
        assert private_funders.meta.count == 500

    def test_filter_by_grants_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering funders by grants count."""
        major_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=grants_count%3A%3E10000&mailto=test%40example.com",
            json=major_response,
        )

        major_funders = client.funders.list(filter={"grants_count": ">10000"})
        assert major_funders.meta.count == 50

    def test_funder_roles(self) -> None:
        """Test funder role functionality."""
        funder_data = self.get_sample_entity()
        funder = Funder(**funder_data)

        assert len(funder.roles) == 2
        funder_role = next(r for r in funder.roles if r.role == "funder")
        assert funder_role.works_count == 500000

        institution_role = next(
            r for r in funder.roles if r.role == "institution"
        )
        assert institution_role.works_count == 2000

    def test_search_funders_by_description(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching funders by description."""
        search_response = self.get_list_response(count=25)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=description.search%3Ahealth+research&mailto=test%40example.com",
            json=search_response,
        )

        health_funders = client.funders.list(
            filter={"description.search": "health research"}
        )
        assert health_funders.meta.count == 25

    def test_international_funders(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for international funders."""
        # Funders from multiple countries
        international_response = self.get_list_response(count=75)

        httpx_mock.add_response(
            url="https://api.openalex.org/funders?filter=country_code%3AGB%7CDE%7CFR%7CJP&mailto=test%40example.com",
            json=international_response,
        )

        international_funders = client.funders.list(
            filter={"country_code": ["GB", "DE", "FR", "JP"]}
        )
        assert international_funders.meta.count == 75

    def test_zero_works_funders(self) -> None:
        """Test funders with no associated works."""
        funder_data = self.get_sample_entity()
        funder_data["works_count"] = 0
        funder_data["grants_count"] = 100

        funder = Funder(**funder_data)
        assert funder.funding_per_work is None  # Division by zero protection
