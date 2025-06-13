"""
Comprehensive tests for the Source/Source model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date


class TestSourceModel:
    """Test suite for Source/Source model with real OpenAlex data structure."""

    def test_source_basic_fields(self, mock_source_data):
        """Test basic venue fields from fixture."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        # Basic identifiers
        assert venue.id == "https://openalex.org/S137773608"
        assert venue.issn_l == "0028-0836"
        assert venue.issn == ["0028-0836", "1476-4687"]
        assert venue.display_name == "Nature"
        assert venue.type == "journal"

        # Publisher information
        assert venue.host_organization == "https://openalex.org/P4310319908"
        assert venue.host_organization_name == "Nature Portfolio"
        assert venue.host_organization_lineage == [
            "https://openalex.org/P4310319908",
            "https://openalex.org/P4310319965",
        ]

        # Metrics
        assert venue.works_count == 431710
        assert venue.cited_by_count == 25258309

    def test_source_summary_stats(self, mock_source_data):
        """Test summary statistics."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert venue.summary_stats is not None
        assert venue.summary_stats.two_year_mean_citedness == 16.2611434684417
        assert venue.summary_stats.h_index == 1779
        assert venue.summary_stats.i10_index == 117589

        # Test convenience properties
        assert venue.h_index == 1779
        assert venue.i10_index == 117589

    def test_source_open_access_status(self, mock_source_data):
        """Test open access fields."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert venue.is_oa is False
        assert venue.is_in_doaj is False

    def test_source_indexing(self, mock_source_data):
        """Test indexing information."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert venue.is_indexed_in_scopus is True
        assert venue.is_core is True

    def test_source_ids_structure(self, mock_source_data):
        """Test the IDs nested structure."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert venue.ids.openalex == "https://openalex.org/S137773608"
        assert venue.ids.issn_l == "0028-0836"
        assert venue.ids.issn == ["0028-0836", "1476-4687"]
        assert venue.ids.mag == "137773608"
        assert venue.ids.wikidata == "https://www.wikidata.org/entity/Q180445"

    def test_source_homepage_url(self, mock_source_data):
        """Test homepage URL."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.homepage_url == "https://www.nature.com/nature/"

    def test_source_apc_prices(self, mock_source_data):
        """Test article processing charges."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert len(venue.apc_prices) == 3

        # Check different currencies
        price_dict = {p.currency: p for p in venue.apc_prices}

        assert price_dict["EUR"].price == 9750
        assert price_dict["USD"].price == 11690
        assert price_dict["GBP"].price == 8490

        assert venue.apc_usd == 11690

    def test_source_country_code(self, mock_source_data):
        """Test country code."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.country_code == "GB"

    def test_source_societies(self, mock_source_data):
        """Test affiliated societies."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.societies == []

    def test_source_alternate_titles(self, mock_source_data):
        """Test alternate titles."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.alternate_titles == []

    def test_source_abbreviated_title(self, mock_source_data):
        """Test abbreviated title."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.abbreviated_title is None

    def test_source_topics(self, mock_source_data):
        """Test venue topics."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert len(venue.topics) == 25

        # Top topic
        top_topic = venue.topics[0]
        assert top_topic.id == "https://openalex.org/T13656"
        assert top_topic.display_name == "Science, Research, and Medicine"
        assert top_topic.count == 12534
        assert top_topic.subfield.display_name == "Reproductive Medicine"
        assert top_topic.field.display_name == "Medicine"
        assert top_topic.domain.display_name == "Health Sciences"

        # Nature publishes diverse topics
        topic_names = [t.display_name for t in venue.topics[:5]]
        assert "Science, Research, and Medicine" in topic_names
        assert "History and Developments in Astronomy" in topic_names
        assert "Astro and Planetary Science" in topic_names

    def test_source_topic_share(self, mock_source_data):
        """Test topic share percentages."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert len(venue.topic_share) == 25

        # Top topic share
        top_share = venue.topic_share[0]
        assert top_share.id == "https://openalex.org/T13656"
        assert top_share.display_name == "Science, Research, and Medicine"
        assert top_share.value == 0.0869209

    def test_source_x_concepts(self, mock_source_data):
        """Test x_concepts legacy field."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert len(venue.x_concepts) == 14

        # Top concept
        biology_concept = venue.x_concepts[0]
        assert biology_concept.id == "https://openalex.org/C86803240"
        assert biology_concept.display_name == "Biology"
        assert biology_concept.level == 0
        assert biology_concept.score == 58.1

    def test_source_counts_by_year(self, mock_source_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Source

        venue = Source(**mock_source_data)

        assert len(venue.counts_by_year) == 13

        # Most recent year
        recent = venue.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 2075
        assert recent.cited_by_count == 382314

        # Verify descending order
        years = [c.year for c in venue.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_source_works_api_url(self, mock_source_data):
        """Test works API URL."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert (
            venue.works_api_url
            == "https://api.openalex.org/works?filter=primary_location.source.id:S137773608"
        )

    def test_source_updated_date(self, mock_source_data):
        """Test updated date field."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.updated_date == date(2025, 6, 7)

    def test_source_created_date(self, mock_source_data):
        """Test created date field."""
        from openalex.models import Source

        venue = Source(**mock_source_data)
        assert venue.created_date == date(2016, 6, 24)

    def test_source_minimal_data(self):
        """Test venue with minimal required fields."""
        from openalex.models import Source

        minimal_source = Source(
            id="https://openalex.org/S123456", display_name="Test Journal"
        )

        assert minimal_source.id == "https://openalex.org/S123456"
        assert minimal_source.display_name == "Test Journal"
        assert minimal_source.issn_l is None
        assert minimal_source.issn is None
        assert minimal_source.type is None
        assert minimal_source
