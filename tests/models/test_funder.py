"""
Comprehensive tests for the Funder model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestFunderModel:
    """Test suite for Funder model with real OpenAlex data structure."""

    def test_funder_basic_fields(self, mock_funder_data):
        """Test basic funder fields from fixture."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        # Basic identifiers
        assert funder.id == "https://openalex.org/F4320332161"
        assert funder.display_name == "National Institutes of Health"

        # Alternate names
        assert funder.alternate_titles == [
            "US National Institutes of Health",
            "Institutos Nacionales de la Salud",
            "NIH",
        ]

        # Country and description
        assert funder.country_code == "US"
        assert funder.description == "US government medical research agency"

        # Metrics
        assert funder.grants_count == 273557
        assert funder.works_count == 386574
        assert funder.cited_by_count == 15234811

    def test_funder_homepage_and_images(self, mock_funder_data):
        """Test homepage and image URLs."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        assert funder.homepage_url == "http://www.nih.gov"
        assert (
            funder.image_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/NIH 2013 logo vertical.svg"
        )
        assert (
            funder.image_thumbnail_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/NIH 2013 logo vertical.svg&width=300"
        )

    def test_funder_summary_stats(self, mock_funder_data):
        """Test summary statistics."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        assert funder.summary_stats is not None
        assert funder.summary_stats.two_year_mean_citedness == 5.326992141129093
        assert funder.summary_stats.h_index == 859
        assert funder.summary_stats.i10_index == 234803

        # Test convenience properties
        assert funder.h_index == 859
        assert funder.i10_index == 234803

    def test_funder_ids_structure(self, mock_funder_data):
        """Test the IDs nested structure."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        assert funder.ids.openalex == "https://openalex.org/F4320332161"
        assert funder.ids.ror == "https://ror.org/01cwqze88"
        assert funder.ids.wikidata == "https://www.wikidata.org/entity/Q390551"
        assert funder.ids.crossref == "100000002"
        assert funder.ids.doi == "https://doi.org/10.13039/100000002"

    def test_funder_counts_by_year(self, mock_funder_data):
        """Test yearly grant and citation counts."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        assert len(funder.counts_by_year) == 14

        # Most recent year
        recent = funder.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 11187
        assert recent.cited_by_count == 861833

        # High-productivity year
        year_2021 = next(c for c in funder.counts_by_year if c.year == 2021)
        assert year_2021.works_count == 40674
        assert year_2021.cited_by_count == 1921450

        # Verify descending order
        years = [c.year for c in funder.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_funder_roles(self, mock_funder_data):
        """Test funder roles."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        assert len(funder.roles) == 3

        # Check different roles
        roles_dict = {r.role: r for r in funder.roles}

        assert "funder" in roles_dict
        assert roles_dict["funder"].id == funder.id
        assert roles_dict["funder"].works_count == 386574

        assert "institution" in roles_dict
        assert (
            roles_dict["institution"].id == "https://openalex.org/I1299303238"
        )
        assert roles_dict["institution"].works_count == 280601

        assert "publisher" in roles_dict
        assert roles_dict["publisher"].id == "https://openalex.org/P4310316754"
        assert roles_dict["publisher"].works_count == 38485

    def test_funder_updated_date(self, mock_funder_data):
        """Test updated date field."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)
        assert funder.updated_date == date(2025, 6, 17)

    def test_funder_created_date(self, mock_funder_data):
        """Test created date field."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)
        assert funder.created_date == date(2023, 2, 13)

    def test_funder_minimal_data(self):
        """Test funder with minimal required fields."""
        from openalex.models import Funder

        minimal_funder = Funder(
            id="https://openalex.org/F123456", display_name="Test Funder"
        )

        assert minimal_funder.id == "https://openalex.org/F123456"
        assert minimal_funder.display_name == "Test Funder"
        assert minimal_funder.country_code is None
        assert minimal_funder.description is None
        assert minimal_funder.grants_count == 0
        assert minimal_funder.works_count == 0

    def test_funder_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Funder

        # Missing required fields
        with pytest.raises(ValidationError):
            Funder()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Funder(id="not-a-url", display_name="Test")

        # Invalid country code
        with pytest.raises(ValidationError):
            Funder(
                id="https://openalex.org/F123",
                display_name="Test",
                country_code="ZZZ",  # Not a valid ISO code
            )

    def test_government_funder(self, mock_funder_data):
        """Test government funding agency."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        # NIH is a US government agency
        assert funder.country_code == "US"
        assert "government" in funder.description.lower()
        assert funder.grants_count > 250_000  # Major funder

    def test_private_foundation_funder(self):
        """Test private foundation funder."""
        from openalex.models import Funder

        funder_data = {
            "id": "https://openalex.org/F4320311493",
            "display_name": "Bill & Melinda Gates Foundation",
            "country_code": "US",
            "description": "Private philanthropic foundation",
            "alternate_titles": ["Gates Foundation", "BMGF"],
            "grants_count": 50000,
            "works_count": 75000,
        }

        funder = Funder(**funder_data)

        assert "Gates" in funder.display_name
        assert "foundation" in funder.description.lower()
        assert funder.grants_count > 0

    def test_international_funder(self):
        """Test international funding organization."""
        from openalex.models import Funder

        funder_data = {
            "id": "https://openalex.org/F789",
            "display_name": "European Research Council",
            "alternate_titles": ["ERC", "Conseil européen de la recherche"],
            "country_code": "EU",  # Or appropriate code
            "description": "EU funding body for frontier research",
            "grants_count": 15000,
        }

        funder = Funder(**funder_data)

        assert "European" in funder.display_name
        assert len(funder.alternate_titles) > 0
        assert funder.grants_count > 0

    def test_funder_with_crossref_doi(self, mock_funder_data):
        """Test funder with Crossref and DOI identifiers."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        # NIH has Crossref Funder Registry ID
        assert funder.ids.crossref == "100000002"
        assert funder.ids.doi == "https://doi.org/10.13039/100000002"
        assert "10.13039" in funder.ids.doi  # Crossref Funder ID prefix

    def test_funder_metrics_comparison(self):
        """Test comparing metrics between funders."""
        from openalex.models import Funder

        # Major government funder
        nih_data = {
            "id": "https://openalex.org/F1",
            "display_name": "National Institutes of Health",
            "grants_count": 273197,
            "works_count": 386464,
            "cited_by_count": 15223472,
            "summary_stats": {
                "2yr_mean_citedness": 5.3,
                "h_index": 855,
                "i10_index": 232869,
            },
        }

        # Smaller foundation
        foundation_data = {
            "id": "https://openalex.org/F2",
            "display_name": "Small Research Foundation",
            "grants_count": 500,
            "works_count": 1200,
            "cited_by_count": 50000,
            "summary_stats": {
                "2yr_mean_citedness": 2.1,
                "h_index": 85,
                "i10_index": 450,
            },
        }

        nih = Funder(**nih_data)
        foundation = Funder(**foundation_data)

        # NIH metrics should be much higher
        assert nih.grants_count > foundation.grants_count * 100
        assert nih.h_index > foundation.h_index * 5
        assert nih.cited_by_count > foundation.cited_by_count * 100

    def test_funder_complete_profile(self, mock_funder_data):
        """Test complete funder profile with all fields populated."""
        from openalex.models import Funder

        funder = Funder(**mock_funder_data)

        # Verify all major sections are populated
        assert funder.id is not None
        assert funder.display_name is not None
        assert funder.grants_count > 0
        assert funder.works_count > 0
        assert funder.cited_by_count > 0
        assert len(funder.counts_by_year) > 0
        assert funder.summary_stats is not None
        assert funder.ids is not None
        assert funder.homepage_url is not None
