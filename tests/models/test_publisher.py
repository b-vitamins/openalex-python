from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import Publisher


class TestPublisher:
    """Test Publisher model with comprehensive realistic fixtures."""

    @pytest.fixture
    def parent_publisher_data(self) -> dict[str, Any]:
        """Parent publisher data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/P4310319965",
            "display_name": "Springer Nature",
            "alternate_titles": [
                "Springer Nature Group",
                "Springer Nature Limited",
            ],
            "country_codes": ["GB", "DE", "US"],
            "hierarchy_level": 0,
            "parent_publisher": None,
            "lineage": ["https://openalex.org/P4310319965"],
            "works_count": 12345678,
            "cited_by_count": 234567890,
            "counts_by_year": [
                {
                    "year": 2024,
                    "works_count": 456789,
                    "cited_by_count": 8901234,
                },
                {
                    "year": 2023,
                    "works_count": 445678,
                    "cited_by_count": 8789012,
                },
                {
                    "year": 2022,
                    "works_count": 434567,
                    "cited_by_count": 8678901,
                },
                {
                    "year": 2021,
                    "works_count": 423456,
                    "cited_by_count": 8567890,
                },
                {
                    "year": 2020,
                    "works_count": 412345,
                    "cited_by_count": 8456789,
                },
            ],
            "roles": [
                {
                    "role": "publisher",
                    "id": "https://openalex.org/P4310319965",
                    "works_count": 12345678,
                }
            ],
            "sources_api_url": "https://api.openalex.org/sources?filter=host_organization.id:P4310319965",
            "ids": {
                "openalex": "https://openalex.org/P4310319965",
                "ror": "https://ror.org/0566bfb96",
                "wikidata": "https://www.wikidata.org/wiki/Q176916",
            },
            "created_date": "2016-06-24",
            "updated_date": "2024-12-16T12:34:56.789012",
        }

    @pytest.fixture
    def child_publisher_data(self) -> dict[str, Any]:
        """Child publisher data (imprint)."""
        return {
            "id": "https://openalex.org/P4310320568",
            "display_name": "Springer",
            "alternate_titles": [
                "Springer-Verlag",
                "Springer Science+Business Media",
            ],
            "country_codes": ["DE"],
            "hierarchy_level": 1,
            "parent_publisher": "https://openalex.org/P4310319965",
            "lineage": [
                "https://openalex.org/P4310319965",
                "https://openalex.org/P4310320568",
            ],
            "works_count": 5678901,
            "cited_by_count": 123456789,
            "counts_by_year": [
                {
                    "year": 2024,
                    "works_count": 234567,
                    "cited_by_count": 4567890,
                },
                {
                    "year": 2023,
                    "works_count": 223456,
                    "cited_by_count": 4456789,
                },
            ],
            "roles": [
                {
                    "role": "publisher",
                    "id": "https://openalex.org/P4310320568",
                    "works_count": 5678901,
                }
            ],
            "sources_api_url": "https://api.openalex.org/sources?filter=host_organization.id:P4310320568",
            "ids": {
                "openalex": "https://openalex.org/P4310320568",
                "wikidata": "https://www.wikidata.org/wiki/Q176916",
            },
        }

    @pytest.fixture
    def university_press_publisher_data(self) -> dict[str, Any]:
        """University press publisher data."""
        return {
            "id": "https://openalex.org/P4310311648",
            "display_name": "Oxford University Press",
            "alternate_titles": [
                "OUP",
                "Oxford UP",
                "The Oxford University Press",
            ],
            "country_codes": ["GB"],
            "hierarchy_level": 0,
            "parent_publisher": None,
            "lineage": ["https://openalex.org/P4310311648"],
            "works_count": 2345678,
            "cited_by_count": 45678901,
            "counts_by_year": [
                {"year": 2024, "works_count": 89012, "cited_by_count": 1234567}
            ],
            "roles": [
                {
                    "role": "publisher",
                    "id": "https://openalex.org/P4310311648",
                    "works_count": 2345678,
                },
                {
                    "role": "institution",
                    "id": "https://openalex.org/I40120149",
                    "works_count": 345678,
                },
            ],
            "sources_api_url": "https://api.openalex.org/sources?filter=host_organization.id:P4310311648",
            "ids": {
                "openalex": "https://openalex.org/P4310311648",
                "ror": "https://ror.org/02n415q13",
                "wikidata": "https://www.wikidata.org/wiki/Q217595",
            },
        }

    def test_parent_publisher_creation(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test creating a parent publisher with all fields."""
        publisher = Publisher(**parent_publisher_data)

        # Basic fields
        assert publisher.id == "https://openalex.org/P4310319965"
        assert publisher.display_name == "Springer Nature"

        # Hierarchy
        assert publisher.hierarchy_level == 0
        assert publisher.parent_publisher is None
        assert len(publisher.lineage) == 1
        assert publisher.lineage[0] == publisher.id

        # Properties
        assert publisher.is_parent_publisher is True
        assert publisher.has_parent() is False

        # Metrics
        assert publisher.works_count == 12345678
        assert publisher.cited_by_count == 234567890

    def test_publisher_alternate_titles(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test publisher alternate titles."""
        publisher = Publisher(**parent_publisher_data)

        assert len(publisher.alternate_titles) == 2
        assert "Springer Nature Group" in publisher.alternate_titles
        assert "Springer Nature Limited" in publisher.alternate_titles

    def test_publisher_country_codes(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test multiple country codes."""
        publisher = Publisher(**parent_publisher_data)

        assert len(publisher.country_codes) == 3
        assert "GB" in publisher.country_codes
        assert "DE" in publisher.country_codes
        assert "US" in publisher.country_codes

        # Helper property
        assert publisher.countries == ["GB", "DE", "US"]

    def test_publisher_counts_by_year(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test yearly publication and citation counts."""
        publisher = Publisher(**parent_publisher_data)

        assert len(publisher.counts_by_year) == 5

        recent = publisher.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 456789
        assert recent.cited_by_count == 8901234

    def test_publisher_roles(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test publisher roles."""
        publisher = Publisher(**parent_publisher_data)

        assert len(publisher.roles) == 1
        role = publisher.roles[0]
        assert role.role == "publisher"
        assert role.id == publisher.id
        assert role.works_count == 12345678

    def test_publisher_ids(self, parent_publisher_data: dict[str, Any]) -> None:
        """Test publisher external identifiers."""
        publisher = Publisher(**parent_publisher_data)

        assert publisher.ids is not None
        assert publisher.ids.openalex == publisher.id
        assert str(publisher.ids.ror) == "https://ror.org/0566bfb96"
        assert "wikidata.org" in str(publisher.ids.wikidata)

    def test_child_publisher(
        self, child_publisher_data: dict[str, Any]
    ) -> None:
        """Test child publisher (imprint) with parent."""
        publisher = Publisher(**child_publisher_data)

        # Hierarchy
        assert publisher.hierarchy_level == 1
        assert publisher.parent_publisher == "https://openalex.org/P4310319965"
        assert len(publisher.lineage) == 2

        # Properties
        assert publisher.is_parent_publisher is False
        assert publisher.has_parent() is True

        # Country codes
        assert publisher.country_codes == ["DE"]

    def test_university_press_publisher(
        self, university_press_publisher_data: dict[str, Any]
    ) -> None:
        """Test university press with multiple roles."""
        publisher = Publisher(**university_press_publisher_data)

        assert publisher.display_name == "Oxford University Press"
        assert "OUP" in publisher.alternate_titles

        # Multiple roles
        assert len(publisher.roles) == 2

        # Publisher role
        pub_role = publisher.roles[0]
        assert pub_role.role == "publisher"
        assert pub_role.works_count == 2345678

        # Institution role
        inst_role = publisher.roles[1]
        assert inst_role.role == "institution"
        assert inst_role.id == "https://openalex.org/I40120149"

    def test_publisher_helper_methods(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test publisher helper methods."""
        publisher = Publisher(**parent_publisher_data)

        # Year-based lookups
        assert publisher.works_in_year(2024) == 456789
        assert publisher.citations_in_year(2023) == 8789012
        assert publisher.works_in_year(2019) == 0  # Not in data

        # Active years
        active_years = publisher.active_years()
        assert 2024 in active_years
        assert len(active_years) == 5

    def test_minimal_publisher(self) -> None:
        """Test publisher with minimal data."""
        publisher = Publisher(id="P123", display_name="Test Publisher")

        assert publisher.hierarchy_level == 0
        assert publisher.parent_publisher is None
        assert len(publisher.lineage) == 0
        assert publisher.country_codes == []
        assert publisher.is_parent_publisher is True

    def test_publisher_validation_errors(self) -> None:
        """Test validation errors for invalid publisher data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Publisher()

        # Invalid hierarchy level
        with pytest.raises(ValidationError):
            Publisher(id="P123", display_name="Test", hierarchy_level=-1)

    def test_publisher_edge_cases(self) -> None:
        """Test edge cases in publisher data."""
        # Publisher with empty lists
        publisher = Publisher(
            id="P456",
            display_name="Empty Publisher",
            alternate_titles=[],
            country_codes=[],
            lineage=[],
            counts_by_year=[],
            roles=[],
        )

        assert publisher.countries == []
        assert publisher.active_years() == []

        # Publisher at deep hierarchy level
        deep_publisher = Publisher(
            id="P789",
            display_name="Deep Imprint",
            hierarchy_level=3,
            parent_publisher="P456",
            lineage=["P123", "P456", "P789", "P999"],
        )
        assert deep_publisher.is_parent_publisher is False
        assert deep_publisher.has_parent() is True

    def test_datetime_fields(
        self, parent_publisher_data: dict[str, Any]
    ) -> None:
        """Test datetime field parsing."""
        publisher = Publisher(**parent_publisher_data)

        assert isinstance(publisher.created_date, str)
        assert publisher.created_date == "2016-06-24"

        assert isinstance(publisher.updated_date, datetime)
        assert publisher.updated_date.year == 2024
