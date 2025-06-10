from __future__ import annotations

import pytest
from pydantic import ValidationError

from openalex.models import BaseFilter, GroupBy, SortOrder


class TestBaseFilter:
    def test_defaults(self) -> None:
        bf = BaseFilter()
        assert bf.page == 1
        assert bf.per_page == 25
        assert bf.to_params()["page"] == 1

    def test_to_params(self) -> None:
        bf = BaseFilter(
            filter={"is_oa": True},
            search="ml",
            sort="cited_by_count:desc",
            select=["id"],
        )
        params = bf.to_params()
        assert params["filter"] == "is_oa:true"
        assert params["search"] == "ml"
        assert params["sort"] == "cited_by_count:desc"
        assert params["select"] == "id"

    def test_validation(self) -> None:
        with pytest.raises(ValidationError):
            BaseFilter(page=0)


class TestEnums:
    def test_group_by_values(self) -> None:
        assert GroupBy.TYPE == "type"
        assert GroupBy.CITED_BY_COUNT == "cited_by_count"

    def test_sort_order(self) -> None:
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"
