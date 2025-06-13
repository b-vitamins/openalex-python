"""
Comprehensive tests for the Concept model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestConceptModel:
    """Test suite for Concept model with real OpenAlex data structure."""

    def test_concept_basic_fields(self, mock_concept_data):
        """Test basic concept fields from fixture."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        # Basic identifiers
        assert concept.id == "https://openalex.org/C71924100"
        assert concept.wikidata == "https://www.wikidata.org/wiki/Q11190"
        assert concept.display_name == "Medicine"
        assert concept.level == 0  # Top-level concept

        # Description
        assert (
            concept.description
            == "field of study for diagnosing, treating and preventing disease"
        )

        # Metrics
        assert concept.works_count == 64992842
        assert concept.cited_by_count == 856329809

    def test_concept_summary_stats(self, mock_concept_data):
        """Test summary statistics."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert concept.summary_stats is not None
        assert (
            concept.summary_stats.two_year_mean_citedness == 1.7869663176673092
        )
        assert concept.summary_stats.h_index == 3292
        assert concept.summary_stats.i10_index == 14227920

        # Test convenience properties
        assert concept.h_index == 3292
        assert concept.i10_index == 14227920

    def test_concept_ids_structure(self, mock_concept_data):
        """Test the IDs nested structure."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert concept.ids.openalex == "https://openalex.org/C71924100"
        assert concept.ids.wikidata == "https://www.wikidata.org/wiki/Q11190"
        assert concept.ids.mag == "71924100"
        assert concept.ids.wikipedia == "https://en.wikipedia.org/wiki/Medicine"
        assert concept.ids.umls_cui == ["C0013227"]

    def test_concept_image_urls(self, mock_concept_data):
        """Test image URLs."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert (
            concept.image_url
            == "https://upload.wikimedia.org/wikipedia/commons/d/d2/Asklepios.3.jpg"
        )
        assert (
            concept.image_thumbnail_url
            == "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Asklepios.3.jpg/66px-Asklepios.3.jpg"
        )

    def test_concept_international_names(self, mock_concept_data):
        """Test international display names and descriptions."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert concept.international is not None

        # Check display names in various languages
        display_names = concept.international.display_name
        assert display_names.get("en") == "medicine"
        assert display_names.get("es") == "medicina"
        assert display_names.get("fr") == "médecine"
        assert display_names.get("de") == "Medizin"
        assert display_names.get("zh") == "医学"
        assert display_names.get("ja") == "医学"
        assert display_names.get("ar") == "طب"

        # Check descriptions
        descriptions = concept.international.description
        assert "field of study" in descriptions.get("en", "").lower()
        assert "corps humain" in descriptions.get("fr", "").lower()

    def test_concept_ancestors(self, mock_concept_data):
        """Test concept ancestors (hierarchical relationships)."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        # Medicine is a top-level concept, so no ancestors
        assert concept.ancestors == []

    def test_concept_related_concepts(self, mock_concept_data):
        """Test related concepts."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert len(concept.related_concepts) > 40

        # Check top related concepts
        top_related = concept.related_concepts[:5]

        # Surgery should be highly related to Medicine
        surgery = next(c for c in top_related if c.display_name == "Surgery")
        assert surgery.score > 100
        assert surgery.id == "https://openalex.org/C141071460"

        # Other medical fields
        related_names = [c.display_name for c in top_related]
        assert "Surgery" in related_names
        assert "Nursing" in related_names

    def test_concept_counts_by_year(self, mock_concept_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        assert len(concept.counts_by_year) == 14

        # Most recent year
        recent = concept.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 891805
        assert recent.cited_by_count == 19492777

        # Verify descending order
        years = [c.year for c in concept.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_concept_works_api_url(self, mock_concept_data):
        """Test works API URL."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)
        assert (
            concept.works_api_url
            == "https://api.openalex.org/works?filter=concepts.id:C71924100"
        )

    def test_concept_updated_date(self, mock_concept_data):
        """Test updated date field."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)
        assert concept.updated_date == date(2025, 6, 8)

    def test_concept_created_date(self, mock_concept_data):
        """Test created date field."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)
        assert concept.created_date == date(2016, 6, 24)

    def test_concept_minimal_data(self):
        """Test concept with minimal required fields."""
        from openalex.models import Concept

        minimal_concept = Concept(
            id="https://openalex.org/C123456", display_name="Test Concept"
        )

        assert minimal_concept.id == "https://openalex.org/C123456"
        assert minimal_concept.display_name == "Test Concept"
        assert minimal_concept.wikidata is None
        assert minimal_concept.level == 0
        assert minimal_concept.description is None
        assert minimal_concept.works_count == 0

    def test_concept_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Concept

        # Missing required fields
        with pytest.raises(ValidationError):
            Concept()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Concept(id="not-a-url", display_name="Test")

    def test_concept_hierarchy_levels(self):
        """Test concepts at different hierarchy levels."""
        from openalex.models import Concept

        # Level 0 - Top level concept
        medicine = Concept(
            id="https://openalex.org/C1",
            display_name="Medicine",
            level=0,
            ancestors=[],
        )
        assert medicine.level == 0
        assert len(medicine.ancestors) == 0

        # Level 1 - Sub-concept
        surgery = Concept(
            id="https://openalex.org/C2",
            display_name="Surgery",
            level=1,
            ancestors=[
                {
                    "id": "https://openalex.org/C1",
                    "display_name": "Medicine",
                    "level": 0,
                }
            ],
        )
        assert surgery.level == 1
        assert len(surgery.ancestors) == 1
        assert surgery.ancestors[0].display_name == "Medicine"

        # Level 2 - More specific
        cardiac_surgery = Concept(
            id="https://openalex.org/C3",
            display_name="Cardiac Surgery",
            level=2,
            ancestors=[
                {
                    "id": "https://openalex.org/C1",
                    "display_name": "Medicine",
                    "level": 0,
                },
                {
                    "id": "https://openalex.org/C2",
                    "display_name": "Surgery",
                    "level": 1,
                },
            ],
        )
        assert cardiac_surgery.level == 2
        assert len(cardiac_surgery.ancestors) == 2

    def test_concept_with_umls_codes(self, mock_concept_data):
        """Test concept with UMLS CUI codes."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        # Medicine has UMLS codes
        assert concept.ids.umls_cui == ["C0013227"]
        assert len(concept.ids.umls_cui) == 1

    def test_interdisciplinary_concept(self):
        """Test concept spanning multiple fields."""
        from openalex.models import Concept

        bioinformatics_data = {
            "id": "https://openalex.org/C789",
            "display_name": "Bioinformatics",
            "level": 1,
            "description": "Application of computational methods to biological data",
            "related_concepts": [
                {
                    "id": "https://openalex.org/C41008148",
                    "display_name": "Computer science",
                    "level": 0,
                    "score": 95.5,
                },
                {
                    "id": "https://openalex.org/C86803240",
                    "display_name": "Biology",
                    "level": 0,
                    "score": 92.3,
                },
            ],
        }

        concept = Concept(**bioinformatics_data)

        # Should be related to both CS and Biology
        related_fields = [c.display_name for c in concept.related_concepts]
        assert "Computer science" in related_fields
        assert "Biology" in related_fields

    def test_concept_metrics_scale(self, mock_concept_data):
        """Test the scale of metrics for major concepts."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        # Medicine is one of the largest concepts
        assert concept.works_count > 60_000_000
        assert concept.cited_by_count > 800_000_000
        assert concept.h_index > 3000
        assert concept.i10_index > 14_000_000

    def test_concept_complete_profile(self, mock_concept_data):
        """Test complete concept profile with all fields populated."""
        from openalex.models import Concept

        concept = Concept(**mock_concept_data)

        # Verify all major sections are populated
        assert concept.id is not None
        assert concept.display_name is not None
        assert concept.description is not None
        assert concept.works_count > 0
        assert concept.cited_by_count > 0
        assert concept.level is not None
        assert len(concept.related_concepts) > 0
        assert len(concept.counts_by_year) > 0
        assert concept.summary_stats is not None
        assert concept.ids is not None
        assert concept.international is not None
        assert concept.image_url is not None
