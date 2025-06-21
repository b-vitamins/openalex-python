"""
Comprehensive tests for the Publisher model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestPublisherModel:
    """Test suite for Publisher model with real OpenAlex data structure."""

    def test_publisher_basic_fields(self, mock_publisher_data):
        """Test basic publisher fields from fixture."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        # Basic identifiers
        assert publisher.id == "https://openalex.org/P4310319965"
        assert publisher.display_name == "Springer Nature"

        # Alternate names
        assert publisher.alternate_titles == [
            "エイプレス",
            "Springer Nature Group",
            "施普林格-自然出版集团",
        ]

        # Hierarchy
        assert publisher.hierarchy_level == 0
        assert publisher.parent_publisher is None
        assert publisher.lineage == ["https://openalex.org/P4310319965"]

        # Country
        assert publisher.country_codes == ["DE"]

        # Metrics
        assert publisher.works_count == 10535865
        assert publisher.cited_by_count == 254043705

    def test_publisher_homepage_and_images(self, mock_publisher_data):
        """Test homepage and image URLs."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        assert publisher.homepage_url == "https://www.springernature.com"
        assert (
            publisher.image_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Springer Nature Logo.svg"
        )
        assert (
            publisher.image_thumbnail_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Springer Nature Logo.svg&width=300"
        )

    def test_publisher_summary_stats(self, mock_publisher_data):
        """Test summary statistics."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        assert publisher.summary_stats is not None
        assert (
            publisher.summary_stats.two_year_mean_citedness
            == 2.4417943212795215
        )
        assert publisher.summary_stats.h_index == 2059
        assert publisher.summary_stats.i10_index == 4256773

        # Test convenience properties
        assert publisher.h_index == 2059
        assert publisher.i10_index == 4256773

    def test_publisher_ids_structure(self, mock_publisher_data):
        """Test the IDs nested structure."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        assert publisher.ids.openalex == "https://openalex.org/P4310319965"
        assert publisher.ids.ror == "https://ror.org/0117jxy09"
        assert (
            publisher.ids.wikidata
            == "https://www.wikidata.org/entity/Q21096327"
        )

    def test_publisher_counts_by_year(self, mock_publisher_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        assert len(publisher.counts_by_year) == 12

        # Most recent year (note: 2023 in this data)
        recent = publisher.counts_by_year[0]
        assert recent.year == 2023
        assert recent.works_count == 137188
        assert recent.cited_by_count == 3713193

        # High-productivity year
        year_2022 = next(c for c in publisher.counts_by_year if c.year == 2022)
        assert year_2022.works_count == 591311
        assert year_2022.cited_by_count == 13004211

        # Verify descending order
        years = [c.year for c in publisher.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_publisher_roles(self, mock_publisher_data):
        """Test publisher roles."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        assert len(publisher.roles) == 3

        # Check different roles
        roles_dict = {r.role: r for r in publisher.roles}

        assert "institution" in roles_dict
        assert (
            roles_dict["institution"].id == "https://openalex.org/I1313014049"
        )
        assert roles_dict["institution"].works_count == 10187

        assert "publisher" in roles_dict
        assert roles_dict["publisher"].id == publisher.id
        assert roles_dict["publisher"].works_count == 10535865

    def test_publisher_sources_api_url(self, mock_publisher_data):
        """Test sources API URL."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)
        assert (
            publisher.sources_api_url
            == "https://api.openalex.org/sources?filter=host_organization.id:P4310319965"
        )

    def test_publisher_updated_date(self, mock_publisher_data):
        """Test updated date field."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)
        assert publisher.updated_date == date(2025, 6, 17)

    def test_publisher_created_date(self, mock_publisher_data):
        """Test created date field."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)
        assert publisher.created_date == date(2023, 1, 1)

    def test_publisher_minimal_data(self):
        """Test publisher with minimal required fields."""
        from openalex.models import Publisher

        minimal_publisher = Publisher(
            id="https://openalex.org/P123456", display_name="Test Publisher"
        )

        assert minimal_publisher.id == "https://openalex.org/P123456"
        assert minimal_publisher.display_name == "Test Publisher"
        assert minimal_publisher.hierarchy_level == 0
        assert minimal_publisher.parent_publisher is None
        assert minimal_publisher.lineage == []
        assert minimal_publisher.works_count == 0

    def test_publisher_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Publisher

        # Missing required fields
        with pytest.raises(ValidationError):
            Publisher()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Publisher(id="not-a-url", display_name="Test")

    def test_publisher_with_parent(self):
        """Test publisher with parent hierarchy."""
        from openalex.models import Publisher

        publisher_data = {
            "id": "https://openalex.org/P456",
            "display_name": "Nature Publishing Group",
            "hierarchy_level": 1,
            "parent_publisher": "https://openalex.org/P123",
            "lineage": [
                "https://openalex.org/P123",
                "https://openalex.org/P456",
            ],
        }

        publisher = Publisher(**publisher_data)

        assert publisher.hierarchy_level == 1
        assert publisher.parent_publisher == "https://openalex.org/P123"
        assert len(publisher.lineage) == 2
        assert publisher.lineage[0] == "https://openalex.org/P123"
        assert publisher.lineage[1] == "https://openalex.org/P456"

    def test_publisher_with_multiple_countries(self):
        """Test publisher operating in multiple countries."""
        from openalex.models import Publisher

        publisher_data = {
            "id": "https://openalex.org/P789",
            "display_name": "International Publisher",
            "country_codes": ["US", "GB", "DE", "JP"],
        }

        publisher = Publisher(**publisher_data)

        assert len(publisher.country_codes) == 4
        assert "US" in publisher.country_codes
        assert "GB" in publisher.country_codes
        assert "DE" in publisher.country_codes
        assert "JP" in publisher.country_codes

    def test_large_publisher_metrics(self, mock_publisher_data):
        """Test metrics for large publisher."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        # Springer Nature is one of the largest publishers
        assert publisher.works_count > 10_000_000
        assert publisher.cited_by_count > 250_000_000
        assert publisher.h_index > 2000
        assert publisher.i10_index > 4_000_000

    def test_publisher_complete_profile(self, mock_publisher_data):
        """Test complete publisher profile with all fields populated."""
        from openalex.models import Publisher

        publisher = Publisher(**mock_publisher_data)

        # Verify all major sections are populated
        assert publisher.id is not None
        assert publisher.display_name is not None
        assert publisher.works_count > 0
        assert publisher.cited_by_count > 0
        assert len(publisher.counts_by_year) > 0
        assert publisher.summary_stats is not None
        assert publisher.ids is not None
        assert publisher.homepage_url is not None
