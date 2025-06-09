from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    DehydratedTopic,
    Topic,
    TopicHierarchy,
    TopicLevel,
)


class TestTopic:
    """Test Topic model with comprehensive realistic fixtures."""

    @pytest.fixture
    def domain_topic_data(self) -> dict[str, Any]:
        """Domain-level topic data (level 0)."""
        return {
            "id": "https://openalex.org/T10001",
            "display_name": "Physical Sciences",
            "description": "Physical sciences encompass the branches of natural science that study non-living systems, including physics, chemistry, astronomy, and earth sciences.",
            "keywords": [
                "physics",
                "chemistry",
                "astronomy",
                "earth sciences",
                "materials science",
            ],
            "ids": {
                "openalex": "https://openalex.org/T10001",
                "wikipedia": "https://en.wikipedia.org/wiki/Physical_science",
            },
            "subfield": None,
            "field": None,
            "domain": {
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
            "siblings": [
                {
                    "id": "https://openalex.org/T10002",
                    "display_name": "Life Sciences",
                },
                {
                    "id": "https://openalex.org/T10003",
                    "display_name": "Health Sciences",
                },
                {
                    "id": "https://openalex.org/T10004",
                    "display_name": "Social Sciences",
                },
            ],
            "works_count": 12345678,
            "cited_by_count": 234567890,
            "updated_date": "2024-12-16T14:56:78.901234",
        }

    @pytest.fixture
    def field_topic_data(self) -> dict[str, Any]:
        """Field-level topic data (level 1)."""
        return {
            "id": "https://openalex.org/T10018",
            "display_name": "Chemistry",
            "description": "Chemistry is the scientific study of the properties and behavior of matter.",
            "keywords": [
                "organic chemistry",
                "inorganic chemistry",
                "physical chemistry",
                "analytical chemistry",
                "biochemistry",
            ],
            "ids": {
                "openalex": "https://openalex.org/T10018",
                "wikipedia": "https://en.wikipedia.org/wiki/Chemistry",
            },
            "subfield": None,
            "field": {
                "id": "https://openalex.org/fields/16",
                "display_name": "Chemistry",
            },
            "domain": {
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
            "siblings": [
                {
                    "id": "https://openalex.org/T10019",
                    "display_name": "Physics",
                },
                {
                    "id": "https://openalex.org/T10020",
                    "display_name": "Materials Science",
                },
            ],
            "works_count": 3456789,
            "cited_by_count": 67890123,
        }

    @pytest.fixture
    def subfield_topic_data(self) -> dict[str, Any]:
        """Subfield-level topic data (level 2) - most detailed level."""
        return {
            "id": "https://openalex.org/T10555",
            "display_name": "Density Functional Theory and Molecular Dynamics",
            "description": "This topic covers computational methods in quantum chemistry including density functional theory (DFT) and molecular dynamics simulations for studying molecular systems.",
            "keywords": [
                "density functional theory",
                "DFT",
                "molecular dynamics",
                "ab initio",
                "quantum chemistry",
                "computational chemistry",
                "electronic structure",
            ],
            "ids": {
                "openalex": "https://openalex.org/T10555",
                "wikipedia": "https://en.wikipedia.org/wiki/Density_functional_theory",
            },
            "subfield": {
                "id": "https://openalex.org/subfields/1606",
                "display_name": "Physical and Theoretical Chemistry",
            },
            "field": {
                "id": "https://openalex.org/fields/16",
                "display_name": "Chemistry",
            },
            "domain": {
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
            "siblings": [
                {
                    "id": "https://openalex.org/T10556",
                    "display_name": "Molecular Spectroscopy",
                },
                {
                    "id": "https://openalex.org/T10557",
                    "display_name": "Chemical Kinetics and Dynamics",
                },
                {
                    "id": "https://openalex.org/T10558",
                    "display_name": "Quantum Chemistry Methods",
                },
            ],
            "works_count": 234567,
            "cited_by_count": 5678901,
            "updated_date": "2024-12-16T15:12:34.567890",
        }

    @pytest.fixture
    def interdisciplinary_topic_data(self) -> dict[str, Any]:
        """Interdisciplinary topic spanning multiple domains."""
        return {
            "id": "https://openalex.org/T11234",
            "display_name": "Machine Learning in Scientific Computing",
            "description": "Application of machine learning and artificial intelligence methods to scientific computing problems.",
            "keywords": [
                "machine learning",
                "scientific computing",
                "neural networks",
                "physics-informed neural networks",
                "scientific machine learning",
            ],
            "ids": {"openalex": "https://openalex.org/T11234"},
            "subfield": {
                "id": "https://openalex.org/subfields/1703",
                "display_name": "Computational Theory and Mathematics",
            },
            "field": {
                "id": "https://openalex.org/fields/17",
                "display_name": "Computer Science",
            },
            "domain": {
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
            "siblings": [],
            "works_count": 45678,
            "cited_by_count": 890123,
        }

    def test_domain_topic_creation(
        self, domain_topic_data: dict[str, Any]
    ) -> None:
        """Test creating a domain-level topic."""
        topic = Topic(**domain_topic_data)

        # Basic fields
        assert topic.id == "https://openalex.org/T10001"
        assert topic.display_name == "Physical Sciences"
        assert "natural science" in topic.description

        # Keywords
        assert len(topic.keywords) == 5
        assert "physics" in topic.keywords
        assert "chemistry" in topic.keywords

        # Hierarchy
        assert topic.subfield is None
        assert topic.field is None
        assert topic.domain is not None
        assert topic.domain.display_name == "Physical Sciences"

        # Level property
        assert topic.level == TopicLevel.DOMAIN

        # Metrics
        assert topic.works_count == 12345678
        assert topic.cited_by_count == 234567890

    def test_field_topic_creation(
        self, field_topic_data: dict[str, Any]
    ) -> None:
        """Test creating a field-level topic."""
        topic = Topic(**field_topic_data)

        assert topic.display_name == "Chemistry"

        # Hierarchy
        assert topic.subfield is None
        assert topic.field is not None
        assert topic.field.display_name == "Chemistry"
        assert topic.domain.display_name == "Physical Sciences"

        # Level property
        assert topic.level == TopicLevel.FIELD

        # Keywords
        assert "organic chemistry" in topic.keywords
        assert "biochemistry" in topic.keywords

    def test_subfield_topic_creation(
        self, subfield_topic_data: dict[str, Any]
    ) -> None:
        """Test creating a subfield-level topic."""
        topic = Topic(**subfield_topic_data)

        assert (
            topic.display_name
            == "Density Functional Theory and Molecular Dynamics"
        )

        # Full hierarchy
        assert topic.subfield is not None
        assert (
            topic.subfield.display_name == "Physical and Theoretical Chemistry"
        )
        assert topic.field.display_name == "Chemistry"
        assert topic.domain.display_name == "Physical Sciences"

        # Level property
        assert topic.level == TopicLevel.SUBFIELD

        # Keywords
        assert len(topic.keywords) == 7
        assert "density functional theory" in topic.keywords
        assert "DFT" in topic.keywords
        assert "molecular dynamics" in topic.keywords

    def test_topic_siblings(self, field_topic_data: dict[str, Any]) -> None:
        """Test topic siblings."""
        topic = Topic(**field_topic_data)

        assert len(topic.siblings) == 2

        # First sibling
        physics = topic.siblings[0]
        assert physics.display_name == "Physics"

        # Check all siblings are at same level
        materials = topic.siblings[1]
        assert materials.display_name == "Materials Science"

    def test_topic_ids(self, subfield_topic_data: dict[str, Any]) -> None:
        """Test topic external identifiers."""
        topic = Topic(**subfield_topic_data)

        assert topic.ids is not None
        assert topic.ids.openalex == topic.id
        assert "wikipedia.org" in str(topic.ids.wikipedia)

    def test_interdisciplinary_topic(
        self, interdisciplinary_topic_data: dict[str, Any]
    ) -> None:
        """Test interdisciplinary topic."""
        topic = Topic(**interdisciplinary_topic_data)

        assert "Machine Learning" in topic.display_name
        assert topic.field.display_name == "Computer Science"
        assert topic.domain.display_name == "Physical Sciences"

        # No siblings for specialized topics
        assert len(topic.siblings) == 0

    def test_topic_helper_methods(
        self, subfield_topic_data: dict[str, Any]
    ) -> None:
        """Test topic helper methods."""
        topic = Topic(**subfield_topic_data)

        # Has keyword
        assert topic.has_keyword("DFT") is True
        assert (
            topic.has_keyword("density functional") is True
        )  # Case insensitive
        assert topic.has_keyword("unrelated") is False

        # Get hierarchy
        hierarchy = topic.get_hierarchy()
        assert hierarchy["domain"] == "Physical Sciences"
        assert hierarchy["field"] == "Chemistry"
        assert hierarchy["subfield"] == "Physical and Theoretical Chemistry"

    def test_dehydrated_topic(self) -> None:
        """Test dehydrated topic model."""
        dehydrated = DehydratedTopic(
            id="https://openalex.org/T10555",
            display_name="Density Functional Theory and Molecular Dynamics",
            score=0.9876,
            subfield={
                "id": "https://openalex.org/subfields/1606",
                "display_name": "Physical and Theoretical Chemistry",
            },
            field={
                "id": "https://openalex.org/fields/16",
                "display_name": "Chemistry",
            },
            domain={
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
        )

        assert dehydrated.score == 0.9876
        assert (
            dehydrated.subfield.display_name
            == "Physical and Theoretical Chemistry"
        )

    def test_minimal_topic(self) -> None:
        """Test topic with minimal data."""
        topic = Topic(id="T123", display_name="Test Topic")

        assert topic.description is None
        assert len(topic.keywords) == 0
        assert topic.subfield is None
        assert topic.level == TopicLevel.DOMAIN  # Default when no hierarchy

    def test_topic_validation_errors(self) -> None:
        """Test validation errors for invalid topic data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Topic()

        # Invalid hierarchy (subfield without field)
        with pytest.raises(ValidationError):
            Topic(
                id="T123",
                display_name="Test",
                subfield={"id": "S123", "display_name": "Subfield"},
                # Missing field
            )

    def test_topic_edge_cases(self) -> None:
        """Test edge cases in topic data."""
        # Topic with empty lists
        topic = Topic(
            id="T456", display_name="Empty Topic", keywords=[], siblings=[]
        )

        assert topic.has_keyword("anything") is False

        # Topic with only domain
        domain_only = Topic(
            id="T789",
            display_name="Domain Only",
            domain={"id": "D1", "display_name": "Test Domain"},
        )
        assert domain_only.level == TopicLevel.DOMAIN
        assert domain_only.get_hierarchy() == {
            "domain": "Test Domain",
            "field": None,
            "subfield": None,
        }

    def test_topic_keyword_matching(self) -> None:
        """Test keyword matching functionality."""
        topic = Topic(
            id="T999",
            display_name="Test Topic",
            keywords=[
                "Machine Learning",
                "Deep Learning",
                "Neural Networks",
                "AI",
                "Artificial Intelligence",
            ],
        )

        # Case insensitive matching
        assert topic.has_keyword("machine learning") is True
        assert topic.has_keyword("DEEP LEARNING") is True
        assert topic.has_keyword("ai") is True

        # Partial matching
        assert topic.has_keyword("machine") is True
        assert topic.has_keyword("learning") is True
        assert topic.has_keyword("neural") is True

        # Non-matching
        assert topic.has_keyword("quantum") is False

    def test_datetime_fields(self, domain_topic_data: dict[str, Any]) -> None:
        """Test datetime field parsing."""
        topic = Topic(**domain_topic_data)

        assert isinstance(topic.updated_date, datetime)
        assert topic.updated_date.year == 2024

    def test_parse_updated_date_malformed(self) -> None:
        """Seconds above 59 are clamped."""
        topic = Topic(
            id="T1",
            display_name="Topic",
            updated_date="2024-12-31T23:59:70Z",
        )
        assert isinstance(topic.updated_date, datetime)
        assert topic.updated_date.second == 59

    def test_hierarchy_path_and_level(self) -> None:
        """Hierarchy helpers work with all levels."""
        domain = TopicHierarchy(id="D1", display_name="Domain")
        field = TopicHierarchy(id="F1", display_name="Field")
        sub = TopicHierarchy(id="S1", display_name="Sub")
        topic = Topic(
            id="T2",
            display_name="Name",
            domain=domain,
            field=field,
            subfield=sub,
        )
        assert topic.hierarchy_path == "Domain > Field > Sub"
        assert topic.level.name == "SUBFIELD"

    def test_parse_updated_date_regex_branch(self) -> None:
        """Malformed datetime handled via regex."""
        topic = Topic(
            id="T3",
            display_name="Topic",
            updated_date="2024-12-31T12:34:61BAD",
        )
        assert isinstance(topic.updated_date, datetime)
        assert topic.updated_date.second == 59

    def test_parse_updated_date_none_and_invalid(self) -> None:
        """None or invalid updated_date returns None."""
        t_none = Topic(id="T4", display_name="t", updated_date=None)
        assert t_none.updated_date is None
        t_bad = Topic(id="T5", display_name="t", updated_date="bad")
        assert t_bad.updated_date is None
