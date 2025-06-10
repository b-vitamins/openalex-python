from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    Grant,
    MeshTag,
    OpenAccessStatus,
    Work,
    WorkType,
)
from openalex.models.work import (
    BaseFilter as WorkBaseFilter,
)
from openalex.models.work import (
    InstitutionsFilter as WorkInstitutionsFilter,
)
from openalex.models.work import (
    WorksFilter as WorkWorksFilter,
)


class TestWork:
    """Test Work model with comprehensive realistic fixtures."""

    @pytest.fixture
    def comprehensive_work_data(self) -> dict[str, Any]:
        """Comprehensive work data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/W2741809807",
            "doi": "https://doi.org/10.1103/physrevlett.77.3865",
            "title": "Generalized Gradient Approximation Made Simple",
            "display_name": "Generalized Gradient Approximation Made Simple",
            "publication_year": 1996,
            "publication_date": "1996-10-28",
            "type": "article",
            "type_crossref": "journal-article",
            "cited_by_count": 50000,
            "is_retracted": False,
            "is_paratext": False,
            "cited_by_api_url": "https://api.openalex.org/works?filter=cites:W2741809807",
            "abstract_inverted_index": {
                "Generalized": [0, 87],
                "gradient": [1, 88, 124],
                "approximations": [2],
                "(GGA's)": [3],
                "for": [4, 41, 85, 113, 125, 161],
                "the": [
                    5,
                    24,
                    42,
                    49,
                    66,
                    82,
                    86,
                    114,
                    117,
                    126,
                    129,
                    138,
                    150,
                ],
                "exchange-correlation": [6, 127],
                "energy": [7, 128],
                "improve": [8],
                "upon": [9],
                "local": [10, 130],
                "spin": [11, 131],
                "density": [12, 89, 132],
                "(LSD)": [13],
                "description": [14],
                "of": [15, 23, 32, 51, 65, 81, 101, 105, 116, 137, 149, 152],
                "atoms,": [16],
                "molecules,": [17],
                "and": [18, 29, 36, 62, 71, 79, 108, 123, 146, 158],
                "solids.": [19],
                "We": [20],
                "present": [21],
                "a": [22, 97, 111],
                "exchange": [25, 43, 90],
                "GGA": [26],
                "that": [27, 46],
                "combines": [28],
                "desirable": [30],
                "features": [31],
                "previous": [33],
                "semilocal": [34],
                "functionals": [35],
                "is": [37],
                "as": [38, 40],
                "accurate": [39],
                "LSD": [44],
                "correlation": [45, 67, 91],
                "satisfies": [47],
                "limit": [50, 139],
                "uniform": [52],
                "electron": [53],
                "gas.": [54],
            },
            "biblio": {
                "volume": "77",
                "issue": "18",
                "first_page": "3865",
                "last_page": "3868",
            },
            "is_oa": True,
            "open_access": {
                "is_oa": True,
                "oa_status": "bronze",
                "oa_url": "https://example.com/paper.pdf",
                "any_repository_has_fulltext": True,
            },
            "authorships": [
                {
                    "author_position": "first",
                    "author": {
                        "id": "https://openalex.org/A5023888391",
                        "display_name": "John P. Perdew",
                        "orcid": "https://orcid.org/0000-0003-4237-824X",
                    },
                    "institutions": [
                        {
                            "id": "https://openalex.org/I131249849",
                            "display_name": "Tulane University",
                            "ror": "https://ror.org/04v7hvq31",
                            "country_code": "US",
                            "type": "education",
                            "lineage": ["https://openalex.org/I131249849"],
                        }
                    ],
                    "countries": ["US"],
                    "is_corresponding": True,
                    "raw_author_name": "John P. Perdew",
                    "raw_affiliation_strings": [
                        "Department of Physics and Quantum Theory Group, Tulane University, New Orleans, Louisiana 70118"
                    ],
                },
                {
                    "author_position": "middle",
                    "author": {
                        "id": "https://openalex.org/A5082186243",
                        "display_name": "Kieron Burke",
                        "orcid": None,
                    },
                    "institutions": [
                        {
                            "id": "https://openalex.org/I131249849",
                            "display_name": "Tulane University",
                            "ror": "https://ror.org/04v7hvq31",
                            "country_code": "US",
                            "type": "education",
                            "lineage": ["https://openalex.org/I131249849"],
                        }
                    ],
                    "countries": ["US"],
                    "is_corresponding": False,
                    "raw_author_name": "Kieron Burke",
                    "raw_affiliation_strings": [
                        "Department of Chemistry, Rutgers University, Camden, New Jersey 08102"
                    ],
                },
                {
                    "author_position": "last",
                    "author": {
                        "id": "https://openalex.org/A5100600542",
                        "display_name": "Matthias Ernzerhof",
                        "orcid": "https://orcid.org/0000-0001-6126-0532",
                    },
                    "institutions": [
                        {
                            "id": "https://openalex.org/I70931966",
                            "display_name": "Université de Montréal",
                            "ror": "https://ror.org/0161xgx34",
                            "country_code": "CA",
                            "type": "education",
                            "lineage": ["https://openalex.org/I70931966"],
                        }
                    ],
                    "countries": ["CA"],
                    "is_corresponding": False,
                    "raw_author_name": "Matthias Ernzerhof",
                    "raw_affiliation_strings": [
                        "Département de Chimie, Université de Montréal, Montréal, Québec, Canada H3C 3J7"
                    ],
                },
            ],
            "countries_distinct_count": 2,
            "corresponding_author_ids": ["https://openalex.org/A5023888391"],
            "corresponding_institution_ids": [
                "https://openalex.org/I131249849"
            ],
            "apc_list": {
                "value": 3450,
                "currency": "USD",
                "value_usd": 3450,
                "provenance": "doaj",
            },
            "apc_paid": None,
            "fwci": 25.7,
            "has_fulltext": True,
            "fulltext_origin": "pdf",
            "referenced_works": [
                "https://openalex.org/W1964141474",
                "https://openalex.org/W1991138228",
                "https://openalex.org/W2033123394",
                "https://openalex.org/W2036018115",
                "https://openalex.org/W2094641428",
            ],
            "referenced_works_count": 48,
            "related_works": [
                "https://openalex.org/W2963642177",
                "https://openalex.org/W2791889424",
                "https://openalex.org/W2739804168",
                "https://openalex.org/W2171074650",
                "https://openalex.org/W2166919327",
            ],
            "citation_normalized_percentile": {
                "value": 0.999969,
                "is_in_top_1_percent": True,
                "is_in_top_10_percent": True,
            },
            "concepts": [
                {
                    "id": "https://openalex.org/C71924100",
                    "wikidata": "https://www.wikidata.org/wiki/Q11190",
                    "display_name": "Medicine",
                    "level": 0,
                    "score": 0.9187037,
                },
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 0.8546321,
                },
                {
                    "id": "https://openalex.org/C185592680",
                    "wikidata": "https://www.wikidata.org/wiki/Q2329",
                    "display_name": "Chemistry",
                    "level": 0,
                    "score": 0.7234156,
                },
            ],
            "mesh": [
                {
                    "descriptor_ui": "D008967",
                    "descriptor_name": "Molecular Structure",
                    "qualifier_ui": "",
                    "qualifier_name": None,
                    "is_major_topic": True,
                }
            ],
            "keywords": [
                {
                    "id": "https://openalex.org/keywords/density-functional-theory",
                    "display_name": "Density Functional Theory",
                    "score": 0.542901,
                },
                {
                    "id": "https://openalex.org/keywords/gradient-approximation",
                    "display_name": "Gradient Approximation",
                    "score": 0.501234,
                },
            ],
            "language": "en",
            "primary_location": {
                "is_oa": True,
                "landing_page_url": "https://doi.org/10.1103/physrevlett.77.3865",
                "pdf_url": None,
                "source": {
                    "id": "https://openalex.org/S48139910",
                    "display_name": "Physical Review Letters",
                    "issn_l": "0031-9007",
                    "issn": ["0031-9007", "1079-7114"],
                    "is_oa": False,
                    "is_in_doaj": False,
                    "is_core": True,
                    "host_organization": "https://openalex.org/P4310320017",
                    "host_organization_name": "American Physical Society",
                    "host_organization_lineage": [
                        "https://openalex.org/P4310320017"
                    ],
                    "host_organization_lineage_names": [
                        "American Physical Society"
                    ],
                    "type": "journal",
                },
                "license": None,
                "license_id": None,
                "version": "publishedVersion",
                "is_accepted": True,
                "is_published": True,
            },
            "best_oa_location": {
                "is_oa": True,
                "landing_page_url": "https://doi.org/10.1103/physrevlett.77.3865",
                "pdf_url": None,
                "source": {
                    "id": "https://openalex.org/S48139910",
                    "display_name": "Physical Review Letters",
                    "issn_l": "0031-9007",
                    "issn": ["0031-9007", "1079-7114"],
                    "is_oa": False,
                    "is_in_doaj": False,
                    "is_core": True,
                    "host_organization": "https://openalex.org/P4310320017",
                    "host_organization_name": "American Physical Society",
                    "host_organization_lineage": [
                        "https://openalex.org/P4310320017"
                    ],
                    "host_organization_lineage_names": [
                        "American Physical Society"
                    ],
                    "type": "journal",
                },
                "license": None,
                "license_id": None,
                "version": "publishedVersion",
                "is_accepted": True,
                "is_published": True,
            },
            "sustainable_development_goals": [
                {
                    "id": "https://metadata.un.org/sdg/7",
                    "display_name": "Affordable and clean energy",
                    "score": 0.42,
                }
            ],
            "grants": [
                {
                    "funder": "https://openalex.org/F4320306076",
                    "funder_display_name": "National Science Foundation",
                    "award_id": "DMR-9521353",
                }
            ],
            "datasets": [],
            "versions": [],
            "locations_count": 3,
            "locations": [
                {
                    "is_oa": True,
                    "landing_page_url": "https://doi.org/10.1103/physrevlett.77.3865",
                    "pdf_url": None,
                    "source": {
                        "id": "https://openalex.org/S48139910",
                        "display_name": "Physical Review Letters",
                        "issn_l": "0031-9007",
                        "issn": ["0031-9007", "1079-7114"],
                        "is_oa": False,
                        "is_in_doaj": False,
                        "is_core": True,
                        "host_organization": "https://openalex.org/P4310320017",
                        "host_organization_name": "American Physical Society",
                        "host_organization_lineage": [
                            "https://openalex.org/P4310320017"
                        ],
                        "host_organization_lineage_names": [
                            "American Physical Society"
                        ],
                        "type": "journal",
                    },
                    "license": None,
                    "license_id": None,
                    "version": "publishedVersion",
                    "is_accepted": True,
                    "is_published": True,
                },
                {
                    "is_oa": True,
                    "landing_page_url": "https://arxiv.org/abs/cond-mat/9605139",
                    "pdf_url": "https://arxiv.org/pdf/cond-mat/9605139.pdf",
                    "source": {
                        "id": "https://openalex.org/S4306400194",
                        "display_name": "arXiv (Cornell University)",
                        "issn_l": None,
                        "issn": None,
                        "is_oa": True,
                        "is_in_doaj": False,
                        "is_core": False,
                        "host_organization": "https://openalex.org/I205783295",
                        "host_organization_name": "Cornell University",
                        "host_organization_lineage": [
                            "https://openalex.org/I205783295"
                        ],
                        "host_organization_lineage_names": [
                            "Cornell University"
                        ],
                        "type": "repository",
                    },
                    "license": "cc-by",
                    "license_id": "https://openalex.org/licenses/cc-by",
                    "version": "submittedVersion",
                    "is_accepted": False,
                    "is_published": False,
                },
            ],
            "primary_topic": {
                "id": "https://openalex.org/T10018",
                "display_name": "Density Functional Theory and Molecular Dynamics",
                "score": 0.9998,
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
            },
            "topics": [
                {
                    "id": "https://openalex.org/T10018",
                    "display_name": "Density Functional Theory and Molecular Dynamics",
                    "score": 0.9998,
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
            "counts_by_year": [
                {"year": 2024, "cited_by_count": 2500},
                {"year": 2023, "cited_by_count": 2400},
                {"year": 2022, "cited_by_count": 2300},
                {"year": 2021, "cited_by_count": 2200},
                {"year": 2020, "cited_by_count": 2100},
            ],
            "created_date": "2016-06-24",
            "updated_date": "2024-12-15T13:45:01.169181",
            "ids": {
                "openalex": "https://openalex.org/W2741809807",
                "doi": "https://doi.org/10.1103/physrevlett.77.3865",
                "pmid": "https://pubmed.ncbi.nlm.nih.gov/10062328",
            },
            "indexed_in": ["crossref", "pubmed"],
            "ngrams_url": "https://api.openalex.org/works/W2741809807/ngrams",
        }

    def test_comprehensive_work_creation(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test creating a work with all fields from comprehensive data."""
        work = Work(**comprehensive_work_data)

        # Basic fields
        assert work.id == "https://openalex.org/W2741809807"
        assert work.title == "Generalized Gradient Approximation Made Simple"
        assert work.publication_year == 1996
        assert work.publication_date == date(1996, 10, 28)
        assert work.type == WorkType.ARTICLE
        assert work.type_crossref == "journal-article"

        # Metrics
        assert work.cited_by_count == 50000
        assert work.is_retracted is False
        assert work.is_paratext is False
        assert work.fwci == 25.7

        # Citation percentile
        assert work.citation_normalized_percentile is not None
        assert work.citation_normalized_percentile.value == 0.999969
        assert work.citation_normalized_percentile.is_in_top_1_percent is True
        assert work.citation_normalized_percentile.is_in_top_10_percent is True

        # Open Access
        assert work.is_oa is True
        assert work.open_access.oa_status == OpenAccessStatus.BRONZE
        assert work.open_access.any_repository_has_fulltext is True

        # APC
        assert work.apc_list is not None
        assert work.apc_list.value == 3450
        assert work.apc_list.currency == "USD"
        assert work.apc_paid is None

        # Biblio
        assert work.biblio is not None
        assert work.biblio.volume == "77"
        assert work.biblio.issue == "18"
        assert work.biblio.first_page == "3865"
        assert work.biblio.last_page == "3868"

    def test_authorship_details(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test authorship parsing with various roles."""
        work = Work(**comprehensive_work_data)

        assert len(work.authorships) == 3

        # First author (corresponding)
        first_author = work.authorships[0]
        assert first_author.author_position == "first"
        assert first_author.is_corresponding is True
        assert first_author.author.display_name == "John P. Perdew"
        assert (
            first_author.author.orcid == "https://orcid.org/0000-0003-4237-824X"
        )
        assert len(first_author.institutions) == 1
        assert first_author.institutions[0].display_name == "Tulane University"
        assert first_author.countries == ["US"]
        assert first_author.raw_author_name == "John P. Perdew"

        # Middle author
        middle_author = work.authorships[1]
        assert middle_author.author_position == "middle"
        assert middle_author.is_corresponding is False
        assert middle_author.author.orcid is None

        # Last author
        last_author = work.authorships[2]
        assert last_author.author_position == "last"
        assert last_author.author.display_name == "Matthias Ernzerhof"
        assert last_author.institutions[0].country_code == "CA"

        # Check corresponding IDs
        assert work.corresponding_author_ids == [
            "https://openalex.org/A5023888391"
        ]
        assert work.corresponding_institution_ids == [
            "https://openalex.org/I131249849"
        ]
        assert work.countries_distinct_count == 2

    def test_abstract_reconstruction(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test abstract reconstruction from inverted index."""
        work = Work(**comprehensive_work_data)
        abstract = work.abstract

        assert abstract is not None
        assert abstract.startswith("Generalized gradient approximations")
        assert "exchange-correlation energy" in abstract
        assert "gas." in abstract
        assert len(abstract.split()) > 50  # Substantial abstract

    def test_locations_and_versions(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test multiple locations including repositories."""
        work = Work(**comprehensive_work_data)

        assert work.locations_count == 3
        assert len(work.locations) == 2  # As per the data

        # Primary location (journal)
        primary = work.primary_location
        assert primary is not None
        assert primary.is_oa is True
        assert primary.source.display_name == "Physical Review Letters"
        assert primary.source.type == "journal"
        assert primary.version == "publishedVersion"
        assert primary.is_accepted is True
        assert primary.is_published is True

        # Best OA location
        best_oa = work.best_oa_location
        assert best_oa is not None
        assert best_oa.source.id == primary.source.id

        # Repository location
        repo_location = work.locations[1]
        assert repo_location.source.display_name == "arXiv (Cornell University)"
        assert repo_location.source.type == "repository"
        assert (
            repo_location.pdf_url
            == "https://arxiv.org/pdf/cond-mat/9605139.pdf"
        )
        assert repo_location.license == "cc-by"
        assert repo_location.version == "submittedVersion"

    def test_concepts_and_topics(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test concepts and topics hierarchy."""
        work = Work(**comprehensive_work_data)

        # Concepts
        assert len(work.concepts) == 3
        medicine_concept = work.concepts[0]
        assert medicine_concept.display_name == "Medicine"
        assert medicine_concept.level == 0
        assert medicine_concept.score > 0.9

        # Primary topic
        primary_topic = work.primary_topic
        assert primary_topic is not None
        assert (
            primary_topic.display_name
            == "Density Functional Theory and Molecular Dynamics"
        )
        assert primary_topic.score > 0.99
        assert (
            primary_topic.subfield.display_name
            == "Physical and Theoretical Chemistry"
        )
        assert primary_topic.field.display_name == "Chemistry"
        assert primary_topic.domain.display_name == "Physical Sciences"

        # Topics list
        assert len(work.topics) == 1
        assert work.topics[0].id == primary_topic.id

    def test_mesh_and_keywords(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test MeSH terms and keywords."""
        work = Work(**comprehensive_work_data)

        # MeSH
        assert len(work.mesh) == 1
        mesh_term = work.mesh[0]
        assert mesh_term.descriptor_ui == "D008967"
        assert mesh_term.descriptor_name == "Molecular Structure"
        assert mesh_term.is_major_topic is True

        # Keywords
        assert len(work.keywords) == 2
        keyword_names = [k.display_name for k in work.keywords]
        assert "Density Functional Theory" in keyword_names
        assert all(k.score > 0.5 for k in work.keywords)

    def test_mesh_tag_variations(self) -> None:
        """Test MeSH tag model variations."""
        # Major topic
        mesh_major = MeshTag(
            descriptor_ui="D008967",
            descriptor_name="Molecular Structure",
            qualifier_ui="",
            qualifier_name=None,
            is_major_topic=True,
        )
        assert mesh_major.is_major_topic is True
        assert mesh_major.qualifier_name is None

        # With qualifier
        mesh_qualified = MeshTag(
            descriptor_ui="D001943",
            descriptor_name="Breast Neoplasms",
            qualifier_ui="Q000628",
            qualifier_name="therapy",
            is_major_topic=False,
        )
        assert mesh_qualified.qualifier_ui == "Q000628"
        assert mesh_qualified.qualifier_name == "therapy"

        # Work with multiple MeSH terms
        work_multi_mesh = Work(
            id="W123",
            display_name="Medical Work",
            mesh=[
                {
                    "descriptor_ui": "D001943",
                    "descriptor_name": "Breast Neoplasms",
                    "qualifier_ui": "Q000188",
                    "qualifier_name": "drug therapy",
                    "is_major_topic": True,
                },
                {
                    "descriptor_ui": "D000970",
                    "descriptor_name": "Antineoplastic Agents",
                    "qualifier_ui": "",
                    "qualifier_name": None,
                    "is_major_topic": True,
                },
                {
                    "descriptor_ui": "D006801",
                    "descriptor_name": "Humans",
                    "qualifier_ui": "",
                    "qualifier_name": None,
                    "is_major_topic": False,
                },
            ],
        )
        assert len(work_multi_mesh.mesh) == 3
        major_topics = [m for m in work_multi_mesh.mesh if m.is_major_topic]
        assert len(major_topics) == 2

    def test_grants_and_funders(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test grants parsing."""
        work = Work(**comprehensive_work_data)

        assert len(work.grants) == 1
        grant = work.grants[0]
        assert grant.funder == "https://openalex.org/F4320306076"
        assert grant.funder_display_name == "National Science Foundation"
        assert grant.award_id == "DMR-9521353"

    def test_grant_model_variations(self) -> None:
        """Test Grant model with various scenarios."""
        # Complete grant
        grant_complete = Grant(
            funder="https://openalex.org/F4320306076",
            funder_display_name="National Science Foundation",
            award_id="DMR-9521353",
        )
        assert (
            grant_complete.funder_display_name == "National Science Foundation"
        )
        assert grant_complete.award_id == "DMR-9521353"

        # Minimal grant
        grant_minimal = Grant(funder="F123")
        assert grant_minimal.funder == "F123"
        assert grant_minimal.funder_display_name is None
        assert grant_minimal.award_id is None

        # Work with multiple grants
        work_multi_grant = Work(
            id="W123",
            display_name="Multi-grant Work",
            grants=[
                {
                    "funder": "F1",
                    "funder_display_name": "NSF",
                    "award_id": "12345",
                },
                {
                    "funder": "F2",
                    "funder_display_name": "NIH",
                    "award_id": "67890",
                },
                {
                    "funder": "F3",
                    "funder_display_name": "DOE",
                    "award_id": None,
                },
            ],
        )
        assert len(work_multi_grant.grants) == 3
        assert work_multi_grant.grants[1].funder_display_name == "NIH"
        assert work_multi_grant.grants[2].award_id is None

    def test_sustainable_development_goals(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test SDG parsing."""
        work = Work(**comprehensive_work_data)

        assert len(work.sustainable_development_goals) == 1
        sdg = work.sustainable_development_goals[0]
        assert sdg.display_name == "Affordable and clean energy"
        assert sdg.score == 0.42

    def test_sdg_variations(self) -> None:
        """Test various SDG scenarios."""
        # Work with multiple SDGs
        work_multi_sdg = Work(
            id="W123",
            display_name="Climate Work",
            sustainable_development_goals=[
                {
                    "id": "https://metadata.un.org/sdg/13",
                    "display_name": "Climate action",
                    "score": 0.95,
                },
                {
                    "id": "https://metadata.un.org/sdg/7",
                    "display_name": "Affordable and clean energy",
                    "score": 0.87,
                },
                {
                    "id": "https://metadata.un.org/sdg/11",
                    "display_name": "Sustainable cities and communities",
                    "score": 0.65,
                },
            ],
        )
        assert len(work_multi_sdg.sustainable_development_goals) == 3

        # Check ordering by score
        sdgs = work_multi_sdg.sustainable_development_goals
        assert sdgs[0].score == 0.95
        assert sdgs[1].score == 0.87
        assert sdgs[2].score == 0.65

        # Work with no SDGs
        work_no_sdg = Work(
            id="W456",
            display_name="Pure Math Work",
            sustainable_development_goals=[],
        )
        assert len(work_no_sdg.sustainable_development_goals) == 0

    def test_citation_percentile_variations(self) -> None:
        """Test citation normalized percentile variations."""
        # Top 1% work
        work_top1 = Work(
            id="W123",
            display_name="Highly Cited",
            citation_normalized_percentile={
                "value": 0.999969,
                "is_in_top_1_percent": True,
                "is_in_top_10_percent": True,
            },
        )
        assert work_top1.citation_normalized_percentile.value == 0.999969
        assert (
            work_top1.citation_normalized_percentile.is_in_top_1_percent is True
        )
        assert (
            work_top1.citation_normalized_percentile.is_in_top_10_percent
            is True
        )

        # Top 10% but not top 1%
        work_top10 = Work(
            id="W456",
            display_name="Well Cited",
            citation_normalized_percentile={
                "value": 0.92,
                "is_in_top_1_percent": False,
                "is_in_top_10_percent": True,
            },
        )
        assert work_top10.citation_normalized_percentile.value == 0.92
        assert (
            work_top10.citation_normalized_percentile.is_in_top_1_percent
            is False
        )
        assert (
            work_top10.citation_normalized_percentile.is_in_top_10_percent
            is True
        )

        # Average citation
        work_average = Work(
            id="W789",
            display_name="Average Work",
            citation_normalized_percentile={
                "value": 0.50,
                "is_in_top_1_percent": False,
                "is_in_top_10_percent": False,
            },
        )
        assert work_average.citation_normalized_percentile.value == 0.50
        assert (
            work_average.citation_normalized_percentile.is_in_top_1_percent
            is False
        )
        assert (
            work_average.citation_normalized_percentile.is_in_top_10_percent
            is False
        )

    def test_referenced_and_related_works(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test references and related works."""
        work = Work(**comprehensive_work_data)

        assert work.referenced_works_count == 48
        assert len(work.referenced_works) == 5  # Sample shown
        assert all(
            ref.startswith("https://openalex.org/W")
            for ref in work.referenced_works
        )

        assert len(work.related_works) == 5
        assert all(
            rel.startswith("https://openalex.org/W")
            for rel in work.related_works
        )

    def test_counts_by_year(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test yearly citation counts."""
        work = Work(**comprehensive_work_data)

        assert len(work.counts_by_year) == 5
        assert work.counts_by_year[0].year == 2024
        assert work.counts_by_year[0].cited_by_count == 2500

        # Check descending order
        years = [c.year for c in work.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_edge_cases(self) -> None:
        """Test edge cases and minimal work creation."""
        # Minimal work
        minimal_work = Work(
            id="W123",
            display_name="Test",
        )
        assert minimal_work.title == "Test"
        assert minimal_work.abstract is None
        assert minimal_work.publication_year is None

        # Work with empty lists
        work_empty = Work(
            id="W456",
            display_name="Empty Lists Test",
            authorships=[],
            concepts=[],
            mesh=[],
            keywords=[],
            locations=[],
        )
        assert len(work_empty.authorships) == 0
        assert work_empty.primary_location is None
        assert work_empty.best_oa_location is None

    def test_work_validation_errors(self) -> None:
        """Test validation errors for invalid data."""
        # Missing required field
        with pytest.raises(ValidationError):
            Work()

        # Invalid type
        with pytest.raises(ValidationError):
            Work(id="W123", display_name="Test", type="invalid_type")

        # Invalid date format
        with pytest.raises(ValidationError):
            Work(
                id="W123", display_name="Test", publication_date="invalid-date"
            )

    def test_helper_methods(
        self, comprehensive_work_data: dict[str, Any]
    ) -> None:
        """Test Work helper methods."""
        work = Work(**comprehensive_work_data)

        # Test year-based lookups
        assert work.citations_in_year(2024) == 2500
        assert work.citations_in_year(2019) == 0  # Not in data

        # Test author extraction
        author_names = work.author_names()
        assert len(author_names) == 3
        assert "John P. Perdew" in author_names
        assert "Matthias Ernzerhof" in author_names

        # Test institution extraction
        institution_names = work.institution_names()
        assert "Tulane University" in institution_names
        assert "Université de Montréal" in institution_names

        # Test boolean checks
        assert work.has_fulltext is True
        assert work.has_abstract() is True
        assert work.has_references() is True

    def test_open_access_details(self) -> None:
        """Test various open access scenarios."""
        # Gold OA
        gold_oa_work = Work(
            id="W123",
            display_name="Gold OA Work",
            open_access={
                "is_oa": True,
                "oa_status": "gold",
                "oa_url": "https://example.com/gold.pdf",
                "any_repository_has_fulltext": False,
            },
        )
        assert gold_oa_work.open_access.oa_status == OpenAccessStatus.GOLD

        # Hybrid OA
        hybrid_work = Work(
            id="W456",
            display_name="Hybrid Work",
            open_access={
                "is_oa": True,
                "oa_status": "hybrid",
                "oa_url": "https://example.com/hybrid.pdf",
                "any_repository_has_fulltext": True,
            },
        )
        assert hybrid_work.open_access.oa_status == OpenAccessStatus.HYBRID

        # Closed access
        closed_work = Work(
            id="W789",
            display_name="Closed Work",
            open_access={
                "is_oa": False,
                "oa_status": "closed",
                "oa_url": None,
                "any_repository_has_fulltext": False,
            },
        )
        assert closed_work.is_oa is False
        assert closed_work.open_access.oa_url is None

        # Green OA
        green_oa_work = Work(
            id="W999",
            display_name="Green OA Work",
            open_access={
                "is_oa": True,
                "oa_status": "green",
                "oa_url": "https://arxiv.org/pdf/1234.5678.pdf",
                "any_repository_has_fulltext": True,
            },
        )
        assert green_oa_work.open_access.oa_status == OpenAccessStatus.GREEN
        assert green_oa_work.open_access.any_repository_has_fulltext is True

        # Bronze OA
        bronze_oa_work = Work(
            id="W888",
            display_name="Bronze OA Work",
            open_access={
                "is_oa": True,
                "oa_status": "bronze",
                "oa_url": "https://publisher.com/free-article",
                "any_repository_has_fulltext": False,
            },
        )
        assert bronze_oa_work.open_access.oa_status == OpenAccessStatus.BRONZE

    def test_biblio_details(self) -> None:
        """Test bibliographic information."""
        # Complete biblio
        work_complete = Work(
            id="W123",
            display_name="Complete Biblio",
            biblio={
                "volume": "77",
                "issue": "18",
                "first_page": "3865",
                "last_page": "3868",
            },
        )
        assert work_complete.biblio.volume == "77"
        assert work_complete.biblio.issue == "18"
        assert work_complete.biblio.page_range == "3865-3868"

        # Single page
        work_single_page = Work(
            id="W456",
            display_name="Single Page",
            biblio={"volume": "12", "issue": "3", "first_page": "e12345"},
        )
        assert work_single_page.biblio.page_range == "e12345"

        # No pages
        work_no_pages = Work(
            id="W789", display_name="No Pages", biblio={"volume": "100"}
        )
        assert work_no_pages.biblio.page_range is None

    def test_location_versions(self) -> None:
        """Test different location versions in detail."""
        work = Work(
            id="W123",
            display_name="Multi-version Work",
            locations=[
                {
                    "is_oa": True,
                    "landing_page_url": "https://doi.org/10.1103/physrevlett.77.3865",
                    "pdf_url": None,
                    "source": {
                        "id": "S48139910",
                        "display_name": "Physical Review Letters",
                        "type": "journal",
                    },
                    "license": None,
                    "license_id": None,
                    "version": "publishedVersion",
                    "is_accepted": True,
                    "is_published": True,
                },
                {
                    "is_oa": True,
                    "landing_page_url": "https://arxiv.org/abs/2401.12345",
                    "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
                    "source": {
                        "id": "S4306400194",
                        "display_name": "arXiv",
                        "type": "repository",
                    },
                    "license": "cc-by",
                    "license_id": "https://openalex.org/licenses/cc-by",
                    "version": "submittedVersion",
                    "is_accepted": False,
                    "is_published": False,
                },
                {
                    "is_oa": True,
                    "landing_page_url": "https://repository.edu/handle/123456",
                    "pdf_url": "https://repository.edu/pdf/123456.pdf",
                    "source": {
                        "id": "S999",
                        "display_name": "Institutional Repository",
                        "type": "repository",
                    },
                    "license": "cc-by-nc",
                    "license_id": "https://openalex.org/licenses/cc-by-nc",
                    "version": "acceptedVersion",
                    "is_accepted": True,
                    "is_published": False,
                },
            ],
        )

        # Check all three versions
        assert len(work.locations) == 3

        # Published version
        published = work.locations[0]
        assert published.version == "publishedVersion"
        assert published.is_published is True
        assert published.source.type == "journal"

        # Submitted version
        submitted = work.locations[1]
        assert submitted.version == "submittedVersion"
        assert submitted.is_accepted is False
        assert submitted.pdf_url == "https://arxiv.org/pdf/2401.12345.pdf"

        # Accepted version
        accepted = work.locations[2]
        assert accepted.version == "acceptedVersion"
        assert accepted.is_accepted is True
        assert accepted.is_published is False
        assert accepted.license == "cc-by-nc"

    def test_authorship_edge_cases(self) -> None:
        """Test special authorship scenarios."""
        work = Work(
            id="W123",
            display_name="Special Authorships",
            authorships=[
                {
                    "author_position": "first",
                    "author": {
                        "id": None,
                        "display_name": "Anonymous",
                        "orcid": None,
                    },
                    "institutions": [],
                    "countries": [],
                    "is_corresponding": False,
                    "raw_author_name": "Anonymous",
                    "raw_affiliation_strings": [],
                },
                {
                    "author_position": "group",
                    "author": {
                        "id": None,
                        "display_name": "The COVID-19 Genomics UK (COG-UK) Consortium",
                        "orcid": None,
                    },
                    "institutions": [
                        {
                            "id": "I123",
                            "display_name": "University of Cambridge",
                            "ror": "https://ror.org/013meh722",
                            "country_code": "GB",
                            "type": "education",
                        }
                    ],
                    "countries": ["GB"],
                    "is_corresponding": True,
                    "raw_author_name": "The COVID-19 Genomics UK (COG-UK) Consortium",
                    "raw_affiliation_strings": [
                        "COVID-19 Genomics UK (COG-UK) Consortium"
                    ],
                },
                {
                    "author_position": "last",
                    "author": {
                        "id": "A123",
                        "display_name": "Jane Doe",
                        "orcid": None,
                    },
                    "institutions": [],
                    "countries": ["Unknown"],
                    "is_corresponding": False,
                    "raw_author_name": "Jane Doe",
                    "raw_affiliation_strings": ["Independent Researcher"],
                },
            ],
        )

        # Anonymous author
        anon = work.authorships[0]
        assert anon.author.display_name == "Anonymous"
        assert anon.author.id is None
        assert len(anon.institutions) == 0

        # Consortium authorship
        consortium = work.authorships[1]
        assert "Consortium" in consortium.author.display_name
        assert consortium.author_position == "group"
        assert consortium.is_corresponding is True

        # Independent researcher
        independent = work.authorships[2]
        assert len(independent.institutions) == 0
        assert independent.countries == ["Unknown"]

    def test_apc_details(self) -> None:
        """Test APC (Article Processing Charge) information."""
        # Work with APC paid
        work_apc_paid = Work(
            id="W123",
            display_name="APC Paid Work",
            apc_list={
                "value": 3450,
                "currency": "USD",
                "value_usd": 3450,
                "provenance": "doaj",
            },
            apc_paid={
                "value": 3450,
                "currency": "USD",
                "value_usd": 3450,
                "provenance": "publisher",
            },
        )
        assert work_apc_paid.apc_list.value == 3450
        assert work_apc_paid.apc_list.currency == "USD"
        assert work_apc_paid.apc_paid.provenance == "publisher"

        # Work with different currencies
        work_multi_currency = Work(
            id="W456",
            display_name="Multi-currency APC",
            apc_list={
                "value": 2500,
                "currency": "EUR",
                "value_usd": 2750,
                "provenance": "publisher",
            },
        )
        assert work_multi_currency.apc_list.currency == "EUR"
        assert work_multi_currency.apc_list.value_usd == 2750


def test_work_basefilter_paths() -> None:
    """Validate BaseFilter parameter handling and filter string building."""
    bf_none = WorkBaseFilter(filter=None)
    assert bf_none.filter is None

    bf_str = WorkBaseFilter(filter="foo")
    assert bf_str.filter == "foo"

    bf = WorkBaseFilter(
        filter={"x": 1},
        select="id",
        group_by="type",
        per_page=10,
    )
    params = bf.to_params()
    assert params["filter"] == "x:1"
    assert params["select"] == "id"
    assert params["group-by"] == "type"
    assert params["per-page"] == 10

    built = bf._build_filter_string(
        {"a": None, "b": True, "c": [1, 2], "d": date(2024, 1, 2), "e": "v"}
    )
    assert "b:true" in built
    assert "c:1|2" in built
    assert "d:2024-01-02" in built
    assert "e:v" in built
    assert "a" not in built


def test_work_filter_string_operations() -> None:
    """Ensure Works and Institutions filters accumulate correctly."""
    wf = (
        WorkWorksFilter(filter="raw")
        .with_publication_year(2024)
        .with_type("article")
        .with_open_access()
    )
    assert wf.filter["raw"] == "raw"
    assert wf.filter["publication_year"] == [2024]
    assert wf.filter["type"] == ["article"]
    assert wf.filter["is_oa"] is True

    inf = (
        WorkInstitutionsFilter(filter="start")
        .with_country("US")
        .with_type("education")
    )
    assert inf.filter["raw"] == "start"
    assert inf.filter["country_code"] == ["US"]
    assert inf.filter["type"] == ["education"]
