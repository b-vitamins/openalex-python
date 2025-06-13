"""
Comprehensive tests for the Institution model using conftest fixtures.
Tests cover all fields, relationships, and edge cases based on actual OpenAlex data.
"""

from datetime import date

import pytest
from pydantic import ValidationError


class TestInstitutionModel:
    """Test suite for Institution model with real OpenAlex data structure."""

    def test_institution_basic_fields(self, mock_institution_data):
        """Test basic institution fields from fixture."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        # Basic identifiers
        assert institution.id == "https://openalex.org/I27837315"
        assert institution.ror == "https://ror.org/00jmfr291"
        assert institution.display_name == "University of Michigan"
        assert institution.country_code == "US"
        assert institution.type == "funder"
        assert (
            institution.type_id
            == "https://openalex.org/institution-types/funder"
        )

        # Metrics
        assert institution.works_count == 932499
        assert institution.cited_by_count == 22747187

    def test_institution_homepage_and_images(self, mock_institution_data):
        """Test homepage and image URLs."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.homepage_url == "https://www.umich.edu"
        assert (
            institution.image_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/University%20of%20Michigan%20logo.svg"
        )
        assert (
            institution.image_thumbnail_url
            == "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/University%20of%20Michigan%20logo.svg&width=300"
        )

    def test_institution_display_name_variants(self, mock_institution_data):
        """Test display name acronyms and alternatives."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.display_name_acronyms == ["UM"]
        assert institution.display_name_alternatives == [
            "UMich",
            "University of Michigan–Ann Arbor",
            "Université du Michigan",
        ]

    def test_institution_lineage(self, mock_institution_data):
        """Test institution lineage."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.lineage == ["https://openalex.org/I27837315"]
        # This is a top-level institution, so lineage only contains itself

    def test_institution_repositories(self, mock_institution_data):
        """Test institution repositories."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.repositories) == 2

        # Check repositories
        repo_names = [repo.display_name for repo in institution.repositories]
        assert (
            "CINECA IRIS Institutional Research Information System (IRIS Istituto Nazionale di Ricerca Metrologica)"
            in repo_names
        )
        assert "Deep Blue (University of Michigan)" in repo_names

        # Verify repository structure
        deep_blue = next(
            r for r in institution.repositories if "Deep Blue" in r.display_name
        )
        assert deep_blue.id == "https://openalex.org/S4306400393"
        assert deep_blue.host_organization == institution.id
        assert deep_blue.host_organization_name == institution.display_name

    def test_institution_summary_stats(self, mock_institution_data):
        """Test summary statistics."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.summary_stats is not None
        assert (
            institution.summary_stats.two_year_mean_citedness
            == 0.37478000185261595
        )
        assert institution.summary_stats.h_index == 1265
        assert institution.summary_stats.i10_index == 245116

        # Test convenience properties
        assert institution.h_index == 1265
        assert institution.i10_index == 245116

    def test_institution_ids_structure(self, mock_institution_data):
        """Test the IDs nested structure."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.ids.openalex == "https://openalex.org/I27837315"
        assert institution.ids.ror == "https://ror.org/00jmfr291"
        assert institution.ids.mag == "27837315"
        assert institution.ids.grid == "grid.214458.e"
        assert (
            institution.ids.wikipedia
            == "https://en.wikipedia.org/wiki/University%20of%20Michigan"
        )
        assert (
            institution.ids.wikidata == "https://www.wikidata.org/wiki/Q230492"
        )

    def test_institution_geo_location(self, mock_institution_data):
        """Test geographic location information."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.geo is not None
        assert institution.geo.city == "Ann Arbor"
        assert institution.geo.geonames_city_id == "4984247"
        assert institution.geo.region is None
        assert institution.geo.country_code == "US"
        assert institution.geo.country == "United States"
        assert institution.geo.latitude == 42.27756
        assert institution.geo.longitude == -83.74088

    def test_institution_international_names(self, mock_institution_data):
        """Test international display names."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert institution.international is not None
        assert (
            len(institution.international.display_name) > 50
        )  # Many languages

        # Check a few languages
        assert (
            institution.international.display_name.get("en")
            == "University of Michigan"
        )
        assert (
            institution.international.display_name.get("es")
            == "Universidad de Míchigan"
        )
        assert (
            institution.international.display_name.get("fr")
            == "université du Michigan"
        )
        assert (
            institution.international.display_name.get("ja") == "ミシガン大学"
        )
        assert institution.international.display_name.get("zh") == "密西根大学"

    def test_institution_associated_institutions(self, mock_institution_data):
        """Test associated institutions."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.associated_institutions) == 12

        # Check child institutions
        child_institutions = [
            ai
            for ai in institution.associated_institutions
            if ai.relationship == "child"
        ]
        assert len(child_institutions) == 7

        child_names = [ai.display_name for ai in child_institutions]
        assert "Center for Complex Particle Systems" in child_names
        assert "University of Michigan Press" in child_names

        # Check related institutions
        related_institutions = [
            ai
            for ai in institution.associated_institutions
            if ai.relationship == "related"
        ]
        assert len(related_institutions) == 5

        related_names = [ai.display_name for ai in related_institutions]
        assert "Michigan Medicine" in related_names
        assert "University of Michigan–Dearborn" in related_names

    def test_institution_counts_by_year(self, mock_institution_data):
        """Test yearly publication and citation counts."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.counts_by_year) == 14

        # Most recent year
        recent = institution.counts_by_year[0]
        assert recent.year == 2025
        assert recent.works_count == 6145
        assert recent.cited_by_count == 532567

        # High-productivity year
        year_2022 = next(
            c for c in institution.counts_by_year if c.year == 2022
        )
        assert year_2022.works_count == 454439
        assert year_2022.cited_by_count == 1495516

        # Verify descending order
        years = [c.year for c in institution.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_institution_roles(self, mock_institution_data):
        """Test institution roles."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.roles) == 3

        # Check different roles
        roles_dict = {r.role: r for r in institution.roles}

        assert "institution" in roles_dict
        assert roles_dict["institution"].id == institution.id
        assert roles_dict["institution"].works_count == 932499

        assert "funder" in roles_dict
        assert roles_dict["funder"].id == "https://openalex.org/F4320309652"
        assert roles_dict["funder"].works_count == 4048

        assert "publisher" in roles_dict
        assert roles_dict["publisher"].id == "https://openalex.org/P4310316579"
        assert roles_dict["publisher"].works_count == 21226

    def test_institution_topics(self, mock_institution_data):
        """Test institution research topics."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.topics) == 25

        # Top topics
        top_topic = institution.topics[0]
        assert top_topic.id == "https://openalex.org/T10048"
        assert (
            top_topic.display_name
            == "Particle physics theoretical and experimental studies"
        )
        assert top_topic.count == 5089
        assert (
            top_topic.subfield.display_name == "Nuclear and High Energy Physics"
        )

        # Check diversity of research
        topic_names = [t.display_name for t in institution.topics[:5]]
        assert (
            "Particle physics theoretical and experimental studies"
            in topic_names
        )
        assert "Astro and Planetary Science" in topic_names
        assert "Nuclear Physics and Applications" in topic_names
        assert "Health disparities and outcomes" in topic_names

    def test_institution_topic_share(self, mock_institution_data):
        """Test topic share percentages."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.topic_share) == 25

        # Top topic share
        top_share = institution.topic_share[0]
        assert top_share.id == "https://openalex.org/T14440"
        assert top_share.display_name == "Quality of Life Measurement"
        assert top_share.value == 0.1615252

    def test_institution_x_concepts(self, mock_institution_data):
        """Test x_concepts legacy field."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        assert len(institution.x_concepts) == 5

        # Top concept
        cs_concept = institution.x_concepts[0]
        assert cs_concept.id == "https://openalex.org/C41008148"
        assert cs_concept.display_name == "Computer science"
        assert cs_concept.level == 0
        assert cs_concept.score == 57.9

    def test_institution_is_super_system(self, mock_institution_data):
        """Test is_super_system field."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)
        assert institution.is_super_system is False

    def test_institution_works_api_url(self, mock_institution_data):
        """Test works API URL."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)
        assert (
            institution.works_api_url
            == "https://api.openalex.org/works?filter=institutions.id:I27837315"
        )

    def test_institution_updated_date(self, mock_institution_data):
        """Test updated date field."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)
        assert institution.updated_date == date(2025, 6, 6)

    def test_institution_created_date(self, mock_institution_data):
        """Test created date field."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)
        assert institution.created_date == date(2016, 6, 24)

    def test_institution_minimal_data(self):
        """Test institution with minimal required fields."""
        from openalex.models import Institution

        minimal_institution = Institution(
            id="https://openalex.org/I123456", display_name="Test Institution"
        )

        assert minimal_institution.id == "https://openalex.org/I123456"
        assert minimal_institution.display_name == "Test Institution"
        assert minimal_institution.ror is None
        assert minimal_institution.country_code is None
        assert minimal_institution.type is None
        assert len(minimal_institution.repositories) == 0

    def test_institution_validation_errors(self):
        """Test validation errors for invalid data."""
        from openalex.models import Institution

        # Missing required fields
        with pytest.raises(ValidationError):
            Institution()

        # Invalid URL format for id
        with pytest.raises(ValidationError):
            Institution(id="not-a-url", display_name="Test")

        # Invalid ROR format
        with pytest.raises(ValidationError):
            Institution(
                id="https://openalex.org/I123",
                display_name="Test",
                ror="invalid-ror",
            )

        # Invalid country code
        with pytest.raises(ValidationError):
            Institution(
                id="https://openalex.org/I123",
                display_name="Test",
                country_code="ZZZ",  # Not a valid ISO code
            )

    def test_institution_with_parent(self):
        """Test institution with parent institution."""
        from openalex.models import Institution

        institution_data = {
            "id": "https://openalex.org/I456",
            "display_name": "Department of Physics",
            "type": "education",
            "lineage": [
                "https://openalex.org/I123",  # University
                "https://openalex.org/I456",  # Department
            ],
            "parent_institution": {
                "id": "https://openalex.org/I123",
                "display_name": "Parent University",
                "type": "education",
            },
        }

        institution = Institution(**institution_data)

        assert institution.parent_institution is not None
        assert institution.parent_institution.id == "https://openalex.org/I123"
        assert (
            institution.parent_institution.display_name == "Parent University"
        )
        assert len(institution.lineage) == 2

    def test_institution_without_location(self):
        """Test institution without geographic information."""
        from openalex.models import Institution

        institution_data = {
            "id": "https://openalex.org/I789",
            "display_name": "Virtual Research Institute",
            "type": "other",
            "geo": None,
        }

        institution = Institution(**institution_data)

        assert institution.geo is None

    def test_institution_types(self):
        """Test different institution types."""
        from openalex.models import Institution

        valid_types = [
            "education",
            "healthcare",
            "company",
            "archive",
            "nonprofit",
            "government",
            "facility",
            "other",
            "funder",
        ]

        for inst_type in valid_types:
            institution = Institution(
                id=f"https://openalex.org/I{inst_type}",
                display_name=f"Test {inst_type}",
                type=inst_type,
            )
            assert institution.type == inst_type

    def test_institution_complete_profile(self, mock_institution_data):
        """Test complete institution profile with all fields populated."""
        from openalex.models import Institution

        institution = Institution(**mock_institution_data)

        # Verify all major sections are populated
        assert institution.id is not None
        assert institution.display_name is not None
        assert institution.works_count > 0
        assert institution.cited_by_count > 0
        assert institution.geo is not None
        assert len(institution.associated_institutions) > 0
        assert len(institution.topics) > 0
        assert len(institution.counts_by_year) > 0
        assert institution.summary_stats is not None
        assert institution.ids is not None
        assert institution.international is not None
