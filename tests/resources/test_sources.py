"""Tests for Sources resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import pytest

from openalex.models import Source, SourceType

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import AsyncSourcesResource, SourcesResource


class TestSourcesResource(BaseResourceTest[Source]):
    """Test Sources resource functionality."""

    resource_name: ClassVar[str] = "sources"
    entity_class: ClassVar[type[Source]] = Source
    sample_id: ClassVar[str] = "S4210194219"
    sample_ids: ClassVar[list[str]] = [
        "S4210194219",
        "S2764455111",
        "S4306525036",
    ]

    def get_resource(self, client: OpenAlex) -> SourcesResource:
        """Get sources resource."""
        return client.sources

    def get_async_resource(self, client: AsyncOpenAlex) -> AsyncSourcesResource:
        """Get async sources resource."""
        return client.sources

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample source data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "issn_l": "0031-9007",
            "issn": ["0031-9007", "1079-7114"],
            "display_name": "Physical Review Letters",
            "host_organization": "https://openalex.org/P4310320261",
            "host_organization_name": "American Physical Society",
            "host_organization_lineage": ["https://openalex.org/P4310320261"],
            "works_count": 150000,
            "cited_by_count": 5000000,
            "summary_stats": {
                "2yr_mean_citedness": 8.5,
                "h_index": 450,
                "i10_index": 140000,
            },
            "is_oa": False,
            "is_in_doaj": False,
            "is_core": True,
            "type": "journal",
            "homepage_url": "https://journals.aps.org/prl/",
            "apc_prices": [
                {"price": 3500, "currency": "USD"},
                {"price": 3200, "currency": "EUR"},
            ],
            "apc_usd": 3500,
            "country_code": "US",
            "societies": [
                {
                    "id": "https://openalex.org/S4210320261",
                    "display_name": "American Physical Society",
                    "url": "https://www.aps.org",
                    "organization": "American Physical Society",
                }
            ],
            "alternate_titles": ["Phys. Rev. Lett.", "PRL"],
            "abbreviated_title": "Phys Rev Lett",
            "counts_by_year": [
                {"year": 2023, "works_count": 3000, "cited_by_count": 250000},
                {"year": 2022, "works_count": 2900, "cited_by_count": 240000},
            ],
            "works_api_url": f"https://api.openalex.org/works?filter=primary_location.source.id:{self.sample_id}",
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Source-specific tests
    def test_get_by_issn(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting source by ISSN."""
        issn = "0031-9007"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/sources/issn:{issn}?mailto=test%40example.com",
            json=entity_data,
        )

        source = client.sources.by_issn(issn)
        assert source.id == entity_data["id"]
        assert source.issn_l == issn

    def test_filter_by_type(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering sources by type."""
        journal_response = self.get_list_response(count=5000)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=type%3Ajournal&mailto=test%40example.com",
            json=journal_response,
        )

        journals = client.sources.list(filter={"type": "journal"})
        assert journals.meta.count == 5000

    def test_filter_repositories(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for repository sources."""
        repo_response = self.get_list_response(count=500)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=type%3Arepository&mailto=test%40example.com",
            json=repo_response,
        )

        repositories = client.sources.list(filter={"type": "repository"})
        assert repositories.meta.count == 500

    def test_filter_by_publisher(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering sources by publisher."""
        publisher_id = "P4310320261"
        publisher_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url=f"https://api.openalex.org/sources?filter=host_organization%3A{publisher_id}&mailto=test%40example.com",
            json=publisher_response,
        )

        publisher_sources = client.sources.list(
            filter={"host_organization": publisher_id}
        )
        assert publisher_sources.meta.count == 50

    def test_filter_open_access(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for open access sources."""
        oa_response = self.get_list_response(count=2000)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=is_oa%3Atrue&mailto=test%40example.com",
            json=oa_response,
        )

        oa_sources = client.sources.list(filter={"is_oa": True})
        assert oa_sources.meta.count == 2000

    def test_filter_by_apc_range(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering sources by APC range."""
        apc_response = self.get_list_response(count=1000)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=apc_usd%3A1000-5000&mailto=test%40example.com",
            json=apc_response,
        )

        affordable_sources = client.sources.list(
            filter={"apc_usd": "1000-5000"}
        )
        assert affordable_sources.meta.count == 1000

    def test_source_metrics(self) -> None:
        """Test source metric properties."""
        source_data = self.get_sample_entity()
        source = Source(**source_data)

        # Test type checking
        assert source.is_journal is True
        assert source.is_repository is False
        assert source.is_conference is False

        # Test APC handling
        assert source.has_apc is True
        assert source.get_apc_in_currency("USD") == 3500
        assert source.get_apc_in_currency("EUR") == 3200
        assert source.get_apc_in_currency("GBP") is None

        # Test ISSN handling
        all_issns = source.all_issns()
        assert "0031-9007" in all_issns
        assert "1079-7114" in all_issns
        assert len(all_issns) == 2

    def test_conference_sources(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test handling conference sources."""
        conference_data = self.get_sample_entity()
        conference_data.update(
            {
                "type": "conference",
                "display_name": "International Conference on Machine Learning",
                "alternate_titles": ["ICML", "Int Conf Mach Learn"],
            }
        )

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=type%3Aconference&mailto=test%40example.com",
            json=self.get_list_response(results=[conference_data]),
        )

        conferences = client.sources.list(filter={"type": "conference"})
        assert conferences.results[0].type == SourceType.CONFERENCE

    def test_doaj_sources(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for DOAJ sources."""
        doaj_response = self.get_list_response(count=1500)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=is_in_doaj%3Atrue&mailto=test%40example.com",
            json=doaj_response,
        )

        doaj_sources = client.sources.list(filter={"is_in_doaj": True})
        assert doaj_sources.meta.count == 1500

    def test_sort_by_works_count(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sorting sources by works count."""
        sorted_response = self.get_list_response()

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?sort=works_count%3Adesc&mailto=test%40example.com",
            json=sorted_response,
        )

        result = client.sources.list(sort="works_count:desc")
        assert result.meta.count == 100

    def test_homepage_url_filter(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering sources that have homepage URLs."""
        homepage_response = self.get_list_response(count=8000)

        httpx_mock.add_response(
            url="https://api.openalex.org/sources?filter=homepage_url%3A%21null&mailto=test%40example.com",
            json=homepage_response,
        )

        sources_with_homepage = client.sources.list(
            filter={"homepage_url": "!null"}
        )
        assert sources_with_homepage.meta.count == 8000

    @pytest.mark.asyncio()
    async def test_async_by_issn(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        issn = "0031-9007"
        entity = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/sources/issn:{issn}?mailto=test%40example.com",
            json=entity,
        )
        source = await async_client.sources.by_issn(f" {issn} ")
        assert source.id == entity["id"]
