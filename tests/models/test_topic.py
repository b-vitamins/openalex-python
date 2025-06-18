"""
Comprehensive tests for the Topic model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestTopicModel:
    """Test suite for Topic model with real OpenAlex data structure."""

    def test_topic_basic_fields(self, mock_topic_data):
        """Test basic topic fields from fixture."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # Basic identifiers
        assert topic.id == "https://openalex.org/T11636"
        assert (
            topic.display_name
            == "Artificial Intelligence in Healthcare and Education"
        )

        # Description
        expected_desc = "This cluster of papers explores the intersection of artificial intelligence and medicine"
        assert topic.description.startswith(expected_desc)

        # Keywords
        expected_keywords = [
            "Artificial Intelligence",
            "Machine Learning",
            "Healthcare",
            "Medical Imaging",
            "Clinical Decision Support",
            "Ethical Challenges",
            "Big Data",
            "Precision Medicine",
            "Radiology",
            "Health Equity",
        ]
        assert topic.keywords == expected_keywords

        # Metrics
        assert topic.works_count == 42251
        assert topic.cited_by_count == 468006

    def test_topic_ids_structure(self, mock_topic_data):
        """Test the IDs nested structure."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        assert topic.ids.openalex == "https://openalex.org/T11636"
        assert (
            topic.ids.wikipedia
            == "https://en.wikipedia.org/wiki/Artificial_intelligence_in_healthcare"
        )

    def test_topic_hierarchy(self, mock_topic_data):
        """Test topic hierarchy - subfield, field, domain."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # Subfield
        assert topic.subfield.id == "https://openalex.org/subfields/2718"
        assert topic.subfield.display_name == "Health Informatics"

        # Field
        assert topic.field.id == "https://openalex.org/fields/27"
        assert topic.field.display_name == "Medicine"

        # Domain
        assert topic.domain.id == "https://openalex.org/domains/4"
        assert topic.domain.display_name == "Health Sciences"

    def test_topic_siblings(self, mock_topic_data):
        """Test sibling topics."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # This topic has no siblings in the fixture
        assert topic.siblings == []

    def test_topic_updated_date(self, mock_topic_data):
        """Test updated date field."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)
        assert topic.updated_date == date(2025, 6, 9)

    def test_topic_created_date(self, mock_topic_data):
        """Test created date field."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)
        assert topic.created_date == date(2024, 1, 23)

    def test_topic_minimal_data(self):
        """Test topic with minimal required fields."""
        from openalex.models import Topic

        minimal_topic = Topic(
            id="https://openalex.org/T123456", display_name="Test Topic"
        )

        assert minimal_topic.id == "https://openalex.org/T123456"
        assert minimal_topic.display_name == "Test Topic"
        assert minimal_topic.description is None
        assert minimal_topic.keywords == []
        assert minimal_topic.works_count == 0
        assert minimal_topic.cited_by_count == 0

    def test_topic_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Topic

        # Missing required fields
        with pytest.raises(ValidationError):
            Topic()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Topic(id="not-a-url", display_name="Test")

    def test_topic_with_siblings(self):
        """Test topic with sibling topics."""
        from openalex.models import Topic

        topic_data = {
            "id": "https://openalex.org/T123",
            "display_name": "Machine Learning",
            "subfield": {
                "id": "https://openalex.org/S1",
                "display_name": "Artificial Intelligence",
            },
            "field": {
                "id": "https://openalex.org/F1",
                "display_name": "Computer Science",
            },
            "domain": {
                "id": "https://openalex.org/D1",
                "display_name": "Physical Sciences",
            },
            "siblings": [
                {
                    "id": "https://openalex.org/T124",
                    "display_name": "Deep Learning",
                },
                {
                    "id": "https://openalex.org/T125",
                    "display_name": "Neural Networks",
                },
            ],
        }

        topic = Topic(**topic_data)

        assert len(topic.siblings) == 2
        sibling_names = [s.display_name for s in topic.siblings]
        assert "Deep Learning" in sibling_names
        assert "Neural Networks" in sibling_names

    def test_interdisciplinary_topic(self):
        """Test interdisciplinary topic spanning multiple fields."""
        from openalex.models import Topic

        topic_data = {
            "id": "https://openalex.org/T456",
            "display_name": "Bioinformatics",
            "description": "Computational approaches to biological data",
            "keywords": ["Genomics", "Computational Biology", "Data Analysis"],
            "subfield": {
                "id": "https://openalex.org/S2",
                "display_name": "Computational Biology",
            },
            "field": {
                "id": "https://openalex.org/F2",
                "display_name": "Biology",
            },
            "domain": {
                "id": "https://openalex.org/D2",
                "display_name": "Life Sciences",
            },
            "works_count": 75000,
            "cited_by_count": 1500000,
        }

        topic = Topic(**topic_data)

        assert "Bioinformatics" in topic.display_name
        assert "Computational" in topic.subfield.display_name
        assert topic.domain.display_name == "Life Sciences"

    def test_emerging_topic(self):
        """Test newly emerging research topic."""
        from openalex.models import Topic

        topic_data = {
            "id": "https://openalex.org/T789",
            "display_name": "Large Language Models",
            "description": "Research on transformer-based language models",
            "keywords": ["GPT", "BERT", "Transformers", "NLP"],
            "works_count": 5000,  # Relatively few works
            "cited_by_count": 100000,  # High citation rate
            "created_date": "2023-01-01",  # Recent creation
            "subfield": {
                "id": "https://openalex.org/S3",
                "display_name": "Natural Language Processing",
            },
            "field": {
                "id": "https://openalex.org/F1",
                "display_name": "Computer Science",
            },
            "domain": {
                "id": "https://openalex.org/D1",
                "display_name": "Physical Sciences",
            },
        }

        topic = Topic(**topic_data)

        # High citation-to-work ratio indicates hot topic
        citation_ratio = topic.cited_by_count / topic.works_count
        assert citation_ratio > 10

        # Recent creation date
        assert topic.created_date >= date(2023, 1, 1)

    def test_established_topic(self, mock_topic_data):
        """Test well-established research topic."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # AI in Healthcare is established
        assert topic.works_count > 40000
        assert topic.cited_by_count > 400000
        assert len(topic.keywords) >= 10  # Rich keyword set

    def test_topic_keyword_analysis(self, mock_topic_data):
        """Test keyword patterns in topics."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # Check for expected keyword themes
        ai_keywords = [
            k for k in topic.keywords if "Intelligence" in k or "Learning" in k
        ]
        assert len(ai_keywords) >= 2

        healthcare_keywords = [
            k
            for k in topic.keywords
            if "Health" in k or "Medical" in k or "Medicine" in k
        ]
        assert len(healthcare_keywords) >= 3

    def test_topic_hierarchy_consistency(self, mock_topic_data):
        """Test consistency in topic hierarchy."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # Health Informatics should be under Medicine
        assert topic.subfield.display_name == "Health Informatics"
        assert topic.field.display_name == "Medicine"
        assert topic.domain.display_name == "Health Sciences"

        # Hierarchy makes sense
        assert "Health" in topic.subfield.display_name
        assert topic.field.display_name in ["Medicine", "Health"]

    def test_topic_complete_profile(self, mock_topic_data):
        """Test complete topic profile with all fields populated."""
        from openalex.models import Topic

        topic = Topic(**mock_topic_data)

        # Verify all major sections are populated
        assert topic.id is not None
        assert topic.display_name is not None
        assert topic.description is not None
        assert len(topic.keywords) > 0
        assert topic.works_count > 0
        assert topic.cited_by_count > 0
        assert topic.subfield is not None
        assert topic.field is not None
        assert topic.domain is not None
        assert topic.ids is not None
        assert topic.created_date is not None
        assert topic.updated_date is not None

    def test_topic_siblings_and_subfield_parsing(self):
        """Test Topic model parses related entities correctly."""
        from openalex.models import Topic

        topic_data = {
            "id": "https://openalex.org/T10001",
            "display_name": "Climate Change",
            "subfield": {
                "id": "https://openalex.org/subfields/2306",
                "display_name": "Global and Planetary Change",
            },
            "field": {
                "id": "https://openalex.org/fields/23",
                "display_name": "Environmental Science",
            },
            "domain": {
                "id": "https://openalex.org/domains/3",
                "display_name": "Physical Sciences",
            },
            "siblings": [
                {
                    "id": "https://openalex.org/T10002",
                    "display_name": "Global Warming",
                },
                {
                    "id": "https://openalex.org/T10003",
                    "display_name": "Carbon Cycle",
                },
            ],
            "works_count": 250000,
            "cited_by_count": 5000000,
            "keywords": [
                {
                    "id": "https://openalex.org/keywords/climate-change",
                    "display_name": "climate change",
                    "score": 0.95,
                }
            ],
        }

        topic = Topic(**topic_data)

        assert topic.subfield.display_name == "Global and Planetary Change"
        assert topic.field.display_name == "Environmental Science"
        assert topic.domain.display_name == "Physical Sciences"
        assert len(topic.siblings) == 2
        assert all(hasattr(s, "display_name") for s in topic.siblings)
        assert topic.siblings[0].display_name == "Global Warming"
        assert len(topic.keywords) == 1
        assert topic.keywords[0].score == 0.95
        assert topic.openalex_id == "T10001"

        minimal_topic = Topic(
            id="https://openalex.org/T20001",
            display_name="Minimal Topic",
        )
        assert minimal_topic.siblings == []
        assert minimal_topic.subfield is None
        assert minimal_topic.keywords == []
