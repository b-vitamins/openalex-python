from datetime import date

import pytest

from openalex.models import Funder, CountsByYear, SummaryStats


def make_funder(**kwargs: object) -> Funder:
    data = {
        "id": "https://openalex.org/F1",
        "display_name": "National Health Agency",
        "grants_count": 0,
        "works_count": 0,
    }
    data.update(kwargs)
    return Funder(**data)  # type: ignore[arg-type]


def test_parse_updated_date_allows_overflow_seconds() -> None:
    funder = make_funder(updated_date="2020-01-02T00:00:61")
    assert funder.updated_date == date(2020, 1, 2)


def test_country_code_validation_and_normalization() -> None:
    funder = make_funder(country_code="us")
    assert funder.country_code == "US"
    with pytest.raises(ValueError):
        Funder(id="https://openalex.org/F2", display_name="X", country_code="USA")


def test_is_government_funder_detection() -> None:
    gov = make_funder(display_name="Federal Research Agency")
    private = make_funder(display_name="Private Research Foundation")
    assert gov.is_government_funder()
    assert not private.is_government_funder()


def test_funding_per_work_calculation() -> None:
    funder = make_funder(grants_count=20, works_count=5)
    assert funder.funding_per_work == 4
    no_work = make_funder(grants_count=10, works_count=0)
    assert no_work.funding_per_work is None


def test_year_based_helpers() -> None:
    counts = [
        CountsByYear(year=2022, works_count=5, cited_by_count=10),
        CountsByYear(year=2021, works_count=0, cited_by_count=2),
    ]
    funder = make_funder(counts_by_year=counts)
    assert funder.works_in_year(2022) == 5
    assert funder.citations_in_year(2021) == 2
    assert funder.active_years() == [2022]


def test_summary_stats_properties() -> None:
    stats = SummaryStats(h_index=10, i10_index=20)
    funder = make_funder(summary_stats=stats)
    assert funder.h_index == 10
    assert funder.i10_index == 20
