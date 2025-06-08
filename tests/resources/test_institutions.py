"""Tests for Institutions resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from openalex.models import Institution, InstitutionType

from .base import BaseResourceTest

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources import (
        AsyncInstitutionsResource,
        InstitutionsResource,
    )


class TestInstitutionsResource(BaseResourceTest[Institution]):
    """Test Institutions resource functionality."""

    resource_name: ClassVar[str] = "institutions"
    entity_class: ClassVar[type[Institution]] = Institution
    sample_id: ClassVar[str] = "I1174212"
    sample_ids: ClassVar[list[str]] = ["I1174212", "I27837315", "I32971472"]

    def get_resource(self, client: OpenAlex) -> InstitutionsResource:
        """Get institutions resource."""
        return client.institutions

    def get_async_resource(
        self, client: AsyncOpenAlex
    ) -> AsyncInstitutionsResource:
        """Get async institutions resource."""
        return client.institutions

    def get_sample_entity(self) -> dict[str, Any]:
        """Get sample institution data."""
        return {
            "id": f"https://openalex.org/{self.sample_id}",
            "ror": "https://ror.org/04v7hvq31",
            "display_name": "Tulane University",
            "display_name_alternatives": [
                "Université Tulane",
                "Universidad Tulane",
            ],
            "works_count": 50000,
            "cited_by_count": 1000000,
            "summary_stats": {
                "2yr_mean_citedness": 3.2,
                "h_index": 250,
                "i10_index": 25000,
            },
            "country_code": "US",
            "type": "education",
            "lineage": ["https://openalex.org/I1174212"],
            "homepage_url": "https://tulane.edu",
            "image_url": "https://example.com/tulane-logo.png",
            "image_thumbnail_url": "https://example.com/tulane-logo-thumb.png",
            "geo": {
                "city": "New Orleans",
                "geonames_city_id": "4335045",
                "region": "Louisiana",
                "country_code": "US",
                "country": "United States",
                "latitude": 29.9511,
                "longitude": -90.0715,
            },
            "associated_institutions": [
                {
                    "id": "https://openalex.org/I2802835894",
                    "display_name": "Tulane Medical Center",
                    "ror": "https://ror.org/00jge9k46",
                    "relationship": "child",
                    "type": "healthcare",
                },
            ],
            "repositories": [
                {
                    "id": "https://openalex.org/S4306402521",
                    "display_name": "Tulane University Digital Library",
                    "host_organization": "https://openalex.org/I1174212",
                    "host_organization_name": "Tulane University",
                }
            ],
            "x_concepts": [
                {
                    "id": "https://openalex.org/C71924100",
                    "display_name": "Medicine",
                    "level": 0,
                    "score": 45.2,
                },
                {
                    "id": "https://openalex.org/C86803240",
                    "display_name": "Biology",
                    "level": 0,
                    "score": 40.5,
                },
            ],
            "counts_by_year": [
                {"year": 2023, "works_count": 1500, "cited_by_count": 75000},
                {"year": 2022, "works_count": 1400, "cited_by_count": 70000},
            ],
            "works_api_url": f"https://api.openalex.org/works?filter=institutions.id:{self.sample_id}",
            "updated_date": "2024-01-01",
            "created_date": "2023-01-01",
        }

    # Institution-specific tests
    def test_get_by_ror(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting institution by ROR ID."""
        ror = "04v7hvq31"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/institutions/https://ror.org/{ror}?mailto=test%40example.com",
            json=entity_data,
        )

        institution = client.institutions.by_ror(ror)
        assert institution.id == entity_data["id"]
        assert str(institution.ror) == f"https://ror.org/{ror}"

    def test_get_by_ror_with_prefix(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting institution by ROR with full URL."""
        ror_url = "https://ror.org/04v7hvq31"
        entity_data = self.get_sample_entity()

        httpx_mock.add_response(
            url=f"https://api.openalex.org/institutions/{ror_url}?mailto=test%40example.com",
            json=entity_data,
        )

        institution = client.institutions.by_ror(ror_url)
        assert institution.id == entity_data["id"]

    def test_filter_by_type(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering institutions by type."""
        education_response = self.get_list_response(count=5000)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=type%3Aeducation&mailto=test%40example.com",
            json=education_response,
        )

        universities = client.institutions.list(filter={"type": "education"})
        assert universities.meta.count == 5000

    def test_filter_by_country(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering institutions by country."""
        us_response = self.get_list_response(count=3000)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=country_code%3AUS&mailto=test%40example.com",
            json=us_response,
        )

        us_institutions = client.institutions.list(
            filter={"country_code": "US"}
        )
        assert us_institutions.meta.count == 3000

    def test_filter_by_multiple_countries(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering institutions by multiple countries."""
        multi_country_response = self.get_list_response(count=5000)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=country_code%3AUS%7CGB%7CCA&mailto=test%40example.com",
            json=multi_country_response,
        )

        institutions = client.institutions.list(
            filter={"country_code": ["US", "GB", "CA"]}
        )
        assert institutions.meta.count == 5000

    def test_filter_by_continent(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering institutions by continent."""
        europe_response = self.get_list_response(count=10000)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=continent%3Aeurope&mailto=test%40example.com",
            json=europe_response,
        )

        european_institutions = client.institutions.list(
            filter={"continent": "europe"}
        )
        assert european_institutions.meta.count == 10000

    def test_filter_by_works_count_range(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering institutions by works count range."""
        productive_response = self.get_list_response(count=500)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=works_count%3A10000-100000&mailto=test%40example.com",
            json=productive_response,
        )

        productive_institutions = client.institutions.list(
            filter={"works_count": "10000-100000"}
        )
        assert productive_institutions.meta.count == 500

    def test_institution_hierarchy(self) -> None:
        """Test institution hierarchy and relationships."""
        parent_data = self.get_sample_entity()
        parent_data["lineage"] = ["https://openalex.org/I1174212"]

        child_data = self.get_sample_entity()
        child_data.update(
            {
                "id": "https://openalex.org/I2802835894",
                "display_name": "Tulane Medical Center",
                "lineage": [
                    "https://openalex.org/I2802835894",
                    "https://openalex.org/I1174212",
                ],
            }
        )

        parent = Institution(**parent_data)
        child = Institution(**child_data)

        # Parent has no parent
        assert parent.parent_institution is None
        assert parent.root_institution is None

        # Child has parent
        assert len(child.lineage) == 2
        assert child.lineage[1] == parent.id

    def test_institution_geo_properties(self) -> None:
        """Test institution geographic properties."""
        inst_data = self.get_sample_entity()
        institution = Institution(**inst_data)

        assert institution.has_location() is True
        assert institution.geo.city == "New Orleans"
        assert institution.geo.latitude == 29.9511
        assert institution.geo.longitude == -90.0715

    def test_institution_repositories(self) -> None:
        """Test institution repository information."""
        inst_data = self.get_sample_entity()
        institution = Institution(**inst_data)

        assert institution.repository_count() == 1
        assert (
            institution.repositories[0].display_name
            == "Tulane University Digital Library"
        )

    def test_healthcare_institutions(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for healthcare institutions."""
        healthcare_response = self.get_list_response(count=2000)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=type%3Ahealthcare&mailto=test%40example.com",
            json=healthcare_response,
        )

        hospitals = client.institutions.list(filter={"type": "healthcare"})
        assert hospitals.meta.count == 2000

    def test_company_institutions(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test filtering for company institutions."""
        company_response = self.get_list_response(count=1500)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?filter=type%3Acompany&mailto=test%40example.com",
            json=company_response,
        )

        companies = client.institutions.list(filter={"type": "company"})
        assert companies.meta.count == 1500

    def test_search_with_geo_filter(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test searching with geographic filters."""
        geo_search_response = self.get_list_response(count=50)

        httpx_mock.add_response(
            url="https://api.openalex.org/institutions?search=university&filter=geo.city%3Anew+orleans&mailto=test%40example.com",
            json=geo_search_response,
        )

        result = client.institutions.search(
            "university", filter={"geo.city": "new orleans"}
        )
        assert result.meta.count == 50

    def test_associated_institutions(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting associated institutions."""
        # This would typically require following the associated_institutions links
        inst_data = self.get_sample_entity()
        institution = Institution(**inst_data)

        assert len(institution.associated_institutions) == 1
        assert institution.associated_institutions[0].relationship == "child"
        assert (
            institution.associated_institutions[0].type
            == InstitutionType.HEALTHCARE
        )
