"""
Comprehensive tests for the Author model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestAuthorModel:
    """Test suite for Author model with real OpenAlex data structure."""

    def test_author_basic_fields(self, mock_author_data):
        """Test basic author fields from fixture."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        # Basic identifiers
        assert author.id == "https://openalex.org/A5023888391"
        assert author.orcid == "https://orcid.org/0000-0001-6187-6610"
        assert author.display_name == "Jason Priem"
        assert author.display_name_alternatives == [
            "Priem Jason",
            "Jason Priem",
        ]

        # Metrics
        assert author.works_count == 62
        assert author.cited_by_count == 3886

    def test_author_summary_stats(self, mock_author_data):
        """Test summary statistics."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert author.summary_stats is not None
        assert author.summary_stats.two_year_mean_citedness == 6.0
        assert author.summary_stats.h_index == 17
        assert author.summary_stats.i10_index == 20

        # Test convenience properties
        assert author.h_index == 17
        assert author.i10_index == 20

    def test_author_ids_structure(self, mock_author_data):
        """Test the IDs nested structure."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert author.ids.openalex == "https://openalex.org/A5023888391"
        assert author.ids.orcid == "https://orcid.org/0000-0001-6187-6610"
        assert (
            author.ids.scopus
            == "http://www.scopus.com/inward/authorDetails.url?authorID=36455008000&partnerID=MN8TOARS"
        )

    def test_author_affiliations(self, mock_author_data):
        """Test affiliations structure with years."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.affiliations) == 8

        # Current affiliation
        current_aff = author.affiliations[0]
        assert current_aff.institution.id == "https://openalex.org/I4200000001"
        assert current_aff.institution.display_name == "OurResearch"
        assert current_aff.institution.country_code == "CA"
        assert current_aff.institution.type == "nonprofit"
        assert current_aff.years == [2023, 2022, 2021, 2019]

        # Check historical affiliations
        unc_aff = next(
            a
            for a in author.affiliations
            if a.institution.id == "https://openalex.org/I114027177"
        )
        assert (
            unc_aff.institution.display_name
            == "University of North Carolina at Chapel Hill"
        )
        assert unc_aff.years == [2014, 2013, 2012, 2011, 2010]

    def test_author_last_known_institutions(self, mock_author_data):
        """Test last known institution fields."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        # List of last known institutions
        assert len(author.last_known_institutions) == 1
        assert (
            author.last_known_institutions[0].id
            == "https://openalex.org/I4200000001"
        )
        assert author.last_known_institutions[0].display_name == "OurResearch"
        assert author.last_known_institutions[0].country_code == "CA"
        assert author.last_known_institutions[0].type == "nonprofit"

        # Note: last_known_institution (singular) might not be in the data
        # but should be derived from last_known_institutions[0] if implemented

    def test_author_topics(self, mock_author_data):
        """Test author research topics."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.topics) == 25

        # Primary topic
        primary_topic = author.topics[0]
        assert primary_topic.id == "https://openalex.org/T10102"
        assert (
            primary_topic.display_name
            == "scientometrics and bibliometrics research"
        )
        assert primary_topic.count == 23
        assert (
            primary_topic.subfield.display_name
            == "Statistics, Probability and Uncertainty"
        )
        assert primary_topic.field.display_name == "Decision Sciences"
        assert primary_topic.domain.display_name == "Social Sciences"

        # Check other significant topics
        topic_names = [t.display_name for t in author.topics[:5]]
        assert "scientometrics and bibliometrics research" in topic_names
        assert "Research Data Management Practices" in topic_names
        assert "Wikis in Education and Collaboration" in topic_names

    def test_author_topic_share(self, mock_author_data):
        """Test topic share percentages."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.topic_share) == 25

        # Top topic share
        top_share = author.topic_share[0]
        assert top_share.id == "https://openalex.org/T13976"
        assert top_share.display_name == "Web visibility and informetrics"
        assert top_share.value == 0.0003116
        assert top_share.subfield.display_name == "Information Systems"

    def test_author_x_concepts(self, mock_author_data):
        """Test x_concepts legacy field."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.x_concepts) == 19

        # Top concept
        cs_concept = author.x_concepts[0]
        assert cs_concept.id == "https://openalex.org/C41008148"
        assert cs_concept.display_name == "Computer science"
        assert cs_concept.level == 0
        assert cs_concept.score == 95.2

    def test_author_counts_by_year(self, mock_author_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.counts_by_year) == 13

        # Most recent year
        recent = author.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 0
        assert recent.cited_by_count == 78

        # Year with publications
        year_2023 = next(c for c in author.counts_by_year if c.year == 2023)
        assert year_2023.works_count == 6
        assert year_2023.cited_by_count == 317

        # Verify descending order
        years = [c.year for c in author.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_author_works_api_url(self, mock_author_data):
        """Test works API URL."""
        from openalex.models import Author

        author = Author(**mock_author_data)
        assert (
            author.works_api_url
            == "https://api.openalex.org/works?filter=author.id:A5023888391"
        )

    def test_author_updated_date(self, mock_author_data):
        """Test updated date field."""
        from openalex.models import Author

        author = Author(**mock_author_data)
        assert author.updated_date == date(2025, 5, 28)

    def test_author_created_date(self, mock_author_data):
        """Test created date field."""
        from openalex.models import Author

        author = Author(**mock_author_data)
        assert author.created_date == date(2023, 7, 21)

    def test_author_minimal_data(self):
        """Test author with minimal required fields."""
        from openalex.models import Author

        minimal_author = Author(
            id="https://openalex.org/A123456", display_name="Test Author"
        )

        assert minimal_author.id == "https://openalex.org/A123456"
        assert minimal_author.display_name == "Test Author"
        assert minimal_author.orcid is None
        assert minimal_author.works_count == 0
        assert minimal_author.cited_by_count == 0
        assert len(minimal_author.affiliations) == 0

    def test_author_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Author

        # Missing required fields
        with pytest.raises(ValidationError):
            Author()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Author(id="not-a-url", display_name="Test")

        # Invalid ORCID format
        with pytest.raises(ValidationError):
            Author(
                id="https://openalex.org/A123",
                display_name="Test",
                orcid="invalid-orcid",
            )

    def test_author_with_multiple_affiliations(self):
        """Test author with complex affiliation history."""
        from openalex.models import Author

        author_data = {
            "id": "https://openalex.org/A123",
            "display_name": "Marie Curie",
            "affiliations": [
                {
                    "institution": {
                        "id": "https://openalex.org/I1",
                        "display_name": "Sorbonne University",
                        "country_code": "FR",
                        "type": "education",
                    },
                    "years": [1934, 1933, 1932],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I2",
                        "display_name": "Radium Institute",
                        "country_code": "FR",
                        "type": "facility",
                    },
                    "years": [1934, 1933, 1932, 1931, 1930],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I3",
                        "display_name": "University of Paris",
                        "country_code": "FR",
                        "type": "education",
                    },
                    "years": [1906, 1905, 1904, 1903],
                },
            ],
            "last_known_institutions": [
                {
                    "id": "https://openalex.org/I1",
                    "display_name": "Sorbonne University",
                    "country_code": "FR",
                    "type": "education",
                },
                {
                    "id": "https://openalex.org/I2",
                    "display_name": "Radium Institute",
                    "country_code": "FR",
                    "type": "facility",
                },
            ],
        }

        author = Author(**author_data)

        # Check multiple current affiliations
        assert len(author.last_known_institutions) == 2
        institution_names = [
            inst.display_name for inst in author.last_known_institutions
        ]
        assert "Sorbonne University" in institution_names
        assert "Radium Institute" in institution_names

        # Check year ranges
        radium_years = author.affiliations[1].years
        assert 1934 in radium_years
        assert 1930 in radium_years

    def test_author_without_orcid(self):
        """Test author without ORCID."""
        from openalex.models import Author

        author_data = {
            "id": "https://openalex.org/A456",
            "display_name": "Anonymous Researcher",
            "ids": {
                "openalex": "https://openalex.org/A456",
                "scopus": "http://www.scopus.com/inward/authorDetails.url?authorID=123",
            },
        }

        author = Author(**author_data)
        assert author.orcid is None
        assert author.ids.orcid is None
        assert author.ids.scopus is not None

    def test_author_name_alternatives(self, mock_author_data):
        """Test display name alternatives."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        assert len(author.display_name_alternatives) == 2
        assert "Jason Priem" in author.display_name_alternatives
        assert "Priem Jason" in author.display_name_alternatives

    def test_author_research_interests(self):
        """Test author with detailed research interests through topics."""
        from openalex.models import Author

        author_data = {
            "id": "https://openalex.org/A789",
            "display_name": "AI Researcher",
            "topics": [
                {
                    "id": "https://openalex.org/T1",
                    "display_name": "Machine Learning",
                    "count": 50,
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
                },
                {
                    "id": "https://openalex.org/T2",
                    "display_name": "Neural Networks",
                    "count": 30,
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
                },
            ],
        }

        author = Author(**author_data)

        # Verify research focus
        assert author.topics[0].count > author.topics[1].count
        assert all(
            t.field.display_name == "Computer Science" for t in author.topics
        )

    def test_author_metrics_edge_cases(self):
        """Test author with zero or missing metrics."""
        from openalex.models import Author

        author_data = {
            "id": "https://openalex.org/A999",
            "display_name": "New Researcher",
            "works_count": 0,
            "cited_by_count": 0,
            "summary_stats": {
                "2yr_mean_citedness": 0.0,
                "h_index": 0,
                "i10_index": 0,
            },
        }

        author = Author(**author_data)

        assert author.works_count == 0
        assert author.cited_by_count == 0
        assert author.h_index == 0
        assert author.i10_index == 0
        assert author.summary_stats.two_year_mean_citedness == 0.0

    def test_author_complete_profile(self, mock_author_data):
        """Test complete author profile with all fields populated."""
        from openalex.models import Author

        author = Author(**mock_author_data)

        # Verify all major sections are populated
        assert author.id is not None
        assert author.display_name is not None
        assert author.works_count > 0
        assert author.cited_by_count > 0
        assert len(author.affiliations) > 0
        assert len(author.topics) > 0
        assert len(author.counts_by_year) > 0
        assert author.summary_stats is not None
        assert author.ids is not None
        assert author.last_known_institutions is not None
