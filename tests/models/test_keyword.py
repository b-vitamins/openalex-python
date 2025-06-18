"""
Comprehensive tests for the Keyword model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestKeywordModel:
    """Test suite for Keyword model with real OpenAlex data structure."""

    def test_keyword_basic_fields(self, mock_keyword_data):
        """Test basic keyword fields from fixture."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)

        # Basic identifiers
        assert keyword.id == "https://openalex.org/keywords/cardiac-imaging"
        assert keyword.display_name == "Cardiac Imaging"

        # Metrics (note: this keyword has no works yet)
        assert keyword.works_count == 0
        assert keyword.cited_by_count == 0

    def test_keyword_works_api_url(self, mock_keyword_data):
        """Test works API URL."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)
        assert (
            keyword.works_api_url
            == "https://api.openalex.org/works?filter=keywords.id:keywords/cardiac-imaging"
        )

    def test_keyword_updated_date(self, mock_keyword_data):
        """Test updated date field."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)
        assert keyword.updated_date == date(2024, 5, 31)

    def test_keyword_created_date(self, mock_keyword_data):
        """Test created date field."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)
        assert keyword.created_date == date(2024, 4, 10)

    def test_keyword_minimal_data(self):
        """Test keyword with minimal required fields."""
        from openalex.models import Keyword

        minimal_keyword = Keyword(
            id="https://openalex.org/keywords/test-keyword",
            display_name="Test Keyword",
        )

        assert (
            minimal_keyword.id == "https://openalex.org/keywords/test-keyword"
        )
        assert minimal_keyword.display_name == "Test Keyword"
        assert minimal_keyword.works_count == 0
        assert minimal_keyword.cited_by_count == 0

    def test_keyword_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Keyword

        # Missing required fields
        with pytest.raises(ValidationError):
            Keyword()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Keyword(id="not-a-url", display_name="Test")

    def test_keyword_with_works(self):
        """Test keyword that has associated works."""
        from openalex.models import Keyword

        keyword_data = {
            "id": "https://openalex.org/keywords/machine-learning",
            "display_name": "Machine Learning",
            "works_count": 150000,
            "cited_by_count": 5000000,
            "works_api_url": "https://api.openalex.org/works?filter=keywords.id:keywords/machine-learning",
            "created_date": "2023-01-01",
            "updated_date": "2024-06-01",
        }

        keyword = Keyword(**keyword_data)

        assert keyword.display_name == "Machine Learning"
        assert keyword.works_count == 150000
        assert keyword.cited_by_count == 5000000

    def test_compound_keyword(self):
        """Test multi-word compound keyword."""
        from openalex.models import Keyword

        keyword_data = {
            "id": "https://openalex.org/keywords/artificial-neural-networks",
            "display_name": "Artificial Neural Networks",
            "works_count": 75000,
            "cited_by_count": 2500000,
        }

        keyword = Keyword(**keyword_data)

        assert keyword.display_name == "Artificial Neural Networks"
        assert " " in keyword.display_name  # Multi-word keyword

    def test_specialized_keyword(self):
        """Test highly specialized technical keyword."""
        from openalex.models import Keyword

        keyword_data = {
            "id": "https://openalex.org/keywords/crispr-cas9-gene-editing",
            "display_name": "CRISPR-Cas9 Gene Editing",
            "works_count": 5000,
            "cited_by_count": 150000,
        }

        keyword = Keyword(**keyword_data)

        assert "CRISPR" in keyword.display_name
        assert keyword.works_count < 10000  # Specialized topic

    def test_emerging_keyword(self, mock_keyword_data):
        """Test newly created keyword with no works yet."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)

        # New keyword characteristics
        assert keyword.works_count == 0
        assert keyword.cited_by_count == 0
        assert keyword.created_date == date(2024, 4, 10)

        # Created recently
        days_since_creation = (date(2024, 5, 31) - keyword.created_date).days
        assert days_since_creation < 60  # Less than 2 months old

    def test_keyword_url_structure(self, mock_keyword_data):
        """Test keyword ID URL structure."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)

        # Keywords have a specific URL pattern
        assert keyword.id.startswith("https://openalex.org/keywords/")
        assert "keywords/" in keyword.id

        # The slug part should be lowercase with hyphens
        slug = keyword.id.split("/keywords/")[-1]
        assert slug == "cardiac-imaging"
        assert "-" in slug  # Hyphenated

    def test_keyword_display_name_formatting(self):
        """Test various display name formats."""
        from openalex.models import Keyword

        # Title case
        keyword1 = Keyword(
            id="https://openalex.org/keywords/test1",
            display_name="Quantum Computing",
        )
        assert keyword1.display_name == "Quantum Computing"

        # With acronym
        keyword2 = Keyword(
            id="https://openalex.org/keywords/test2",
            display_name="COVID-19 Research",
        )
        assert keyword2.display_name == "COVID-19 Research"

        # With special characters
        keyword3 = Keyword(
            id="https://openalex.org/keywords/test3",
            display_name="Drug-Drug Interactions",
        )
        assert keyword3.display_name == "Drug-Drug Interactions"

    def test_keyword_metrics_range(self):
        """Test different scales of keyword metrics."""
        from openalex.models import Keyword

        # Popular keyword
        popular_keyword = Keyword(
            id="https://openalex.org/keywords/cancer",
            display_name="Cancer",
            works_count=5000000,
            cited_by_count=100000000,
        )
        assert popular_keyword.works_count > 1000000
        assert popular_keyword.cited_by_count > 10000000

        # Niche keyword
        niche_keyword = Keyword(
            id="https://openalex.org/keywords/quantum-dot-solar-cells",
            display_name="Quantum Dot Solar Cells",
            works_count=500,
            cited_by_count=8000,
        )
        assert niche_keyword.works_count < 1000
        assert niche_keyword.cited_by_count < 10000

        # Citation-to-work ratio
        popular_ratio = (
            popular_keyword.cited_by_count / popular_keyword.works_count
        )
        niche_keyword.cited_by_count / niche_keyword.works_count
        assert popular_ratio > 0  # Both should have positive ratios

    def test_keyword_api_filter_format(self, mock_keyword_data):
        """Test the API filter format in works_api_url."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)

        # Check filter format
        assert "filter=keywords.id:" in keyword.works_api_url
        assert keyword.works_api_url.endswith("keywords/cardiac-imaging")

    def test_keyword_complete_profile(self, mock_keyword_data):
        """Test complete keyword profile with all fields populated."""
        from openalex.models import Keyword

        keyword = Keyword(**mock_keyword_data)

        # Verify all fields are populated
        assert keyword.id is not None
        assert keyword.display_name is not None
        assert keyword.works_count is not None
        assert keyword.cited_by_count is not None
        assert keyword.works_api_url is not None
        assert keyword.created_date is not None
        assert keyword.updated_date is not None

    def test_keyword_simple_structure(self):
        """Test that Keyword is a simple model without nested structures."""
        from openalex.models import Keyword

        keyword = Keyword(
            id="https://openalex.org/keywords/test", display_name="Test"
        )

        # Keywords don't have complex nested structures like other entities
        assert not hasattr(keyword, "ids")
        assert not hasattr(keyword, "summary_stats")
        assert not hasattr(keyword, "international")
        assert not hasattr(keyword, "counts_by_year")


class TestKeyword:
    def test_keyword_validation_and_properties(self):
        """Test Keyword model validation and computed properties."""
        from openalex.models import Keyword
        from datetime import date

        keyword_data = {
            "id": "https://openalex.org/K123",
            "display_name": "machine learning",
            "created_date": "2015-01-01",
            "updated_date": "2024-01-01",
            "works_count": 50000,
            "cited_by_count": 1000000,
            "works_api_url": "https://api.openalex.org/works?filter=keywords.id:K123",
            "updated": "2024-01-01T00:00:00"
        }

        keyword = Keyword(**keyword_data)

        assert keyword.id == "https://openalex.org/K123"
        assert isinstance(keyword.created_date, date)
        assert isinstance(keyword.updated_date, date)
        assert keyword.works_count == 50000
        assert keyword.cited_by_count == 1000000
        assert keyword.openalex_id == "K123"

        minimal_keyword = Keyword(
            id="https://openalex.org/K456",
            display_name="test keyword"
        )
        assert minimal_keyword.works_count == 0
        assert minimal_keyword.cited_by_count == 0
        assert minimal_keyword.created_date is None
