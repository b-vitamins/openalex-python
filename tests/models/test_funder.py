from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import Funder


class TestFunder:
    """Test Funder model with comprehensive realistic fixtures."""

    @pytest.fixture
    def government_funder_data(self) -> dict[str, Any]:
        """Government funder data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/F4320306076",
            "display_name": "National Science Foundation",
            "alternate_titles": [
                "NSF",
                "US National Science Foundation",
                "United States National Science Foundation",
            ],
            "country_code": "US",
            "description": "The National Science Foundation (NSF) is an independent agency of the United States government that supports fundamental research and education in all the non-medical fields of science and engineering.",
            "homepage_url": "https://www.nsf.gov/",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/NSF_logo.png/320px-NSF_logo.png",
            "image_thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/NSF_logo.png/160px-NSF_logo.png",
            "grants_count": 543210,
            "works_count": 1234567,
            "cited_by_count": 45678901,
            "summary_stats": {
                "2yr_mean_citedness": 4.567,
                "h_index": 456,
                "i10_index": 234567,
            },
            "counts_by_year": [
                {"year": 2024, "works_count": 45678, "cited_by_count": 2345678},
                {"year": 2023, "works_count": 44567, "cited_by_count": 2234567},
                {"year": 2022, "works_count": 43456, "cited_by_count": 2123456},
                {"year": 2021, "works_count": 42345, "cited_by_count": 2012345},
                {"year": 2020, "works_count": 41234, "cited_by_count": 1901234},
            ],
            "roles": [
                {
                    "role": "funder",
                    "id": "https://openalex.org/F4320306076",
                    "works_count": 1234567,
                },
                {
                    "role": "institution",
                    "id": "https://openalex.org/I135310074",
                    "works_count": 12345,
                },
            ],
            "ids": {
                "openalex": "https://openalex.org/F4320306076",
                "ror": "https://ror.org/021nxhr62",
                "wikidata": "https://www.wikidata.org/wiki/Q304878",
                "crossref": "100000001",
                "doi": "https://doi.org/10.13039/100000001",
            },
            "created_date": "2023-01-01",
            "updated_date": "2024-12-16T13:45:67.890123",
        }

    @pytest.fixture
    def private_foundation_data(self) -> dict[str, Any]:
        """Private foundation funder data."""
        return {
            "id": "https://openalex.org/F4320306079",
            "display_name": "Bill & Melinda Gates Foundation",
            "alternate_titles": [
                "Gates Foundation",
                "BMGF",
                "Bill and Melinda Gates Foundation",
            ],
            "country_code": "US",
            "description": "The Bill & Melinda Gates Foundation is an American private foundation founded by Bill Gates and Melinda French Gates.",
            "homepage_url": "https://www.gatesfoundation.org/",
            "grants_count": 87654,
            "works_count": 234567,
            "cited_by_count": 8901234,
            "counts_by_year": [
                {"year": 2024, "works_count": 8901, "cited_by_count": 456789}
            ],
            "roles": [
                {
                    "role": "funder",
                    "id": "https://openalex.org/F4320306079",
                    "works_count": 234567,
                }
            ],
            "ids": {
                "openalex": "https://openalex.org/F4320306079",
                "ror": "https://ror.org/0456r8d26",
                "wikidata": "https://www.wikidata.org/wiki/Q334105",
                "crossref": "100000865",
                "doi": "https://doi.org/10.13039/100000865",
            },
        }

    @pytest.fixture
    def european_funder_data(self) -> dict[str, Any]:
        """European research council funder data."""
        return {
            "id": "https://openalex.org/F4320306101",
            "display_name": "European Research Council",
            "alternate_titles": [
                "ERC",
                "Conseil Européen de la Recherche",
                "Consejo Europeo de Investigación",
            ],
            "country_code": "BE",
            "description": "The European Research Council (ERC) is a public body for funding of scientific and technological research conducted within the European Union.",
            "homepage_url": "https://erc.europa.eu/",
            "grants_count": 65432,
            "works_count": 345678,
            "cited_by_count": 12345678,
            "summary_stats": {
                "2yr_mean_citedness": 5.123,
                "h_index": 234,
                "i10_index": 98765,
            },
            "counts_by_year": [
                {"year": 2024, "works_count": 12345, "cited_by_count": 567890},
                {"year": 2023, "works_count": 11234, "cited_by_count": 534567},
            ],
            "roles": [
                {
                    "role": "funder",
                    "id": "https://openalex.org/F4320306101",
                    "works_count": 345678,
                }
            ],
            "ids": {
                "openalex": "https://openalex.org/F4320306101",
                "ror": "https://ror.org/0472cxd90",
                "wikidata": "https://www.wikidata.org/wiki/Q1376517",
                "crossref": "501100000781",
                "doi": "https://doi.org/10.13039/501100000781",
            },
        }

    def test_government_funder_creation(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test creating a government funder with all fields."""
        funder = Funder(**government_funder_data)

        # Basic fields
        assert funder.id == "https://openalex.org/F4320306076"
        assert funder.display_name == "National Science Foundation"
        assert funder.country_code == "US"
        assert "independent agency" in funder.description

        # URLs
        assert str(funder.homepage_url) == "https://www.nsf.gov/"
        assert "NSF_logo.png" in str(funder.image_url)
        assert "160px" in str(funder.image_thumbnail_url)

        # Metrics
        assert funder.grants_count == 543210
        assert funder.works_count == 1234567
        assert funder.cited_by_count == 45678901

        # Helper methods
        assert funder.is_government_funder() is True
        assert funder.funding_per_work == pytest.approx(0.44, rel=0.01)

    def test_funder_alternate_titles(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test funder alternate titles."""
        funder = Funder(**government_funder_data)

        assert len(funder.alternate_titles) == 3
        assert "NSF" in funder.alternate_titles
        assert "US National Science Foundation" in funder.alternate_titles

    def test_funder_summary_stats(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test funder summary statistics."""
        funder = Funder(**government_funder_data)

        assert funder.summary_stats is not None
        assert funder.summary_stats.two_year_mean_citedness == 4.567
        assert funder.summary_stats.h_index == 456
        assert funder.summary_stats.i10_index == 234567

    def test_funder_counts_by_year(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test yearly counts."""
        funder = Funder(**government_funder_data)

        assert len(funder.counts_by_year) == 5

        recent = funder.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 45678
        assert recent.cited_by_count == 2345678

    def test_funder_roles(self, government_funder_data: dict[str, Any]) -> None:
        """Test funder roles."""
        funder = Funder(**government_funder_data)

        assert len(funder.roles) == 2

        # Funder role
        funder_role = funder.roles[0]
        assert funder_role.role == "funder"
        assert funder_role.works_count == 1234567

        # Institution role
        inst_role = funder.roles[1]
        assert inst_role.role == "institution"
        assert inst_role.id == "https://openalex.org/I135310074"

    def test_funder_ids(self, government_funder_data: dict[str, Any]) -> None:
        """Test funder external identifiers."""
        funder = Funder(**government_funder_data)

        assert funder.ids is not None
        assert funder.ids.openalex == funder.id
        assert str(funder.ids.ror) == "https://ror.org/021nxhr62"
        assert "wikidata.org" in str(funder.ids.wikidata)
        assert funder.ids.crossref == "100000001"
        assert str(funder.ids.doi) == "https://doi.org/10.13039/100000001"

    def test_private_foundation(
        self, private_foundation_data: dict[str, Any]
    ) -> None:
        """Test private foundation funder."""
        funder = Funder(**private_foundation_data)

        assert funder.display_name == "Bill & Melinda Gates Foundation"
        assert "Gates Foundation" in funder.alternate_titles
        assert funder.is_government_funder() is False

        # Only funder role
        assert len(funder.roles) == 1
        assert funder.roles[0].role == "funder"

    def test_european_funder(
        self, european_funder_data: dict[str, Any]
    ) -> None:
        """Test European funder with multilingual names."""
        funder = Funder(**european_funder_data)

        assert funder.country_code == "BE"
        assert "ERC" in funder.alternate_titles
        assert "Conseil Européen de la Recherche" in funder.alternate_titles

        # EU funders often have government-like status
        assert "European Union" in funder.description

    def test_funder_helper_methods(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test funder helper methods."""
        funder = Funder(**government_funder_data)

        # Year-based lookups
        assert funder.works_in_year(2024) == 45678
        assert funder.citations_in_year(2023) == 2234567
        assert funder.works_in_year(2019) == 0  # Not in data

        # Active years
        active_years = funder.active_years()
        assert 2024 in active_years
        assert len(active_years) == 5

        # Funding metrics
        assert funder.funding_per_work == pytest.approx(0.44, rel=0.01)

    def test_funder_no_works(self) -> None:
        """Test funder with grants but no works."""
        funder = Funder(
            id="F123",
            display_name="New Funder",
            grants_count=100,
            works_count=0,
        )

        assert funder.funding_per_work is None  # Avoid division by zero

    def test_minimal_funder(self) -> None:
        """Test funder with minimal data."""
        funder = Funder(id="F456", display_name="Minimal Funder")

        assert funder.country_code is None
        assert funder.description is None
        assert funder.grants_count == 0
        assert funder.works_count == 0
        assert len(funder.roles) == 0

    def test_funder_validation_errors(self) -> None:
        """Test validation errors for invalid funder data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Funder()

        # Invalid country code
        with pytest.raises(ValidationError):
            Funder(
                id="F123",
                display_name="Test",
                country_code="ZZZ",  # Not a valid ISO code
            )

        # Negative counts
        with pytest.raises(ValidationError):
            Funder(id="F123", display_name="Test", grants_count=-1)

    def test_funder_edge_cases(self) -> None:
        """Test edge cases in funder data."""
        # Funder with empty lists
        funder = Funder(
            id="F789",
            display_name="Empty Funder",
            alternate_titles=[],
            counts_by_year=[],
            roles=[],
        )

        assert funder.active_years() == []
        assert funder.is_government_funder() is False

        # Funder with very long name
        long_name = "The " + "Very " * 20 + "Long Named Foundation"
        funder_long = Funder(id="F999", display_name=long_name)
        assert len(funder_long.display_name) > 100

    def test_datetime_fields(
        self, government_funder_data: dict[str, Any]
    ) -> None:
        """Test datetime field parsing."""
        funder = Funder(**government_funder_data)

        assert isinstance(funder.created_date, str)
        assert funder.created_date == "2023-01-01"

        assert isinstance(funder.updated_date, datetime)
        assert funder.updated_date.year == 2024
