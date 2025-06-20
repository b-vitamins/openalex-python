import pytest

from openalex.models import Institution, CountsByYear, SummaryStats


def make_inst(**kwargs: object) -> Institution:
    data = {
        "id": "https://openalex.org/I1",
        "display_name": "Institute",
        "type": "company",
        "repositories": [],
    }
    data.update(kwargs)
    return Institution(**data)  # type: ignore[arg-type]


def test_type_and_repository_helpers() -> None:
    inst = make_inst(
        type="education",
        repositories=[{"id": "https://openalex.org/S1", "display_name": "Repo"}],
        geo={"city": "X"},
    )
    assert inst.is_education
    assert not inst.is_company
    assert inst.type_id == "https://openalex.org/institution-types/education"
    assert inst.repository_count() == 1
    assert inst.has_location()


def test_parent_and_root_lookup() -> None:
    inst = make_inst(
        lineage=["https://openalex.org/I1", "https://openalex.org/I2", "https://openalex.org/Iroot"]
    )
    assert inst.parent_institution_id == "https://openalex.org/I2"
    assert inst.root_institution == "https://openalex.org/Iroot"


def test_summary_and_year_helpers() -> None:
    counts = [CountsByYear(year=2022, works_count=10, cited_by_count=50)]
    stats = SummaryStats(h_index=5, i10_index=7, two_year_mean_citedness=1.2)
    inst = make_inst(counts_by_year=counts, summary_stats=stats)
    assert inst.h_index == 5
    assert inst.i10_index == 7
    assert inst.two_year_mean_citedness == 1.2
    assert inst.works_in_year(2022) == 10
    assert inst.citations_in_year(2022) == 50
    assert inst.active_years() == [2022]


def test_validators_normalize_fields() -> None:
    inst = make_inst(image_thumbnail_url="https://x/thumb/logo.png", country_code="us")
    assert inst.image_thumbnail_url == "https://x/thumbnail/logo.png"
    assert inst.country_code == "US"
    with pytest.raises(ValueError):
        Institution(id="https://openalex.org/I2", display_name="X", country_code="USA")
