"""
Comprehensive tests for the Work model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestWorkModel:
    """Test suite for Work model with real OpenAlex data structure."""

    def test_work_basic_fields(self, mock_work_data):
        """Test basic work fields from fixture."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        # Basic identifiers
        assert work.id == "https://openalex.org/W2741809807"
        assert work.doi == "https://doi.org/10.7717/peerj.4375"
        assert (
            work.title
            == "The state of OA: a large-scale analysis of the prevalence and impact of Open Access articles"
        )
        assert work.display_name == work.title

        # Publication details
        assert work.publication_year == 2018
        assert work.publication_date == date(2018, 2, 13)
        assert work.type == "article"
        assert work.type_crossref == "journal-article"

        # Metrics
        assert work.cited_by_count == 960
        assert work.is_retracted is False
        assert work.is_paratext is False

    def test_work_ids_structure(self, mock_work_data):
        """Test the IDs nested structure."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.ids.openalex == "https://openalex.org/W2741809807"
        assert work.ids.doi == "https://doi.org/10.7717/peerj.4375"
        assert work.ids.mag == "2741809807"
        assert work.ids.pmid == "https://pubmed.ncbi.nlm.nih.gov/29456894"
        assert (
            work.ids.pmcid
            == "https://www.ncbi.nlm.nih.gov/pmc/articles/5815332"
        )

    def test_work_primary_location(self, mock_work_data):
        """Test primary location structure."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.primary_location is not None
        location = work.primary_location

        assert location.is_oa is True
        assert location.landing_page_url == "https://doi.org/10.7717/peerj.4375"
        assert location.pdf_url == "https://peerj.com/articles/4375.pdf"
        assert location.source.id == "https://openalex.org/S1983995261"
        assert location.source.display_name == "PeerJ"
        assert location.source.issn_l == "2167-8359"
        assert location.source.is_oa is True
        assert location.source.is_in_doaj is True
        assert location.license == "cc-by"
        assert location.license_id == "https://openalex.org/licenses/cc-by"
        assert location.version == "publishedVersion"
        assert location.is_accepted is True
        assert location.is_published is True

    def test_work_open_access(self, mock_work_data):
        """Test open access information."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.open_access.is_oa is True
        assert work.open_access.oa_status == "gold"
        assert work.open_access.oa_url == "https://peerj.com/articles/4375.pdf"
        assert work.open_access.any_repository_has_fulltext is True

    def test_work_authorships(self, mock_work_data):
        """Test authorship structure with all details."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert len(work.authorships) == 9

        # First author
        first_author = work.authorships[0]
        assert first_author.author_position == "first"
        assert first_author.author.id == "https://openalex.org/A5048491430"
        assert first_author.author.display_name == "Heather Piwowar"
        assert (
            first_author.author.orcid == "https://orcid.org/0000-0003-1613-5981"
        )
        assert first_author.is_corresponding is False
        assert first_author.raw_author_name == "Heather Piwowar"
        assert first_author.raw_affiliation_strings == [
            "Impactstory, Sanford, NC, USA"
        ]
        assert first_author.countries == ["US"]
        assert len(first_author.institutions) == 1
        assert (
            first_author.institutions[0].id
            == "https://openalex.org/I4210166736"
        )
        assert (
            first_author.institutions[0].display_name
            == "Impact Technology Development (United States)"
        )

        # Last author
        last_author = work.authorships[-1]
        assert last_author.author_position == "last"
        assert last_author.author.display_name == "Stefanie Haustein"
        assert len(last_author.institutions) == 2
        assert last_author.countries == ["CA"]

    def test_work_topics(self, mock_work_data):
        """Test topics and subtopics."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.primary_topic is not None
        assert work.primary_topic.id == "https://openalex.org/T10102"
        assert (
            work.primary_topic.display_name
            == "scientometrics and bibliometrics research"
        )
        assert work.primary_topic.score > 0.99
        assert (
            work.primary_topic.subfield.display_name
            == "Statistics, Probability and Uncertainty"
        )
        assert work.primary_topic.field.display_name == "Decision Sciences"
        assert work.primary_topic.domain.display_name == "Social Sciences"

        assert len(work.topics) == 3
        topic_names = [t.display_name for t in work.topics]
        assert "scientometrics and bibliometrics research" in topic_names
        assert "Academic Publishing and Open Access" in topic_names

    def test_work_keywords(self, mock_work_data):
        """Test keywords structure."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert len(work.keywords) == 4
        keyword_names = [k.display_name for k in work.keywords]
        assert "Scholarly Communication" in keyword_names
        assert "Web of science" in keyword_names
        assert "Open Science" in keyword_names
        assert "Citation analysis" in keyword_names

    def test_work_concepts(self, mock_work_data):
        """Test concepts structure."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert len(work.concepts) > 0

        # Check high-scoring concept
        citation_concept = next(
            c for c in work.concepts if c.display_name == "Citation"
        )
        assert citation_concept.level == 2
        assert citation_concept.score > 0.68
        assert (
            citation_concept.wikidata == "https://www.wikidata.org/wiki/Q1713"
        )

    def test_work_mesh_terms(self, mock_work_data):
        """Test MeSH terms (empty in this case)."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.mesh == []

    def test_work_locations_count(self, mock_work_data):
        """Test multiple locations."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.locations_count == 7
        assert len(work.locations) == 7

        # Verify different repository types
        location_types = {
            loc.source.type for loc in work.locations if loc.source
        }
        assert "journal" in location_types
        assert "repository" in location_types

    def test_work_best_oa_location(self, mock_work_data):
        """Test best OA location selection."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.best_oa_location is not None
        assert work.best_oa_location.is_oa is True
        assert (
            work.best_oa_location.pdf_url
            == "https://peerj.com/articles/4375.pdf"
        )

    def test_work_referenced_works(self, mock_work_data):
        """Test referenced works."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.referenced_works_count == 45
        assert len(work.referenced_works) == 45
        assert all(
            ref.startswith("https://openalex.org/W")
            for ref in work.referenced_works
        )

    def test_work_related_works(self, mock_work_data):
        """Test related works."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert len(work.related_works) == 10
        assert all(
            rel.startswith("https://openalex.org/W")
            for rel in work.related_works
        )

    def test_work_abstract(self, mock_work_data):
        """Test abstract inverted index reconstruction."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        # The model should reconstruct abstract from inverted index
        abstract = work.abstract
        assert abstract is not None
        assert abstract.startswith("Despite growing interest in Open Access")
        assert "large-scale" in abstract
        assert "67 million articles" in abstract
        assert len(abstract.split()) > 200  # Substantial abstract

    def test_work_biblio(self, mock_work_data):
        """Test bibliographic information."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.biblio.volume == "6"
        assert work.biblio.issue is None
        assert work.biblio.first_page == "e4375"
        assert work.biblio.last_page == "e4375"

    def test_work_sustainable_development_goals(self, mock_work_data):
        """Test SDGs (empty in this case)."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.sustainable_development_goals == []

    def test_work_grants(self, mock_work_data):
        """Test grants information."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.grants == []

    def test_work_apc(self, mock_work_data):
        """Test article processing charges."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.apc_list is not None
        assert work.apc_list.value == 1395
        assert work.apc_list.currency == "USD"
        assert work.apc_list.value_usd == 1395

        assert work.apc_paid is not None
        assert work.apc_paid.value == 1395
        assert work.apc_paid.currency == "USD"

    def test_work_counts_by_year(self, mock_work_data):
        """Test citation counts by year."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert len(work.counts_by_year) > 0

        # Check most recent year
        recent_year = work.counts_by_year[0]
        assert recent_year.year == 2025
        assert recent_year.cited_by_count == 30

        # Verify years are in descending order
        years = [c.year for c in work.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_work_citation_normalized_percentile(self, mock_work_data):
        """Test citation percentile metrics."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.citation_normalized_percentile is not None
        assert work.citation_normalized_percentile.value == 0.999768
        assert work.citation_normalized_percentile.is_in_top_1_percent is True
        assert work.citation_normalized_percentile.is_in_top_10_percent is True

    def test_work_fwci(self, mock_work_data):
        """Test field-weighted citation impact."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.fwci == 76.282

    def test_work_helper_methods(self, mock_work_data):
        """Test helper methods that should be implemented."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        # Test year lookups
        assert work.publication_year == 2018

        # Test boolean properties
        assert work.has_fulltext is True

        # Test author/institution extraction
        author_names = [auth.author.display_name for auth in work.authorships]
        assert "Heather Piwowar" in author_names
        assert "Jason Priem" in author_names

        institution_names = []
        for authorship in work.authorships:
            for inst in authorship.institutions:
                institution_names.append(inst.display_name)
        assert (
            "Impact Technology Development (United States)" in institution_names
        )

    def test_work_minimal_data(self):
        """Test work with minimal required fields."""
        from openalex.models import Work

        minimal_work = Work(
            id="https://openalex.org/W123456", display_name="Minimal Test Work"
        )

        assert minimal_work.id == "https://openalex.org/W123456"
        assert minimal_work.title == "Minimal Test Work"
        assert minimal_work.doi is None
        assert minimal_work.publication_year is None
        assert minimal_work.cited_by_count == 0
        assert len(minimal_work.authorships) == 0

    def test_work_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Work

        # Missing required fields
        with pytest.raises(ValidationError):
            Work()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Work(id="not-a-url", display_name="Test")

        # Invalid type
        with pytest.raises(ValidationError):
            Work(
                id="https://openalex.org/W123",
                display_name="Test",
                type="invalid_type",
            )

    def test_work_with_versions(self):
        """Test work with multiple versions/locations."""
        from openalex.models import Work

        work_data = {
            "id": "https://openalex.org/W123",
            "display_name": "Multi-version Work",
            "locations": [
                {
                    "is_oa": True,
                    "landing_page_url": "https://doi.org/10.1234/test",
                    "pdf_url": "https://journal.com/pdf/test.pdf",
                    "source": {
                        "id": "https://openalex.org/S123",
                        "display_name": "Test Journal",
                        "type": "journal",
                    },
                    "version": "publishedVersion",
                    "is_accepted": True,
                    "is_published": True,
                },
                {
                    "is_oa": True,
                    "landing_page_url": "https://arxiv.org/abs/1234.5678",
                    "pdf_url": "https://arxiv.org/pdf/1234.5678.pdf",
                    "source": {
                        "id": "https://openalex.org/S4306400194",
                        "display_name": "arXiv",
                        "type": "repository",
                    },
                    "version": "submittedVersion",
                    "is_accepted": False,
                    "is_published": False,
                },
            ],
        }

        work = Work(**work_data)
        assert len(work.locations) == 2
        assert work.locations[0].version == "publishedVersion"
        assert work.locations[1].version == "submittedVersion"

    def test_work_corresponding_authors(self, mock_work_data):
        """Test corresponding author information."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        # This work has no corresponding authors marked
        assert work.corresponding_author_ids == []
        assert work.corresponding_institution_ids == []

    def test_work_institution_assertions(self, mock_work_data):
        """Test institution assertions."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.institution_assertions == []

    def test_work_countries_distinct_count(self, mock_work_data):
        """Test countries distinct count."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.countries_distinct_count == 2  # US and CA

    def test_work_institutions_distinct_count(self, mock_work_data):
        """Test institutions distinct count."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.institutions_distinct_count == 8

    def test_work_created_date(self, mock_work_data):
        """Test created date field."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert work.created_date == date(2017, 8, 8)

    def test_work_indexed_in(self, mock_work_data):
        """Test indexed_in field."""
        from openalex.models import Work

        work = Work(**mock_work_data)
        assert "crossref" in work.indexed_in
        assert "doaj" in work.indexed_in
        assert "pubmed" in work.indexed_in

    def test_work_convenience_methods(self, mock_work_data):
        """Test Work model convenience methods."""
        from openalex.models import Work

        work = Work(**mock_work_data)

        assert work.cited_by_count_by_year(2023) == 252
        assert work.cited_by_count_by_year(1999) == 0

        author_names = work.author_names()
        assert "Heather A. Piwowar" in author_names
        assert "Jason Priem" in author_names

        inst_names = work.institution_names()
        assert any("OurResearch" in name for name in inst_names)

        assert work.has_references() is True

        work_no_abstract = Work(**{**mock_work_data, "abstract": None})
        assert work_no_abstract.has_abstract() is False
