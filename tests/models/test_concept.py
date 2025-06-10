from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    Concept,
    DehydratedConcept,
)


class TestConcept:
    """Test Concept model with comprehensive realistic fixtures."""

    @pytest.fixture()
    def comprehensive_concept_data(self) -> dict[str, Any]:
        """Comprehensive concept data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/C121332964",
            "wikidata": "https://www.wikidata.org/wiki/Q413",
            "display_name": "Physics",
            "level": 0,
            "description": "Physics is the natural science that studies matter, its motion and behavior through space and time, and the related entities of energy and force.",
            "works_count": 4567890,
            "cited_by_count": 87654321,
            "summary_stats": {
                "2yr_mean_citedness": 3.456789,
                "h_index": 543,
                "i10_index": 234567,
            },
            "ids": {
                "openalex": "https://openalex.org/C121332964",
                "wikidata": "https://www.wikidata.org/wiki/Q413",
                "wikipedia": "https://en.wikipedia.org/wiki/Physics",
                "umls_aui": ["A0000001"],
                "umls_cui": ["C0000001"],
                "mag": "121332964",
            },
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/CollageFisica.jpg/200px-CollageFisica.jpg",
            "image_thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/CollageFisica.jpg/100px-CollageFisica.jpg",
            "international_display_name": {
                "ar": "فيزياء",
                "ca": "física",
                "cy": "ffiseg",
                "da": "fysik",
                "de": "Physik",
                "el": "φυσική",
                "en": "physics",
                "eo": "fiziko",
                "es": "física",
                "et": "füüsika",
                "eu": "fisika",
                "fi": "fysiikka",
                "fr": "physique",
                "ga": "fisic",
                "gl": "física",
                "he": "פיזיקה",
                "hi": "भौतिक विज्ञान",
                "hu": "fizika",
                "id": "fisika",
                "it": "fisica",
                "ja": "物理学",
                "ko": "물리학",
                "la": "physica",
                "lt": "fizika",
                "lv": "fizika",
                "nl": "natuurkunde",
                "no": "fysikk",
                "pl": "fizyka",
                "pt": "física",
                "ro": "fizică",
                "ru": "физика",
                "sk": "fyzika",
                "sv": "fysik",
                "tr": "fizik",
                "uk": "фізика",
                "vi": "vật lý học",
                "zh": "物理学",
                "zh-cn": "物理学",
                "zh-hans": "物理学",
                "zh-hant": "物理學",
            },
            "ancestors": [],
            "related_concepts": [
                {
                    "id": "https://openalex.org/C62520636",
                    "wikidata": "https://www.wikidata.org/wiki/Q944",
                    "display_name": "Quantum mechanics",
                    "level": 1,
                    "score": 8.234567,
                },
                {
                    "id": "https://openalex.org/C33332235",
                    "wikidata": "https://www.wikidata.org/wiki/Q1069",
                    "display_name": "Thermodynamics",
                    "level": 1,
                    "score": 7.654321,
                },
                {
                    "id": "https://openalex.org/C120665830",
                    "wikidata": "https://www.wikidata.org/wiki/Q11397",
                    "display_name": "Classical mechanics",
                    "level": 1,
                    "score": 7.123456,
                },
            ],
            "works_api_url": "https://api.openalex.org/works?filter=concepts.id:C121332964",
            "counts_by_year": [
                {
                    "year": 2024,
                    "works_count": 234567,
                    "cited_by_count": 4567890,
                },
                {
                    "year": 2023,
                    "works_count": 223456,
                    "cited_by_count": 4345678,
                },
                {
                    "year": 2022,
                    "works_count": 212345,
                    "cited_by_count": 4123456,
                },
                {
                    "year": 2021,
                    "works_count": 201234,
                    "cited_by_count": 3901234,
                },
                {
                    "year": 2020,
                    "works_count": 190123,
                    "cited_by_count": 3678901,
                },
            ],
            "created_date": "2016-06-24",
            "updated_date": "2024-12-16T11:23:45.678901",
        }

    @pytest.fixture()
    def hierarchical_concept_data(self) -> dict[str, Any]:
        """Concept with complex hierarchy."""
        return {
            "id": "https://openalex.org/C62520636",
            "wikidata": "https://www.wikidata.org/wiki/Q944",
            "display_name": "Quantum mechanics",
            "level": 1,
            "description": "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles.",
            "works_count": 567890,
            "cited_by_count": 12345678,
            "ancestors": [
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                }
            ],
            "related_concepts": [
                {
                    "id": "https://openalex.org/C37914503",
                    "wikidata": "https://www.wikidata.org/wiki/Q11452",
                    "display_name": "Quantum field theory",
                    "level": 2,
                    "score": 9.123456,
                },
                {
                    "id": "https://openalex.org/C203014093",
                    "wikidata": "https://www.wikidata.org/wiki/Q44690",
                    "display_name": "Quantum entanglement",
                    "level": 2,
                    "score": 8.765432,
                },
                {
                    "id": "https://openalex.org/C77077793",
                    "wikidata": "https://www.wikidata.org/wiki/Q176645",
                    "display_name": "Wave function",
                    "level": 2,
                    "score": 8.234567,
                },
            ],
        }

    @pytest.fixture()
    def deep_hierarchy_concept_data(self) -> dict[str, Any]:
        """Concept at level 5 with full ancestry."""
        return {
            "id": "https://openalex.org/C3007834351",
            "wikidata": "https://www.wikidata.org/wiki/Q82069695",
            "display_name": "Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)",
            "level": 5,
            "works_count": 234567,
            "cited_by_count": 3456789,
            "ancestors": [
                {
                    "id": "https://openalex.org/C71924100",
                    "wikidata": "https://www.wikidata.org/wiki/Q11190",
                    "display_name": "Medicine",
                    "level": 0,
                },
                {
                    "id": "https://openalex.org/C142724271",
                    "wikidata": "https://www.wikidata.org/wiki/Q7208",
                    "display_name": "Pathology",
                    "level": 1,
                },
                {
                    "id": "https://openalex.org/C203014093",
                    "wikidata": "https://www.wikidata.org/wiki/Q112193867",
                    "display_name": "Virology",
                    "level": 2,
                },
                {
                    "id": "https://openalex.org/C2780993040",
                    "wikidata": "https://www.wikidata.org/wiki/Q57751738",
                    "display_name": "Coronavirus",
                    "level": 3,
                },
                {
                    "id": "https://openalex.org/C524204448",
                    "wikidata": "https://www.wikidata.org/wiki/Q84263196",
                    "display_name": "COVID-19",
                    "level": 4,
                },
            ],
            "related_concepts": [
                {
                    "id": "https://openalex.org/C2778755073",
                    "wikidata": "https://www.wikidata.org/wiki/Q88100308",
                    "display_name": "COVID-19 pandemic",
                    "level": 4,
                    "score": 9.876543,
                }
            ],
        }

    def test_comprehensive_concept_creation(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test creating a concept with all fields from comprehensive data."""
        concept = Concept(**comprehensive_concept_data)

        # Basic fields
        assert concept.id == "https://openalex.org/C121332964"
        assert concept.display_name == "Physics"
        assert str(concept.wikidata) == "https://www.wikidata.org/wiki/Q413"
        assert concept.level == 0
        assert "natural science" in concept.description

        # Metrics
        assert concept.works_count == 4567890
        assert concept.cited_by_count == 87654321

        # URLs
        assert "CollageFisica.jpg" in str(concept.image_url)
        assert "100px" in str(concept.image_thumbnail_url)

        # Helper properties
        assert concept.is_top_level is True
        assert concept.parent_concept is None

    def test_concept_summary_stats(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test concept summary statistics."""
        concept = Concept(**comprehensive_concept_data)

        assert concept.summary_stats is not None
        assert concept.summary_stats.two_year_mean_citedness == 3.456789
        assert concept.summary_stats.h_index == 543
        assert concept.summary_stats.i10_index == 234567

    def test_concept_ids(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test concept external identifiers."""
        concept = Concept(**comprehensive_concept_data)

        assert concept.ids is not None
        assert concept.ids.openalex == concept.id
        assert str(concept.ids.wikidata) == str(concept.wikidata)
        assert "wikipedia.org" in str(concept.ids.wikipedia)
        assert concept.ids.umls_aui == ["A0000001"]
        assert concept.ids.umls_cui == ["C0000001"]
        assert concept.ids.mag == "121332964"

    def test_international_display_names(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test international name translations."""
        concept = Concept(**comprehensive_concept_data)

        assert concept.international_display_name is not None
        assert len(concept.international_display_name) > 35

        # Sample translations
        assert concept.international_display_name["en"] == "physics"
        assert concept.international_display_name["de"] == "Physik"
        assert concept.international_display_name["ja"] == "物理学"
        assert concept.international_display_name["ar"] == "فيزياء"
        assert concept.international_display_name["ru"] == "физика"

    def test_related_concepts(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test related concepts with scores."""
        concept = Concept(**comprehensive_concept_data)

        assert len(concept.related_concepts) == 3

        # First related concept
        quantum = concept.related_concepts[0]
        assert quantum.display_name == "Quantum mechanics"
        assert quantum.level == 1
        assert quantum.score == 8.234567

        # Check ordering by score
        scores = [rc.score for rc in concept.related_concepts]
        assert scores == sorted(scores, reverse=True)

    def test_concept_counts_by_year(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test yearly counts."""
        concept = Concept(**comprehensive_concept_data)

        assert len(concept.counts_by_year) == 5

        recent = concept.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 234567
        assert recent.cited_by_count == 4567890

    def test_hierarchical_concept(
        self, hierarchical_concept_data: dict[str, Any]
    ) -> None:
        """Test concept with parent hierarchy."""
        concept = Concept(**hierarchical_concept_data)

        assert concept.level == 1
        assert concept.is_top_level is False

        # Ancestors
        assert len(concept.ancestors) == 1
        physics = concept.ancestors[0]
        assert physics.display_name == "Physics"
        assert physics.level == 0

        # Helper methods
        assert concept.parent_concept is not None
        assert concept.parent_concept.display_name == "Physics"
        assert concept.ancestor_names() == ["Physics"]

    def test_deep_hierarchy_concept(
        self, deep_hierarchy_concept_data: dict[str, Any]
    ) -> None:
        """Test concept with deep hierarchy (level 5)."""
        concept = Concept(**deep_hierarchy_concept_data)

        assert concept.level == 5
        assert (
            concept.display_name
            == "Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)"
        )

        # Full ancestry
        assert len(concept.ancestors) == 5

        # Check hierarchy levels
        levels = [anc.level for anc in concept.ancestors]
        assert levels == [0, 1, 2, 3, 4]

        # Parent concept
        assert concept.parent_concept.display_name == "COVID-19"
        assert concept.parent_concept.level == 4

        # Ancestor names
        names = concept.ancestor_names()
        assert "Medicine" in names
        assert "Pathology" in names
        assert "Virology" in names
        assert "Coronavirus" in names
        assert "COVID-19" in names

    def test_concept_helper_methods(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test concept helper methods."""
        concept = Concept(**comprehensive_concept_data)

        # Year-based lookups
        assert concept.works_in_year(2024) == 234567
        assert concept.citations_in_year(2023) == 4345678
        assert concept.works_in_year(2019) == 0  # Not in data

        # Active years
        active_years = concept.active_years()
        assert 2024 in active_years
        assert len(active_years) == 5

    def test_dehydrated_concept(self) -> None:
        """Test dehydrated concept model."""
        dehydrated = DehydratedConcept(
            id="https://openalex.org/C121332964",
            wikidata="https://www.wikidata.org/wiki/Q413",
            display_name="Physics",
            level=0,
            score=0.9187037,
        )

        assert dehydrated.id == "https://openalex.org/C121332964"
        assert dehydrated.display_name == "Physics"
        assert dehydrated.score == 0.9187037

    def test_minimal_concept(self) -> None:
        """Test concept with minimal data."""
        concept = Concept(id="C123", display_name="Test Concept", level=0)

        assert concept.wikidata is None
        assert concept.description is None
        assert len(concept.ancestors) == 0
        assert concept.is_top_level is True
        assert concept.parent_concept is None

    def test_concept_validation_errors(self) -> None:
        """Test validation errors for invalid concept data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Concept()

        # Invalid level
        with pytest.raises(ValidationError):
            Concept(id="C123", display_name="Test", level=-1)

        # Invalid level (too high)
        with pytest.raises(ValidationError):
            Concept(
                id="C123",
                display_name="Test",
                level=6,  # Max is 5
            )

    def test_concept_edge_cases(self) -> None:
        """Test edge cases in concept data."""
        # Concept with empty lists
        concept = Concept(
            id="C456",
            display_name="Empty Concept",
            level=2,
            ancestors=[],
            related_concepts=[],
            counts_by_year=[],
        )

        assert concept.parent_concept is None  # No ancestors despite level 2
        assert concept.ancestor_names() == []
        assert concept.active_years() == []

        # Concept with circular reference (shouldn't happen but test handling)
        concept_circular = Concept(
            id="C789",
            display_name="Circular",
            level=1,
            ancestors=[
                {
                    "id": "C789",
                    "wikidata": "https://www.wikidata.org/wiki/Q999",
                    "display_name": "Circular",
                    "level": 1,
                }
            ],
        )
        assert len(concept_circular.ancestors) == 1

    def test_concept_score_ordering(
        self, hierarchical_concept_data: dict[str, Any]
    ) -> None:
        """Test that related concepts maintain score ordering."""
        concept = Concept(**hierarchical_concept_data)

        # Verify scores are in descending order
        for i in range(len(concept.related_concepts) - 1):
            assert (
                concept.related_concepts[i].score
                >= concept.related_concepts[i + 1].score
            )

    def test_datetime_fields(
        self, comprehensive_concept_data: dict[str, Any]
    ) -> None:
        """Test datetime field parsing."""
        concept = Concept(**comprehensive_concept_data)

        assert isinstance(concept.created_date, str)
        assert concept.created_date == "2016-06-24"

        assert isinstance(concept.updated_date, datetime)
        assert concept.updated_date.year == 2024
