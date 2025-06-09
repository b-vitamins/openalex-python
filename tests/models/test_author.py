from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    Author,
)


class TestAuthor:
    """Test Author model with comprehensive realistic fixtures."""

    @pytest.fixture
    def comprehensive_author_data(self) -> dict[str, Any]:
        """Comprehensive author data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/A5023888391",
            "orcid": "https://orcid.org/0000-0003-4237-824X",
            "display_name": "John P. Perdew",
            "display_name_alternatives": [
                "J. P. Perdew",
                "J. Perdew",
                "John Perdew",
                "John Patrick Perdew",
            ],
            "works_count": 523,
            "cited_by_count": 154282,
            "summary_stats": {
                "2yr_mean_citedness": 5.234567,
                "h_index": 126,
                "i10_index": 487,
            },
            "last_known_institution": {
                "id": "https://openalex.org/I131249849",
                "ror": "https://ror.org/04v7hvq31",
                "display_name": "Tulane University",
                "country_code": "US",
                "type": "education",
                "lineage": ["https://openalex.org/I131249849"],
            },
            "last_known_institutions": [
                {
                    "id": "https://openalex.org/I131249849",
                    "ror": "https://ror.org/04v7hvq31",
                    "display_name": "Tulane University",
                    "country_code": "US",
                    "type": "education",
                    "lineage": ["https://openalex.org/I131249849"],
                }
            ],
            "affiliations": [
                {
                    "institution": {
                        "id": "https://openalex.org/I131249849",
                        "ror": "https://ror.org/04v7hvq31",
                        "display_name": "Tulane University",
                        "country_code": "US",
                        "type": "education",
                        "lineage": ["https://openalex.org/I131249849"],
                    },
                    "years": [
                        2024,
                        2023,
                        2022,
                        2021,
                        2020,
                        2019,
                        2018,
                        2017,
                        2016,
                        2015,
                    ],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I1308891854",
                        "ror": "https://ror.org/02z0cw294",
                        "display_name": "Temple University",
                        "country_code": "US",
                        "type": "education",
                        "lineage": ["https://openalex.org/I1308891854"],
                    },
                    "years": [2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007],
                },
            ],
            "x_concepts": [
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 98.7,
                },
                {
                    "id": "https://openalex.org/C62520636",
                    "wikidata": "https://www.wikidata.org/wiki/Q944",
                    "display_name": "Quantum mechanics",
                    "level": 1,
                    "score": 89.3,
                },
                {
                    "id": "https://openalex.org/C185592680",
                    "wikidata": "https://www.wikidata.org/wiki/Q2329",
                    "display_name": "Chemistry",
                    "level": 0,
                    "score": 72.8,
                },
            ],
            "counts_by_year": [
                {"year": 2024, "works_count": 8, "cited_by_count": 6234},
                {"year": 2023, "works_count": 12, "cited_by_count": 6892},
                {"year": 2022, "works_count": 15, "cited_by_count": 7234},
                {"year": 2021, "works_count": 10, "cited_by_count": 6987},
                {"year": 2020, "works_count": 14, "cited_by_count": 6543},
            ],
            "ids": {
                "openalex": "https://openalex.org/A5023888391",
                "orcid": "https://orcid.org/0000-0003-4237-824X",
                "scopus": "http://www.scopus.com/inward/authorDetails.url?authorID=7005929454&partnerID=MN8TOARS",
            },
            "created_date": "2023-07-21",
            "updated_date": "2024-12-16T09:27:51.699330",
        }

    @pytest.fixture
    def minimal_author_data(self) -> dict[str, Any]:
        """Minimal author data for edge case testing."""
        return {
            "id": "https://openalex.org/A5000000001",
            "display_name": "Unknown Author",
            "works_count": 0,
            "cited_by_count": 0,
        }

    @pytest.fixture
    def author_with_multiple_affiliations_data(self) -> dict[str, Any]:
        """Author with complex affiliation history."""
        return {
            "id": "https://openalex.org/A5100000001",
            "display_name": "Marie Curie",
            "orcid": None,
            "works_count": 250,
            "cited_by_count": 50000,
            "summary_stats": {
                "2yr_mean_citedness": 3.5,
                "h_index": 85,
                "i10_index": 225,
            },
            "affiliations": [
                {
                    "institution": {
                        "id": "https://openalex.org/I39804081",
                        "ror": "https://ror.org/04gyf1771",
                        "display_name": "University of Paris",
                        "country_code": "FR",
                        "type": "education",
                        "lineage": ["https://openalex.org/I39804081"],
                    },
                    "years": [1906, 1905, 1904, 1903, 1902, 1901, 1900],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I86519309",
                        "ror": "https://ror.org/01y0t3r11",
                        "display_name": "École Normale Supérieure",
                        "country_code": "FR",
                        "type": "education",
                        "lineage": [
                            "https://openalex.org/I86519309",
                            "https://openalex.org/I1320320797",
                        ],
                    },
                    "years": [1899, 1898, 1897, 1896],
                },
                {
                    "institution": {
                        "id": "https://openalex.org/I3124963559",
                        "ror": "https://ror.org/00za53h95",
                        "display_name": "Radium Institute",
                        "country_code": "FR",
                        "type": "facility",
                        "lineage": [
                            "https://openalex.org/I3124963559",
                            "https://openalex.org/I39804081",
                        ],
                    },
                    "years": [1911, 1910, 1909, 1908, 1907],
                },
            ],
            "last_known_institutions": [
                {
                    "id": "https://openalex.org/I3124963559",
                    "ror": "https://ror.org/00za53h95",
                    "display_name": "Radium Institute",
                    "country_code": "FR",
                    "type": "facility",
                    "lineage": [
                        "https://openalex.org/I3124963559",
                        "https://openalex.org/I39804081",
                    ],
                },
                {
                    "id": "https://openalex.org/I39804081",
                    "ror": "https://ror.org/04gyf1771",
                    "display_name": "University of Paris",
                    "country_code": "FR",
                    "type": "education",
                    "lineage": ["https://openalex.org/I39804081"],
                },
            ],
            "counts_by_year": [
                {"year": 1911, "works_count": 5, "cited_by_count": 120},
                {"year": 1910, "works_count": 8, "cited_by_count": 98},
                {"year": 1909, "works_count": 6, "cited_by_count": 87},
                {"year": 1908, "works_count": 4, "cited_by_count": 65},
                {"year": 1907, "works_count": 7, "cited_by_count": 72},
            ],
            "ids": {
                "openalex": "https://openalex.org/A5100000001",
                "wikidata": "https://www.wikidata.org/wiki/Q7186",
                "wikipedia": "https://en.wikipedia.org/wiki/Marie_Curie",
            },
        }

    def test_comprehensive_author_creation(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test creating an author with all fields from comprehensive data."""
        author = Author(**comprehensive_author_data)

        # Basic fields
        assert author.id == "https://openalex.org/A5023888391"
        assert author.display_name == "John P. Perdew"
        assert str(author.orcid) == "https://orcid.org/0000-0003-4237-824X"

        # Alternative names
        assert len(author.display_name_alternatives) == 4
        assert "J. P. Perdew" in author.display_name_alternatives
        assert "John Patrick Perdew" in author.display_name_alternatives

        # Metrics
        assert author.works_count == 523
        assert author.cited_by_count == 154282

        # Summary stats
        assert author.summary_stats is not None
        assert author.summary_stats.two_year_mean_citedness == 5.234567
        assert author.h_index == 126
        assert author.i10_index == 487

    def test_author_affiliations(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test author affiliations parsing."""
        author = Author(**comprehensive_author_data)

        assert len(author.affiliations) == 2

        # Current affiliation
        current_aff = author.affiliations[0]
        assert current_aff.institution.display_name == "Tulane University"
        assert current_aff.institution.country_code == "US"
        assert 2024 in current_aff.years
        assert 2015 in current_aff.years
        assert len(current_aff.years) == 10

        # Previous affiliation
        prev_aff = author.affiliations[1]
        assert prev_aff.institution.display_name == "Temple University"
        assert 2014 in prev_aff.years
        assert 2007 in prev_aff.years

    def test_last_known_institution(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test last known institution fields."""
        author = Author(**comprehensive_author_data)

        # Single last known institution
        assert author.last_known_institution is not None
        assert author.last_known_institution.display_name == "Tulane University"
        assert author.last_known_institution.type == "education"

        # List of last known institutions
        assert len(author.last_known_institutions) == 1
        assert (
            author.last_known_institutions[0].id
            == author.last_known_institution.id
        )

    def test_author_concepts(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test author concepts/topics."""
        author = Author(**comprehensive_author_data)

        assert len(author.x_concepts) == 3

        # Physics concept
        physics = author.x_concepts[0]
        assert physics.display_name == "Physics"
        assert physics.level == 0
        assert physics.score == 98.7

        # Check concept hierarchy
        quantum = author.x_concepts[1]
        assert quantum.display_name == "Quantum mechanics"
        assert quantum.level == 1  # Sub-concept of physics

    def test_author_counts_by_year(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test yearly publication and citation counts."""
        author = Author(**comprehensive_author_data)

        assert len(author.counts_by_year) == 5

        # Most recent year
        recent = author.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 8
        assert recent.cited_by_count == 6234

        # Verify descending order
        years = [c.year for c in author.counts_by_year]
        assert years == sorted(years, reverse=True)

    def test_author_ids(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test author external identifiers."""
        author = Author(**comprehensive_author_data)

        assert author.ids is not None
        assert author.ids.openalex == "https://openalex.org/A5023888391"
        assert author.ids.orcid == "https://orcid.org/0000-0003-4237-824X"
        assert "scopus.com" in author.ids.scopus

    def test_minimal_author(self, minimal_author_data: dict[str, Any]) -> None:
        """Test author with minimal data."""
        author = Author(**minimal_author_data)

        assert author.display_name == "Unknown Author"
        assert author.works_count == 0
        assert author.cited_by_count == 0
        assert author.orcid is None
        assert author.summary_stats is None
        assert len(author.affiliations) == 0
        assert author.last_known_institution is None

    def test_author_with_multiple_affiliations(
        self, author_with_multiple_affiliations_data: dict[str, Any]
    ) -> None:
        """Test author with complex affiliation history."""
        author = Author(**author_with_multiple_affiliations_data)

        assert len(author.affiliations) == 3

        # Check chronological order of affiliations
        radium_years = author.affiliations[2].years
        assert 1911 in radium_years
        assert 1907 in radium_years

        # Multiple last known institutions
        assert len(author.last_known_institutions) == 2
        institution_names = [
            inst.display_name for inst in author.last_known_institutions
        ]
        assert "Radium Institute" in institution_names
        assert "University of Paris" in institution_names

        # Check lineage
        ens_affiliation = author.affiliations[1]
        assert len(ens_affiliation.institution.lineage) == 2

    def test_author_helper_methods(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test Author helper methods."""
        author = Author(**comprehensive_author_data)

        # Test year-based lookups
        assert author.works_in_year(2024) == 8
        assert author.citations_in_year(2023) == 6892
        assert author.works_in_year(2019) == 0  # Not in data

        # Test active years
        active_years = author.active_years()
        assert 2024 in active_years
        assert 2020 in active_years
        assert len(active_years) == 5

        # Test institution names
        inst_names = author.institution_names()
        assert "Tulane University" in inst_names
        assert "Temple University" in inst_names

        # Test current institutions
        current_insts = author.current_institutions()
        assert len(current_insts) == 1
        assert current_insts[0].display_name == "Tulane University"

    def test_author_validation_errors(self) -> None:
        """Test validation errors for invalid author data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Author()

        # Invalid ORCID format
        with pytest.raises(ValidationError):
            Author(id="A123", display_name="Test", orcid="invalid-orcid")

        # Negative counts
        with pytest.raises(ValidationError):
            Author(id="A123", display_name="Test", works_count=-1)

    def test_author_edge_cases(self) -> None:
        """Test edge cases in author data."""
        # Author with no ORCID but other IDs
        author = Author(
            id="A123",
            display_name="Test Author",
            ids={
                "openalex": "A123",
                "scopus": "http://scopus.com/123",
                "orcid": None,
            },
        )
        assert author.orcid is None
        assert author.ids.scopus is not None

        # Author with empty lists
        author_empty = Author(
            id="A456",
            display_name="Empty Author",
            display_name_alternatives=[],
            affiliations=[],
            x_concepts=[],
            counts_by_year=[],
        )
        assert len(author_empty.display_name_alternatives) == 0
        assert author_empty.active_years() == []
        assert author_empty.institution_names() == []

    def test_summary_stats_properties(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test summary stats property access."""
        author = Author(**comprehensive_author_data)

        # Direct property access
        assert author.h_index == 126
        assert author.i10_index == 487
        assert author.two_year_mean_citedness == 5.234567

        # Author without summary stats
        author_no_stats = Author(id="A789", display_name="No Stats Author")
        assert author_no_stats.h_index is None
        assert author_no_stats.i10_index is None
        assert author_no_stats.two_year_mean_citedness is None

    def test_datetime_fields(
        self, comprehensive_author_data: dict[str, Any]
    ) -> None:
        """Test datetime field parsing."""
        author = Author(**comprehensive_author_data)

        assert isinstance(author.created_date, str)
        assert author.created_date == "2023-07-21"

        assert isinstance(author.updated_date, datetime)
        assert author.updated_date.year == 2024
        assert author.updated_date.month == 12
