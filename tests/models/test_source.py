from __future__ import annotations

from openalex.models import Source, SourceType


class TestSourceModel:
    """Test Source model."""

    def test_source_creation(self) -> None:
        source = Source(
            id="S123",
            display_name="Nature",
            type=SourceType.JOURNAL,
            issn_l="0028-0836",
            issn=["0028-0836", "1476-4687"],
            is_oa=False,
            apc_usd=3000,
        )

        assert source.is_journal is True
        assert source.is_conference is False
        assert source.has_apc is True
        assert source.all_issns() == ["0028-0836", "1476-4687"]

    def test_source_apc_prices(self) -> None:
        source = Source(
            id="S123",
            display_name="Test Journal",
            apc_prices=[
                {"price": 3000, "currency": "USD"},
                {"price": 2500, "currency": "EUR"},
                {"price": 2200, "currency": "GBP"},
            ],
        )

        assert source.get_apc_in_currency("USD") == 3000
        assert source.get_apc_in_currency("EUR") == 2500
        assert source.get_apc_in_currency("JPY") is None
