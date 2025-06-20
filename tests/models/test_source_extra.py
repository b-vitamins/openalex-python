from openalex.models import (
    Source,
    CountsByYear,
    SummaryStats,
    SourceType,
    APCPrice,
)


def make_source(**kwargs: object) -> Source:
    data = {
        "id": "https://openalex.org/S1",
        "display_name": "Test Journal",
        "type": "journal",
    }
    data.update(kwargs)
    return Source(**data)  # type: ignore[arg-type]


def test_issn_validator_handles_none_and_list() -> None:
    s_none = make_source(issn=None)
    assert s_none.issn is None
    s_list = make_source(issn=["1234-5678"])
    assert s_list.issn == ["1234-5678"]

    # Direct validator call
    assert Source.ensure_list(None) is None
    assert Source.ensure_list(["9999-9999"]) == ["9999-9999"]


def test_apc_prices_validator_converts_none() -> None:
    s = make_source(apc_prices=None)
    assert s.apc_prices == []
    assert Source._normalize_apc_prices(None) == []


def test_type_helpers_and_has_apc() -> None:
    s = make_source(apc_prices=[APCPrice(price=100, currency="USD")], apc_usd=200)
    assert s.is_journal
    assert not s.is_conference
    assert s.has_apc


def test_get_apc_in_currency() -> None:
    prices = [APCPrice(price=100, currency="USD"), APCPrice(price=90, currency="EUR")]
    s = make_source(apc_prices=prices)
    assert s.get_apc_in_currency("eur") == 90
    assert s.get_apc_in_currency("gbp") is None


def test_has_issn_and_all_issns() -> None:
    s = make_source(issn=["1234-5678", "1234-5678"], issn_l="8765-4321")
    assert s.has_issn()
    assert s.all_issns() == ["8765-4321", "1234-5678"]

    many = make_source(
        issn=["1", "2", "3"],
        issn_l="0",
    )
    assert many.all_issns() == ["0", "1", "2", "3"]


def test_year_based_helpers() -> None:
    counts = [
        CountsByYear(year=2022, works_count=5, cited_by_count=10),
        CountsByYear(year=2021, works_count=0, cited_by_count=2),
    ]
    s = make_source(counts_by_year=counts)
    assert s.works_in_year(2022) == 5
    assert s.citations_in_year(2021) == 2
    assert s.active_years() == [2022]
