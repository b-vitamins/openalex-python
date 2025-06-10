from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from openalex.models import (
    APCPrice,
    Society,
    Source,
    SourceType,
)


class TestSource:
    """Test Source model with comprehensive realistic fixtures."""

    @pytest.fixture()
    def journal_source_data(self) -> dict[str, Any]:
        """Comprehensive journal source data based on real OpenAlex API response."""
        return {
            "id": "https://openalex.org/S48139910",
            "issn_l": "0031-9007",
            "issn": ["0031-9007", "1079-7114", "1092-0145"],
            "display_name": "Physical Review Letters",
            "host_organization": "https://openalex.org/P4310320017",
            "host_organization_name": "American Physical Society",
            "host_organization_lineage": ["https://openalex.org/P4310320017"],
            "works_count": 198234,
            "cited_by_count": 14526781,
            "summary_stats": {
                "2yr_mean_citedness": 6.842105263157895,
                "h_index": 678,
                "i10_index": 156789,
            },
            "is_oa": False,
            "is_in_doaj": False,
            "is_core": True,
            "type": "journal",
            "homepage_url": "https://journals.aps.org/prl/",
            "apc_prices": [
                {"price": 3500, "currency": "USD"},
                {"price": 3200, "currency": "EUR"},
                {"price": 2800, "currency": "GBP"},
            ],
            "apc_usd": 3500,
            "country_code": "US",
            "societies": [
                {
                    "id": "https://openalex.org/S4210206760",
                    "display_name": "American Physical Society",
                    "url": "https://www.aps.org/",
                    "organization": "American Physical Society",
                }
            ],
            "alternate_titles": ["Phys. Rev. Lett.", "Phys Rev Lett", "PRL"],
            "abbreviated_title": "Phys. Rev. Lett.",
            "x_concepts": [
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 95.7,
                },
                {
                    "id": "https://openalex.org/C62520636",
                    "wikidata": "https://www.wikidata.org/wiki/Q944",
                    "display_name": "Quantum mechanics",
                    "level": 1,
                    "score": 67.3,
                },
                {
                    "id": "https://openalex.org/C185592680",
                    "wikidata": "https://www.wikidata.org/wiki/Q2329",
                    "display_name": "Chemistry",
                    "level": 0,
                    "score": 45.2,
                },
            ],
            "counts_by_year": [
                {"year": 2024, "works_count": 3456, "cited_by_count": 567890},
                {"year": 2023, "works_count": 4123, "cited_by_count": 678901},
                {"year": 2022, "works_count": 3987, "cited_by_count": 654321},
                {"year": 2021, "works_count": 3876, "cited_by_count": 598765},
                {"year": 2020, "works_count": 3654, "cited_by_count": 543210},
            ],
            "works_api_url": "https://api.openalex.org/works?filter=primary_location.source.id:S48139910",
            "ids": {
                "openalex": "https://openalex.org/S48139910",
                "issn_l": "0031-9007",
                "issn": ["0031-9007", "1079-7114", "1092-0145"],
                "mag": "48139910",
                "wikidata": "https://www.wikidata.org/wiki/Q2018386",
                "fatcat": "https://fatcat.wiki/container/3zzw2xvgkjanjgltprf4xmefle",
            },
            "created_date": "2016-06-24",
            "updated_date": "2024-12-16T10:12:34.567890",
        }

    @pytest.fixture()
    def repository_source_data(self) -> dict[str, Any]:
        """Repository source data."""
        return {
            "id": "https://openalex.org/S4306400194",
            "issn_l": None,
            "issn": None,
            "display_name": "arXiv (Cornell University)",
            "host_organization": "https://openalex.org/I205783295",
            "host_organization_name": "Cornell University",
            "host_organization_lineage": ["https://openalex.org/I205783295"],
            "works_count": 2345678,
            "cited_by_count": 34567890,
            "is_oa": True,
            "is_in_doaj": False,
            "is_core": False,
            "type": "repository",
            "homepage_url": "https://arxiv.org/",
            "apc_prices": [],
            "apc_usd": None,
            "country_code": "US",
            "societies": [],
            "alternate_titles": ["arXiv.org", "arXiv e-prints"],
            "abbreviated_title": None,
            "x_concepts": [
                {
                    "id": "https://openalex.org/C121332964",
                    "wikidata": "https://www.wikidata.org/wiki/Q413",
                    "display_name": "Physics",
                    "level": 0,
                    "score": 78.9,
                },
                {
                    "id": "https://openalex.org/C41008148",
                    "wikidata": "https://www.wikidata.org/wiki/Q21198",
                    "display_name": "Computer science",
                    "level": 0,
                    "score": 65.4,
                },
            ],
            "ids": {
                "openalex": "https://openalex.org/S4306400194",
                "fatcat": "https://fatcat.wiki/container/xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            },
        }

    @pytest.fixture()
    def conference_source_data(self) -> dict[str, Any]:
        """Conference source data."""
        return {
            "id": "https://openalex.org/S4306418093",
            "issn_l": "2161-8313",
            "issn": ["2161-8313"],
            "display_name": "International Conference on Learning Representations",
            "host_organization": None,
            "host_organization_name": None,
            "host_organization_lineage": [],
            "works_count": 5432,
            "cited_by_count": 234567,
            "is_oa": True,
            "is_in_doaj": False,
            "is_core": False,
            "type": "conference",
            "homepage_url": "https://iclr.cc/",
            "apc_prices": [],
            "apc_usd": None,
            "country_code": None,
            "societies": [],
            "alternate_titles": ["ICLR"],
            "abbreviated_title": "ICLR",
            "counts_by_year": [
                {"year": 2024, "works_count": 789, "cited_by_count": 45678},
                {"year": 2023, "works_count": 712, "cited_by_count": 38901},
                {"year": 2022, "works_count": 689, "cited_by_count": 32456},
            ],
        }

    @pytest.fixture()
    def ebook_platform_source_data(self) -> dict[str, Any]:
        """E-book platform source data."""
        return {
            "id": "https://openalex.org/S4306401843",
            "issn_l": None,
            "issn": [],
            "display_name": "Springer eBooks",
            "host_organization": "https://openalex.org/P4310319965",
            "host_organization_name": "Springer Nature",
            "host_organization_lineage": ["https://openalex.org/P4310319965"],
            "works_count": 345678,
            "cited_by_count": 4567890,
            "is_oa": False,
            "is_in_doaj": False,
            "is_core": False,
            "type": "ebook-platform",
            "homepage_url": "https://link.springer.com/",
            "country_code": "DE",
            "alternate_titles": [],
        }

    def test_journal_source_creation(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test creating a journal source with all fields."""
        source = Source(**journal_source_data)

        # Basic fields
        assert source.id == "https://openalex.org/S48139910"
        assert source.display_name == "Physical Review Letters"
        assert source.issn_l == "0031-9007"
        assert len(source.issn) == 3
        assert "1079-7114" in source.issn

        # Type and flags
        assert source.type == SourceType.JOURNAL
        assert source.is_journal is True
        assert source.is_repository is False
        assert source.is_conference is False
        assert source.is_oa is False
        assert source.is_in_doaj is False
        assert source.is_core is True

        # Host organization
        assert source.host_organization == "https://openalex.org/P4310320017"
        assert source.host_organization_name == "American Physical Society"
        assert len(source.host_organization_lineage) == 1

        # Metrics
        assert source.works_count == 198234
        assert source.cited_by_count == 14526781

    def test_journal_apc_prices(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test APC (Article Processing Charge) prices."""
        source = Source(**journal_source_data)

        assert len(source.apc_prices) == 3
        assert source.apc_usd == 3500
        assert source.has_apc is True

        # Individual prices
        usd_price = source.apc_prices[0]
        assert usd_price.price == 3500
        assert usd_price.currency == "USD"

        eur_price = source.apc_prices[1]
        assert eur_price.price == 3200
        assert eur_price.currency == "EUR"

        gbp_price = source.apc_prices[2]
        assert gbp_price.price == 2800
        assert gbp_price.currency == "GBP"

        # Helper method
        assert source.get_apc_in_currency("USD") == 3500
        assert source.get_apc_in_currency("EUR") == 3200
        assert source.get_apc_in_currency("GBP") == 2800
        assert source.get_apc_in_currency("JPY") is None
        assert source.get_apc_in_currency("CAD") is None

    def test_apc_price_model(self) -> None:
        """Test APCPrice model directly."""
        # Standard APC price
        price = APCPrice(price=3500, currency="USD")
        assert price.price == 3500
        assert price.currency == "USD"

        # Different currencies
        eur_price = APCPrice(price=3200, currency="EUR")
        assert eur_price.currency == "EUR"

        # Zero price (some journals have zero APC)
        free_price = APCPrice(price=0, currency="USD")
        assert free_price.price == 0

        # High price
        high_price = APCPrice(price=10000, currency="USD")
        assert high_price.price == 10000

    def test_journal_societies(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test society affiliations."""
        source = Source(**journal_source_data)

        assert len(source.societies) == 1
        society = source.societies[0]
        assert society.display_name == "American Physical Society"
        assert str(society.url) == "https://www.aps.org/"
        assert society.organization == "American Physical Society"

    def test_society_model(self) -> None:
        """Test Society model directly."""
        # Complete society
        society = Society(
            id="https://openalex.org/S4210206760",
            display_name="American Physical Society",
            url="https://www.aps.org/",
            organization="American Physical Society",
        )
        assert society.id == "https://openalex.org/S4210206760"
        assert society.display_name == "American Physical Society"
        assert str(society.url) == "https://www.aps.org/"
        assert society.organization == "American Physical Society"

        # Society with minimal data
        minimal_society = Society(id="S123", display_name="Test Society")
        assert minimal_society.url is None
        assert minimal_society.organization is None

        # Multiple societies for a source
        source_multi_society = Source(
            id="S999",
            display_name="Multi-Society Journal",
            societies=[
                {
                    "id": "S1",
                    "display_name": "Society A",
                    "url": "https://societya.org/",
                    "organization": "Society A Organization",
                },
                {
                    "id": "S2",
                    "display_name": "Society B",
                    "url": "https://societyb.org/",
                    "organization": "Society B Organization",
                },
            ],
        )
        assert len(source_multi_society.societies) == 2
        assert source_multi_society.societies[0].display_name == "Society A"
        assert source_multi_society.societies[1].display_name == "Society B"

    def test_journal_alternate_titles(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test alternate titles and abbreviations."""
        source = Source(**journal_source_data)

        assert len(source.alternate_titles) == 3
        assert "Phys. Rev. Lett." in source.alternate_titles
        assert "PRL" in source.alternate_titles
        assert source.abbreviated_title == "Phys. Rev. Lett."

    def test_journal_concepts(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test associated concepts."""
        source = Source(**journal_source_data)

        assert len(source.x_concepts) == 3

        # Top concept
        physics = source.x_concepts[0]
        assert physics.display_name == "Physics"
        assert physics.score == 95.7
        assert physics.level == 0

    def test_journal_summary_stats(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test summary statistics."""
        source = Source(**journal_source_data)

        assert source.summary_stats is not None
        assert source.summary_stats.two_year_mean_citedness == 6.842105263157895
        assert source.summary_stats.h_index == 678
        assert source.summary_stats.i10_index == 156789

    def test_journal_counts_by_year(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test yearly publication and citation counts."""
        source = Source(**journal_source_data)

        assert len(source.counts_by_year) == 5

        recent = source.counts_by_year[0]
        assert recent.year == 2024
        assert recent.works_count == 3456
        assert recent.cited_by_count == 567890

    def test_journal_ids(self, journal_source_data: dict[str, Any]) -> None:
        """Test external identifiers."""
        source = Source(**journal_source_data)

        assert source.ids is not None
        assert source.ids.openalex == source.id
        assert source.ids.issn_l == "0031-9007"
        assert len(source.ids.issn) == 3
        assert source.ids.mag == "48139910"
        assert "wikidata.org" in str(source.ids.wikidata)
        assert "fatcat.wiki" in str(source.ids.fatcat)

    def test_repository_source(
        self, repository_source_data: dict[str, Any]
    ) -> None:
        """Test repository type source."""
        source = Source(**repository_source_data)

        # Basic properties
        assert source.type == SourceType.REPOSITORY
        assert source.is_repository is True
        assert source.is_journal is False
        assert source.is_oa is True

        # No ISSN for repositories
        assert source.issn_l is None
        assert source.issn == []
        assert source.all_issns() == []

        # No APC
        assert len(source.apc_prices) == 0
        assert source.apc_usd is None
        assert source.has_apc is False

        # Host organization
        assert source.host_organization_name == "Cornell University"

    def test_conference_source(
        self, conference_source_data: dict[str, Any]
    ) -> None:
        """Test conference type source."""
        source = Source(**conference_source_data)

        assert source.type == SourceType.CONFERENCE
        assert source.is_conference is True
        assert source.is_oa is True

        # Conference can have ISSN
        assert source.issn_l == "2161-8313"

        # No host organization
        assert source.host_organization is None
        assert source.host_organization_name is None
        assert len(source.host_organization_lineage) == 0

        # Abbreviated title
        assert source.abbreviated_title == "ICLR"
        assert "ICLR" in source.alternate_titles

    def test_ebook_platform_source(
        self, ebook_platform_source_data: dict[str, Any]
    ) -> None:
        """Test e-book platform type source."""
        source = Source(**ebook_platform_source_data)

        assert source.type == SourceType.EBOOK_PLATFORM
        assert source.is_ebook_platform is True
        assert source.is_oa is False

        # No ISSN
        assert source.issn_l is None
        assert len(source.issn) == 0

        # Has host organization
        assert source.host_organization_name == "Springer Nature"
        assert source.country_code == "DE"

    def test_source_helper_methods(
        self, journal_source_data: dict[str, Any]
    ) -> None:
        """Test source helper methods."""
        source = Source(**journal_source_data)

        # ISSN methods
        all_issns = source.all_issns()
        assert len(all_issns) == 4  # issn_l + 3 issn
        assert "0031-9007" in all_issns
        assert "1079-7114" in all_issns

        # Has methods
        assert source.has_issn() is True
        assert source.has_apc is True

        # Year-based lookups
        assert source.works_in_year(2024) == 3456
        assert source.citations_in_year(2023) == 678901
        assert source.works_in_year(2019) == 0  # Not in data

    def test_minimal_source(self) -> None:
        """Test source with minimal data."""
        source = Source(id="S123", display_name="Test Source")

        assert source.type is None
        assert source.issn_l is None
        assert len(source.issn) == 0
        assert source.is_oa is False
        assert source.has_apc is False
        assert source.all_issns() == []

    def test_source_validation_errors(self) -> None:
        """Test validation errors for invalid source data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Source()

        # Invalid type
        with pytest.raises(ValidationError):
            Source(id="S123", display_name="Test", type="invalid_type")

        # Invalid URL
        with pytest.raises(ValidationError):
            Source(id="S123", display_name="Test", homepage_url="not-a-url")

    def test_source_edge_cases(self) -> None:
        """Test edge cases in source data."""
        # Source with empty lists
        source = Source(
            id="S456",
            display_name="Empty Source",
            issn=[],
            apc_prices=[],
            societies=[],
            alternate_titles=[],
            x_concepts=[],
            counts_by_year=[],
        )

        assert source.has_issn() is False
        assert source.has_apc is False
        assert source.all_issns() == []
        assert source.get_apc_in_currency("USD") is None

        # Source with ISSN but no ISSN-L
        source_no_issn_l = Source(
            id="S789",
            display_name="No ISSN-L",
            issn=["1234-5678", "8765-4321"],
            issn_l=None,
        )
        assert source_no_issn_l.all_issns() == ["1234-5678", "8765-4321"]

    def test_datetime_fields(self, journal_source_data: dict[str, Any]) -> None:
        """Test datetime field parsing."""
        source = Source(**journal_source_data)

        assert isinstance(source.created_date, str)
        assert source.created_date == "2016-06-24"

        assert isinstance(source.updated_date, datetime)
        assert source.updated_date.year == 2024
