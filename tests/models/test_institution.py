from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    Institution,
    InstitutionType,
)


class TestInstitution:
    """Test Institution model with comprehensive realistic fixtures."""

    @pytest.fixture()
    def comprehensive_institution_data(self) -> dict[str, Any]:
        """Comprehensive institution data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/I27837315",
            "ror": "https://ror.org/00za53h95",
            "display_name": "University of Michigan-Ann Arbor",
            "relevance_score": None,
            "country_code": "US",
            "type": "education",
            "type_id": "https://openalex.org/institution-types/education",
            "lineage": ["https://openalex.org/I27837315"],
            "homepage_url": "https://umich.edu/",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/93/Seal_of_the_University_of_Michigan.svg",
            "image_thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Seal_of_the_University_of_Michigan.svg/100px-Seal_of_the_University_of_Michigan.svg.png",
            "display_name_acronyms": ["U of M", "UMich", "UM"],
            "display_name_alternatives": [
                "University of Michigan",
                "Univ of Michigan",
                "U Michigan Ann Arbor",
                "University of Michigan Ann Arbor",
            ],
            "works_count": 425691,
            "cited_by_count": 21092874,
            "summary_stats": {
                "2yr_mean_citedness": 4.073980589655935,
                "h_index": 586,
                "i10_index": 133815,
            },
            "ids": {
                "openalex": "https://openalex.org/I27837315",
                "ror": "https://ror.org/00za53h95",
                "mag": "27837315",
                "grid": "grid.214458.e",
                "wikipedia": "https://en.wikipedia.org/wiki/University%20of%20Michigan",
                "wikidata": "https://www.wikidata.org/wiki/Q230492",
            },
            "geo": {
                "city": "Ann Arbor",
                "geonames_city_id": "4984247",
                "region": "Michigan",
                "country_code": "US",
                "country": "United States",
                "latitude": 42.27756,
                "longitude": -83.738224,
            },
            "international_display_name": {
                "ar": "جامعة ميشيغان",
                "be": "Мічыганскі ўніверсітэт",
                "ca": "Universitat de Michigan",
                "cy": "Prifysgol Michigan",
                "da": "University of Michigan",
                "de": "University of Michigan",
                "el": "Πανεπιστήμιο του Μίσιγκαν",
                "en": "University of Michigan-Ann Arbor",
                "eo": "Universitato de Miĉigano",
                "es": "Universidad de Míchigan",
                "et": "Michigani Ülikool",
                "eu": "Michiganeko Unibertsitatea",
                "fi": "Michiganin yliopisto",
                "fr": "université du Michigan",
                "ga": "Ollscoil Michigan",
                "gl": "Universidade de Michigan",
                "he": "אוניברסיטת מישיגן",
                "hu": "Michigani Egyetem",
                "id": "Universitas Michigan",
                "it": "Università del Michigan",
                "ja": "ミシガン大学",
                "ko": "미시간 대학교",
                "la": "Universitas Michiganensis",
                "lt": "Mičigano universitetas",
                "lv": "Mičiganas Universitāte",
                "nb": "University of Michigan",
                "nl": "Universiteit van Michigan",
                "nn": "University of Michigan",
                "pl": "University of Michigan",
                "pt": "Universidade de Michigan",
                "ro": "Universitatea Michigan",
                "ru": "Мичиганский университет",
                "sk": "Michiganská univerzita",
                "sv": "University of Michigan",
                "tr": "Michigan Üniversitesi",
                "uk": "Мічиганський університет",
                "ur": "جامعہ مشی گن",
                "vi": "Đại học Michigan",
                "zh": "密歇根大学",
                "zh-cn": "密歇根大学",
                "zh-hans": "密歇根大学",
                "zh-hant": "密西根大學",
                "zh-hk": "密芝根大學",
                "zh-mo": "密芝根大學",
                "zh-my": "密歇根大学",
                "zh-sg": "密歇根大学",
                "zh-tw": "密西根大學",
            },
            "associated_institutions": [
                {
                    "id": "https://openalex.org/I142606810",
                    "ror": "https://ror.org/01tn5sr83",
                    "display_name": "Michigan Medicine",
                    "country_code": "US",
                    "type": "healthcare",
                    "relationship": "related",
                },
                {
                    "id": "https://openalex.org/I4210119109",
                    "ror": "https://ror.org/00t33hh48",
                    "display_name": "University of Michigan-Dearborn",
                    "country_code": "US",
                    "type": "education",
                    "relationship": "related",
                },
                {
                    "id": "https://openalex.org/I73999763",
                    "ror": "https://ror.org/047s2c258",
                    "display_name": "University of Michigan-Flint",
                    "country_code": "US",
                    "type": "education",
                    "relationship": "related",
                },
            ],
            "x_concepts": [
                {
                    "id": "https://openalex.org/C71924100",
                    "wikidata": "https://www.wikidata.org/wiki/Q11190",
                    "display_name": "Medicine",
                    "level": 0,
                    "score": 42.5,
                },
                {
                    "id": "https://openalex.org/C86803240",
                    "wikidata": "https://www.wikidata.org/wiki/Q420",
                    "display_name": "Biology",
                    "level": 0,
                    "score": 39.8,
                },
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 31.6,
                },
            ],
            "counts_by_year": [
                {"year": 2024, "works_count": 18234, "cited_by_count": 984521},
                {"year": 2023, "works_count": 21456, "cited_by_count": 1245678},
                {"year": 2022, "works_count": 20123, "cited_by_count": 1198765},
                {"year": 2021, "works_count": 19876, "cited_by_count": 1087654},
                {"year": 2020, "works_count": 18765, "cited_by_count": 987654},
            ],
            "roles": [
                {
                    "role": "institution",
                    "id": "https://openalex.org/I27837315",
                    "works_count": 425691,
                },
                {
                    "role": "funder",
                    "id": "https://openalex.org/F4320332182",
                    "works_count": 15423,
                },
            ],
            "topics": [
                {
                    "id": "https://openalex.org/T10018",
                    "display_name": "Density Functional Theory and Molecular Dynamics",
                    "count": 12543,
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
                }
            ],
            "topic_share": [
                {
                    "id": "https://openalex.org/T10018",
                    "display_name": "Density Functional Theory and Molecular Dynamics",
                    "value": 0.0123,
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
                }
            ],
            "repositories": [
                {
                    "id": "https://openalex.org/S4306400393",
                    "display_name": "Deep Blue (University of Michigan)",
                    "host_organization": "https://openalex.org/I27837315",
                    "host_organization_name": "University of Michigan-Ann Arbor",
                    "host_organization_lineage": [
                        "https://openalex.org/I27837315"
                    ],
                }
            ],
            "created_date": "2016-06-24",
            "updated_date": "2024-12-16T09:53:16.081181",
        }

    @pytest.fixture()
    def company_institution_data(self) -> dict[str, Any]:
        """Company institution data."""
        return {
            "id": "https://openalex.org/I1290206253",
            "ror": "https://ror.org/00f54p054",
            "display_name": "Microsoft Research",
            "country_code": "US",
            "type": "company",
            "lineage": [
                "https://openalex.org/I1290206253",
                "https://openalex.org/I1984054323",
            ],
            "homepage_url": "https://www.microsoft.com/en-us/research/",
            "works_count": 45678,
            "cited_by_count": 2345678,
            "geo": {
                "city": "Redmond",
                "geonames_city_id": "5808079",
                "region": "Washington",
                "country_code": "US",
                "country": "United States",
                "latitude": 47.6739881,
                "longitude": -122.121512,
            },
            "associated_institutions": [
                {
                    "id": "https://openalex.org/I1984054323",
                    "ror": "https://ror.org/00000000",
                    "display_name": "Microsoft",
                    "country_code": "US",
                    "type": "company",
                    "relationship": "parent",
                }
            ],
            "repositories": [],
        }

    @pytest.fixture()
    def hierarchical_institution_data(self) -> dict[str, Any]:
        """Institution with complex hierarchy."""
        return {
            "id": "https://openalex.org/I204722609",
            "ror": "https://ror.org/03efmqc40",
            "display_name": "Arizona State University Tempe Campus",
            "country_code": "US",
            "type": "education",
            "lineage": [
                "https://openalex.org/I204722609",  # Self
                "https://openalex.org/I855328596",  # Parent (ASU)
            ],
            "homepage_url": "https://www.asu.edu/",
            "works_count": 87654,
            "cited_by_count": 3456789,
            "geo": {
                "city": "Tempe",
                "geonames_city_id": "5317058",
                "region": "Arizona",
                "country_code": "US",
                "country": "United States",
                "latitude": 33.421513,
                "longitude": -111.933693,
            },
            "associated_institutions": [
                {
                    "id": "https://openalex.org/I855328596",
                    "ror": "https://ror.org/03efmqc40",
                    "display_name": "Arizona State University",
                    "country_code": "US",
                    "type": "education",
                    "relationship": "parent",
                },
                {
                    "id": "https://openalex.org/I130769515",
                    "ror": "https://ror.org/035t8zc32",
                    "display_name": "Arizona State University West Campus",
                    "country_code": "US",
                    "type": "education",
                    "relationship": "related",
                },
            ],
        }

    def test_comprehensive_institution_creation(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test creating an institution with all fields from comprehensive data."""
        institution = Institution(**comprehensive_institution_data)

        # Basic fields
        assert institution.id == "https://openalex.org/I27837315"
        assert institution.ror == "https://ror.org/00za53h95"
        assert institution.display_name == "University of Michigan-Ann Arbor"
        assert institution.country_code == "US"
        assert institution.type == InstitutionType.EDUCATION

        # URLs and images
        assert str(institution.homepage_url) == "https://umich.edu/"
        assert "wikipedia" in str(institution.image_url)
        assert "thumbnail" in str(institution.image_thumbnail_url)

        # Metrics
        assert institution.works_count == 425691
        assert institution.cited_by_count == 21092874

        # Type checks
        assert institution.is_education is True
        assert institution.is_company is False

    def test_institution_names_and_acronyms(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test institution name variations."""
        institution = Institution(**comprehensive_institution_data)

        # Acronyms
        assert len(institution.display_name_acronyms) == 3
        assert "UMich" in institution.display_name_acronyms
        assert "U of M" in institution.display_name_acronyms

        # Alternative names
        assert len(institution.display_name_alternatives) == 4
        assert "University of Michigan" in institution.display_name_alternatives
        assert "U Michigan Ann Arbor" in institution.display_name_alternatives

    def test_institution_geo_location(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test geographic information."""
        institution = Institution(**comprehensive_institution_data)

        assert institution.geo is not None
        assert institution.geo.city == "Ann Arbor"
        assert institution.geo.region == "Michigan"
        assert institution.geo.country == "United States"
        assert institution.geo.country_code == "US"
        assert institution.geo.latitude == 42.27756
        assert institution.geo.longitude == -83.738224
        assert institution.geo.geonames_city_id == "4984247"

        # Helper method
        assert institution.has_location() is True

    def test_international_display_names(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test international name translations."""
        institution = Institution(**comprehensive_institution_data)

        assert institution.international_display_name is not None
        assert len(institution.international_display_name) > 40

        # Sample translations
        assert (
            institution.international_display_name["en"]
            == "University of Michigan-Ann Arbor"
        )
        assert institution.international_display_name["ja"] == "ミシガン大学"
        assert institution.international_display_name["zh"] == "密歇根大学"
        assert institution.international_display_name["ar"] == "جامعة ميشيغان"
        assert (
            institution.international_display_name["fr"]
            == "université du Michigan"
        )

    def test_associated_institutions(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test associated institutions parsing."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.associated_institutions) == 3

        # Medical center
        med_center = institution.associated_institutions[0]
        assert med_center.display_name == "Michigan Medicine"
        assert med_center.type == "healthcare"
        assert med_center.relationship == "related"

        # Branch campuses
        dearborn = institution.associated_institutions[1]
        assert "Dearborn" in dearborn.display_name
        assert dearborn.type == "education"

    def test_institution_concepts(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test research concepts."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.x_concepts) == 3

        # Top concept
        medicine = institution.x_concepts[0]
        assert medicine.display_name == "Medicine"
        assert medicine.score == 42.5
        assert medicine.level == 0

    def test_institution_roles(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test institution roles (institution vs funder)."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.roles) == 2

        # Institution role
        inst_role = institution.roles[0]
        assert inst_role.role == "institution"
        assert inst_role.works_count == 425691

        # Funder role
        funder_role = institution.roles[1]
        assert funder_role.role == "funder"
        assert funder_role.works_count == 15423

    def test_institution_topics(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test research topics with hierarchy."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.topics) == 1
        topic = institution.topics[0]
        assert (
            topic.display_name
            == "Density Functional Theory and Molecular Dynamics"
        )
        assert topic.count == 12543
        assert (
            topic.subfield.display_name == "Physical and Theoretical Chemistry"
        )
        assert topic.field.display_name == "Chemistry"
        assert topic.domain.display_name == "Physical Sciences"

        # Topic share
        assert len(institution.topic_share) == 1
        assert institution.topic_share[0].value == 0.0123

    def test_institution_repositories(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test institutional repositories."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.repositories) == 1
        repo = institution.repositories[0]
        assert repo.display_name == "Deep Blue (University of Michigan)"
        assert repo.host_organization == institution.id
        assert repo.host_organization_name == institution.display_name

        # Helper method
        assert institution.repository_count() == 1

    def test_company_institution(
        self, company_institution_data: dict[str, Any]
    ) -> None:
        """Test company type institution."""
        company = Institution(**company_institution_data)

        assert company.type == InstitutionType.COMPANY
        assert company.is_company is True
        assert company.is_education is False

        # Has parent company
        assert len(company.associated_institutions) == 1
        parent = company.associated_institutions[0]
        assert parent.display_name == "Microsoft"
        assert parent.relationship == "parent"

        # No repositories
        assert len(company.repositories) == 0
        assert company.repository_count() == 0

    def test_hierarchical_institution(
        self, hierarchical_institution_data: dict[str, Any]
    ) -> None:
        """Test institution with hierarchy."""
        institution = Institution(**hierarchical_institution_data)

        # Lineage
        assert len(institution.lineage) == 2
        assert institution.lineage[0] == institution.id  # Self first
        assert (
            institution.lineage[1] == "https://openalex.org/I855328596"
        )  # Parent

        # Helper methods
        assert (
            institution.parent_institution == "https://openalex.org/I855328596"
        )
        assert institution.root_institution == "https://openalex.org/I855328596"

        # Associated institutions
        parent_assoc = institution.associated_institutions[0]
        assert parent_assoc.relationship == "parent"
        assert parent_assoc.display_name == "Arizona State University"

    def test_institution_counts_by_year(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test yearly publication and citation counts."""
        institution = Institution(**comprehensive_institution_data)

        assert len(institution.counts_by_year) == 5

        # Most recent year
        recent = institution.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 18234
        assert recent.cited_by_count == 984521

        # Verify descending order
        years = [c.year for c in institution.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_institution_summary_stats(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test summary statistics."""
        institution = Institution(**comprehensive_institution_data)

        assert institution.summary_stats is not None
        assert (
            institution.summary_stats.two_year_mean_citedness
            == 4.073980589655935
        )
        assert institution.summary_stats.h_index == 586
        assert institution.summary_stats.i10_index == 133815

        # Property access
        assert institution.h_index == 586
        assert institution.i10_index == 133815

    def test_institution_ids(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test external identifiers."""
        institution = Institution(**comprehensive_institution_data)

        assert institution.ids is not None
        assert institution.ids.openalex == institution.id
        assert institution.ids.ror == institution.ror
        assert institution.ids.mag == "27837315"
        assert institution.ids.grid == "grid.214458.e"
        assert "wikipedia.org" in str(institution.ids.wikipedia)
        assert "wikidata.org" in str(institution.ids.wikidata)

    def test_minimal_institution(self) -> None:
        """Test institution with minimal data."""
        institution = Institution(
            id="I123",
            display_name="Test Institution",
            ror="https://ror.org/test123",
        )

        assert institution.country_code is None
        assert institution.type is None
        assert institution.geo is None
        assert len(institution.repositories) == 0
        assert institution.has_location() is False
        assert institution.parent_institution is None

    def test_institution_validation_errors(self) -> None:
        """Test validation errors for invalid institution data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Institution()

        # Invalid ROR format
        with pytest.raises(ValidationError):
            Institution(id="I123", display_name="Test", ror="invalid-ror")

        # Invalid country code
        with pytest.raises(ValidationError):
            Institution(
                id="I123",
                display_name="Test",
                country_code="ZZZ",  # Not a valid ISO code
            )

    def test_institution_helper_methods(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test institution helper methods."""
        institution = Institution(**comprehensive_institution_data)

        # Year-based lookups
        assert institution.works_in_year(2024) == 18234
        assert institution.citations_in_year(2023) == 1245678
        assert institution.works_in_year(2019) == 0  # Not in data

        # Active years
        active_years = institution.active_years()
        assert 2024 in active_years
        assert len(active_years) == 5

    def test_institution_without_hierarchy(self) -> None:
        """Test institution with no parent/lineage."""
        institution = Institution(
            id="I999",
            display_name="Independent Institute",
            lineage=["I999"],  # Only self
        )

        assert institution.parent_institution is None
        assert institution.root_institution is None

    def test_datetime_fields(
        self, comprehensive_institution_data: dict[str, Any]
    ) -> None:
        """Test datetime field parsing."""
        institution = Institution(**comprehensive_institution_data)

        assert isinstance(institution.created_date, str)
        assert institution.created_date == "2016-06-24"

        assert isinstance(institution.updated_date, datetime)
        assert institution.updated_date.year == 2024
