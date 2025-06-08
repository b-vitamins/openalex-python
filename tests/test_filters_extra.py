from datetime import date
import pytest

from openalex.models import BaseFilter, WorksFilter, GroupBy
from pydantic import ValidationError


def test_base_filter_validation() -> None:
    assert BaseFilter().filter is None
    with pytest.raises(ValidationError):
        BaseFilter(filter=123)

    assert BaseFilter(select=None).select is None
    with pytest.raises(ValidationError):
        BaseFilter(select=123)


def test_build_filter_string() -> None:
    bf = BaseFilter()
    filters = {
        "bool": True,
        "list": [1, 2],
        "date": date(2020, 1, 1),
        "str": "x",
        "none": None,
    }
    result = bf._build_filter_string(filters)
    assert "bool:true" in result
    assert "list:1|2" in result
    assert "date:2020-01-01" in result
    assert "str:x" in result
    assert "none" not in result


def test_to_params_and_works_filter() -> None:
    wf = WorksFilter().with_publication_year(2020).with_type(["article", "book"]).with_open_access(False)
    wf = wf.model_copy(update={"group_by": GroupBy.TYPE, "per_page": 10, "select": ["id", "title"]})
    params = wf.to_params()
    assert params["group-by"] == GroupBy.TYPE
    assert params["per-page"] == 10
    assert params["select"] == "id,title"
    filt = params["filter"]
    assert "publication_year:2020" in filt
    assert "type:article|book" in filt
    assert "is_oa:false" in filt
