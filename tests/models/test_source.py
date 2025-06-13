"""
Comprehensive tests for the Source/Source model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestSourceModel:
    """Test suite for Source/Source model with real OpenAlex data structure."""

    def test_source_basic_fields(self, mock_source_data):
        """Test basic source fields from fixture."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        # Basic identifiers
        assert source.id == "https://openalex.org/S137773608"
        assert source.issn_l == "0028-0836"
        assert source.issn == ["0028-0836", "1476-4687"]
        assert source.display_name == "Nature"
        assert source.type == "journal"

        # Publisher information
        assert source.host_organization == "https://openalex.org/P4310319908"
        assert source.host_organization_name == "Nature Portfolio"
        assert source.host_organization_lineage == [
            "https://openalex.org/P4310319908",
            "https://openalex.org/P4310319965",
        ]

        # Metrics
        assert source.works_count == 431710
        assert source.cited_by_count == 25258309

    def test_source_summary_stats(self, mock_source_data):
        """Test summary statistics."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert source.summary_stats is not None
        assert source.summary_stats.two_year_mean_citedness == 16.2611434684417
        assert source.summary_stats.h_index == 1779
        assert source.summary_stats.i10_index == 117589

        # Test convenience properties
        assert source.h_index == 1779
        assert source.i10_index == 117589

    def test_source_open_access_status(self, mock_source_data):
        """Test open access fields."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert source.is_oa is False
        assert source.is_in_doaj is False

    def test_source_indexing(self, mock_source_data):
        """Test indexing information."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert source.is_indexed_in_scopus is True
        assert source.is_core is True

    def test_source_ids_structure(self, mock_source_data):
        """Test the IDs nested structure."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert source.ids.openalex == "https://openalex.org/S137773608"
        assert source.ids.issn_l == "0028-0836"
        assert source.ids.issn == ["0028-0836", "1476-4687"]
        assert source.ids.mag == "137773608"
        assert source.ids.wikidata == "https://www.wikidata.org/entity/Q180445"

    def test_source_homepage_url(self, mock_source_data):
        """Test homepage URL."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.homepage_url == "https://www.nature.com/nature/"

    def test_source_apc_prices(self, mock_source_data):
        """Test article processing charges."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert len(source.apc_prices) == 3

        # Check different currencies
        price_dict = {p.currency: p for p in source.apc_prices}

        assert price_dict["EUR"].price == 9750
        assert price_dict["USD"].price == 11690
        assert price_dict["GBP"].price == 8490

        assert source.apc_usd == 11690

    def test_source_country_code(self, mock_source_data):
        """Test country code."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.country_code == "GB"

    def test_source_societies(self, mock_source_data):
        """Test affiliated societies."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.societies == []

    def test_source_alternate_titles(self, mock_source_data):
        """Test alternate titles."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.alternate_titles == []

    def test_source_abbreviated_title(self, mock_source_data):
        """Test abbreviated title."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.abbreviated_title is None

    def test_source_topics(self, mock_source_data):
        """Test source topics."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert len(source.topics) == 25

        # Top topic
        top_topic = source.topics[0]
        assert top_topic.id == "https://openalex.org/T13656"
        assert top_topic.display_name == "Science, Research, and Medicine"
        assert top_topic.count == 12534
        assert top_topic.subfield.display_name == "Reproductive Medicine"
        assert top_topic.field.display_name == "Medicine"
        assert top_topic.domain.display_name == "Health Sciences"

        # Nature publishes diverse topics
        topic_names = [t.display_name for t in source.topics[:5]]
        assert "Science, Research, and Medicine" in topic_names
        assert "History and Developments in Astronomy" in topic_names
        assert "Astro and Planetary Science" in topic_names

    def test_source_topic_share(self, mock_source_data):
        """Test topic share percentages."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert len(source.topic_share) == 25

        # Top topic share
        top_share = source.topic_share[0]
        assert top_share.id == "https://openalex.org/T13656"
        assert top_share.display_name == "Science, Research, and Medicine"
        assert top_share.value == 0.0869209

    def test_source_x_concepts(self, mock_source_data):
        """Test x_concepts legacy field."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert len(source.x_concepts) == 14

        # Top concept
        biology_concept = source.x_concepts[0]
        assert biology_concept.id == "https://openalex.org/C86803240"
        assert biology_concept.display_name == "Biology"
        assert biology_concept.level == 0
        assert biology_concept.score == 58.1

    def test_source_counts_by_year(self, mock_source_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        assert len(source.counts_by_year) == 14

        # Most recent year
        recent = source.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 2075
        assert recent.cited_by_count == 382314

        # Verify descending order
        years = [c.year for c in source.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_source_works_api_url(self, mock_source_data):
        """Test works API URL."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert (
            source.works_api_url
            == "https://api.openalex.org/works?filter=primary_location.source.id:S137773608"
        )

    def test_source_updated_date(self, mock_source_data):
        """Test updated date field."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.updated_date == date(2025, 6, 7)

    def test_source_created_date(self, mock_source_data):
        """Test created date field."""
        from openalex.models import Source

        source = Source(**mock_source_data)
        assert source.created_date == date(2016, 6, 24)

    def test_source_minimal_data(self):
        """Test source with minimal required fields."""
        from openalex.models import Source

        minimal_source = Source(
            id="https://openalex.org/S123456", display_name="Test Journal"
        )

        assert minimal_source.id == "https://openalex.org/S123456"
        assert minimal_source.display_name == "Test Journal"
        assert minimal_source.issn_l is None
        assert minimal_source.issn is None
        assert minimal_source.type is None
        assert minimal_source.works_count == 0

    def test_source_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Source

        # Missing required fields
        with pytest.raises(ValidationError):
            Source()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Source(id="not-a-url", display_name="Test")

        # Invalid type
        with pytest.raises(ValidationError):
            Source(
                id="https://openalex.org/S123",
                display_name="Test",
                type="invalid_type",
            )

    def test_source_types(self):
        """Test different source types."""
        from openalex.models import Source

        valid_types = [
            "journal",
            "repository",
            "conference",
            "ebook",
            "book series",
            "other",
        ]

        for source_type in valid_types:
            source = Source(
                id=f"https://openalex.org/S{source_type}",
                display_name=f"Test {source_type}",
                type=source_type,
            )
            assert source.type == source_type

    def test_open_access_journal(self):
        """Test open access journal source."""
        from openalex.models import Source

        oa_source_data = {
            "id": "https://openalex.org/S1983995261",
            "display_name": "PeerJ",
            "issn_l": "2167-8359",
            "issn": ["2167-8359"],
            "is_oa": True,
            "is_in_doaj": True,
            "type": "journal",
            "apc_usd": 1395,
        }

        source = Source(**oa_source_data)

        assert source.is_oa is True
        assert source.is_in_doaj is True
        assert source.apc_usd == 1395

    def test_repository_source(self):
        """Test repository source type."""
        from openalex.models import Source

        repo_data = {
            "id": "https://openalex.org/S4306400194",
            "display_name": "arXiv",
            "type": "repository",
            "is_oa": True,
            "host_organization": "https://openalex.org/I205783295",
            "host_organization_name": "Cornell University",
        }

        source = Source(**repo_data)

        assert source.type == "repository"
        assert source.is_oa is True
        assert source.host_organization_name == "Cornell University"

    def test_conference_source(self):
        """Test conference source type."""
        from openalex.models import Source

        conf_data = {
            "id": "https://openalex.org/S123456",
            "display_name": "International Conference on Machine Learning",
            "type": "conference",
            "alternate_titles": ["ICML"],
            "abbreviated_title": "ICML",
        }

        source = Source(**conf_data)

        assert source.type == "conference"
        assert source.alternate_titles == ["ICML"]
        assert source.abbreviated_title == "ICML"

    def test_source_with_multiple_issns(self):
        """Test source with print and electronic ISSNs."""
        from openalex.models import Source

        source_data = {
            "id": "https://openalex.org/S789",
            "display_name": "Journal with Multiple ISSNs",
            "issn_l": "1234-5678",
            "issn": [
                "1234-5678",
                "8765-4321",
                "1111-2222",
            ],  # Print, electronic, other
            "type": "journal",
        }

        source = Source(**source_data)

        assert source.issn_l == "1234-5678"
        assert len(source.issn) == 3
        assert "1234-5678" in source.issn
        assert "8765-4321" in source.issn

    def test_source_with_societies(self):
        """Test source affiliated with academic societies."""
        from openalex.models import Source

        source_data = {
            "id": "https://openalex.org/S999",
            "display_name": "Society Journal",
            "type": "journal",
            "societies": [
                {
                    "id": "https://openalex.org/S1",
                    "display_name": "American Physical Society",
                },
                {
                    "id": "https://openalex.org/S2",
                    "display_name": "Institute of Physics",
                },
            ],
        }

        source = Source(**source_data)

        assert len(source.societies) == 2
        society_names = [s.display_name for s in source.societies]
        assert "American Physical Society" in society_names
        assert "Institute of Physics" in society_names

    def test_source_complete_profile(self, mock_source_data):
        """Test complete source profile with all fields populated."""
        from openalex.models import Source

        source = Source(**mock_source_data)

        # Verify all major sections are populated
        assert source.id is not None
        assert source.display_name is not None
        assert source.works_count > 0
        assert source.cited_by_count > 0
        assert source.issn is not None
        assert source.host_organization is not None
        assert len(source.topics) > 0
        assert len(source.counts_by_year) > 0
        assert source.summary_stats is not None
        assert source.ids is not None
