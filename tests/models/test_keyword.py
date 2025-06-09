from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import Keyword


class TestKeyword:
    """Test Keyword model with comprehensive fixtures."""

    @pytest.fixture
    def comprehensive_keyword_data(self) -> dict[str, Any]:
        """Comprehensive keyword data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/keywords/machine-learning",
            "display_name": "Machine Learning",
            "score": 1234.56,
            "works_count": 987654,
            "cited_by_count": 12345678,
        }

    @pytest.fixture
    def popular_keyword_data(self) -> dict[str, Any]:
        """Popular keyword with high metrics."""
        return {
            "id": "https://openalex.org/keywords/covid-19",
            "display_name": "COVID-19",
            "score": 5678.90,
            "works_count": 2345678,
            "cited_by_count": 34567890,
        }

    @pytest.fixture
    def new_keyword_data(self) -> dict[str, Any]:
        """New keyword with low metrics."""
        return {
            "id": "https://openalex.org/keywords/quantum-machine-learning",
            "display_name": "Quantum Machine Learning",
            "score": 123.45,
            "works_count": 543,
            "cited_by_count": 2345,
        }

    def test_keyword_creation(
        self, comprehensive_keyword_data: dict[str, Any]
    ) -> None:
        """Test creating a keyword with all fields."""
        keyword = Keyword(**comprehensive_keyword_data)

        assert keyword.id == "https://openalex.org/keywords/machine-learning"
        assert keyword.display_name == "Machine Learning"
        assert keyword.score == 1234.56
        assert keyword.works_count == 987654
        assert keyword.cited_by_count == 12345678

    def test_keyword_average_citations(
        self, comprehensive_keyword_data: dict[str, Any]
    ) -> None:
        """Test average citations per work calculation."""
        keyword = Keyword(**comprehensive_keyword_data)

        # 12345678 / 987654 ≈ 12.5
        assert keyword.average_citations_per_work == pytest.approx(
            12.5, rel=0.01
        )

    def test_keyword_popularity_thresholds(
        self, comprehensive_keyword_data: dict[str, Any]
    ) -> None:
        """Test popularity threshold checking."""
        keyword = Keyword(**comprehensive_keyword_data)

        # Default threshold is 1000
        assert keyword.is_popular() is True
        assert keyword.is_popular(threshold=1000) is True
        assert keyword.is_popular(threshold=10000) is False
        assert keyword.is_popular(threshold=100) is True

    def test_keyword_no_works(self) -> None:
        """Test keyword with no works."""
        keyword = Keyword(
            id="https://openalex.org/keywords/new-keyword",
            display_name="Brand New Keyword",
            works_count=0,
            cited_by_count=0,
        )

        assert keyword.works_count == 0
        assert keyword.cited_by_count == 0
        assert keyword.average_citations_per_work is None
        assert keyword.is_popular() is False

    def test_popular_keyword(
        self, popular_keyword_data: dict[str, Any]
    ) -> None:
        """Test highly popular keyword."""
        keyword = Keyword(**popular_keyword_data)

        assert keyword.display_name == "COVID-19"
        assert keyword.average_citations_per_work == pytest.approx(
            14.75, rel=0.01
        )
        assert keyword.is_popular(threshold=10000) is True
        assert keyword.is_popular(threshold=100000) is False

    def test_new_keyword_metrics(
        self, new_keyword_data: dict[str, Any]
    ) -> None:
        """Test newer keyword with lower metrics."""
        keyword = Keyword(**new_keyword_data)

        assert keyword.display_name == "Quantum Machine Learning"
        assert keyword.works_count == 543
        assert keyword.average_citations_per_work == pytest.approx(
            4.32, rel=0.01
        )
        assert keyword.is_popular(threshold=1000) is False
        assert keyword.is_popular(threshold=500) is True

    def test_keyword_minimal_data(self) -> None:
        """Test keyword with minimal required data."""
        keyword = Keyword(id="K123", display_name="Test Keyword")

        assert keyword.id == "K123"
        assert keyword.display_name == "Test Keyword"
        assert keyword.score is None
        assert keyword.works_count == 0
        assert keyword.cited_by_count == 0
        assert keyword.average_citations_per_work is None

    def test_keyword_validation_errors(self) -> None:
        """Test validation errors for invalid keyword data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Keyword()

        # Missing display_name
        with pytest.raises(ValidationError):
            Keyword(id="K123")

        # Negative counts
        with pytest.raises(ValidationError):
            Keyword(id="K123", display_name="Test", works_count=-1)

    def test_keyword_edge_cases(self) -> None:
        """Test edge cases for keyword metrics."""
        # Keyword with citations but no works (shouldn't happen but test robustness)
        keyword = Keyword(
            id="K456",
            display_name="Edge Case",
            works_count=0,
            cited_by_count=1000,
        )
        assert keyword.average_citations_per_work is None

        # Very high score
        keyword_high_score = Keyword(
            id="K789",
            display_name="High Score",
            score=999999.99,
            works_count=1,
            cited_by_count=1,
        )
        assert keyword_high_score.score == 999999.99

        # Exact threshold match
        keyword_threshold = Keyword(
            id="K999",
            display_name="Threshold Test",
            works_count=1000,
            cited_by_count=5000,
        )
        assert keyword_threshold.is_popular(threshold=1000) is True

    def test_keyword_string_representation(self) -> None:
        """Test keyword string representation."""
        keyword = Keyword(
            id="https://openalex.org/keywords/artificial-intelligence",
            display_name="Artificial Intelligence",
            score=2500.0,
            works_count=1500000,
            cited_by_count=25000000,
        )

        # Test that the keyword can be converted to string
        str_repr = str(keyword)
        assert str_repr is not None

        # Verify the display name is accessible
        assert keyword.display_name == "Artificial Intelligence"
