from __future__ import annotations

import pytest
from pydantic import ValidationError

from openalex.models import BaseFilter, WorksFilter


class TestFilters:
    """Test filter models."""

    def test_base_filter(self) -> None:
        filter = BaseFilter(
            search="machine learning",
            sort="cited_by_count:desc",
            page=2,
            per_page=50,
        )

        params = filter.to_params()
        assert params["search"] == "machine learning"
        assert params["sort"] == "cited_by_count:desc"
        assert params["page"] == 2
        assert params["per-page"] == 50

    def test_filter_with_dict(self) -> None:
        filter = BaseFilter(
            filter={
                "is_oa": True,
                "publication_year": [2020, 2021, 2022],
                "type": "article",
            }
        )

        params = filter.to_params()
        assert "is_oa:true" in params["filter"]
        assert "publication_year:2020|2021|2022" in params["filter"]
        assert "type:article" in params["filter"]

    def test_works_filter(self) -> None:
        filter = WorksFilter()
        filter = filter.with_publication_year([2020, 2021])
        filter = filter.with_type("article")
        filter = filter.with_open_access(True)

        params = filter.to_params()
        filter_str = params["filter"]
        assert "publication_year:2020|2021" in filter_str
        assert "type:article" in filter_str
        assert "is_oa:true" in filter_str

    def test_filter_validation(self) -> None:
        filter = WorksFilter(sort="publication_date:desc")
        assert filter.sort == "publication_date:desc"

        with pytest.raises(ValidationError):
            WorksFilter(sort="invalid_field:desc")
