"""Test filter models and parameter building."""

import pytest
from datetime import date, datetime

from openalex.models.filters import BaseFilter


class TestFilterModels:
    """Test filter model functionality."""

    def test_base_filter_validation(self):
        """Test BaseFilter validation and defaults."""
        filter_obj = BaseFilter(
            search="machine learning",
            filter={"publication_year": 2023},
            sort="cited_by_count:desc",
            page=2,
            per_page=50,
        )

        assert filter_obj.search == "machine learning"
        assert filter_obj.filter == {"publication_year": 2023}
        assert filter_obj.page == 2
        assert filter_obj.per_page == 50

    def test_filter_string_format(self):
        """Test filter string can be passed directly."""
        filter_obj = BaseFilter(filter="publication_year:2023,is_oa:true")
        assert filter_obj.filter == "publication_year:2023,is_oa:true"

    def test_select_field_validation(self):
        """Test select field accepts string or list."""
        f1 = BaseFilter(select="id,display_name")
        assert f1.select == "id,display_name"

        f2 = BaseFilter(select=["id", "display_name", "cited_by_count"])
        assert f2.select == ["id", "display_name", "cited_by_count"]

        with pytest.raises(ValueError, match="Select must be"):
            BaseFilter(select=123)

    def test_to_params_conversion(self):
        """Test conversion to API parameters."""
        filter_obj = BaseFilter(
            filter={
                "is_oa": True,
                "publication_year": [2022, 2023],
                "institutions.country_code": "US",
                "from_publication_date": date(2023, 1, 1),
            },
            select=["id", "title"],
            group_by="publication_year",
            per_page=100,
        )

        params = filter_obj.to_params()

        assert (
            params["filter"]
            == "is_oa:true,publication_year:2022|2023,institutions.country_code:US,from_publication_date:2023-01-01"
        )
        assert params["select"] == "id,title"
        assert params["group-by"] == "publication_year"
        assert params["per-page"] == 100

    def test_complex_filter_building(self):
        """Test complex filter scenarios."""
        filter_obj = BaseFilter(
            filter={
                "authorships.author.id": ["A123", "A456"],
                "has_doi": True,
                "cited_by_count": ">100",
                "concepts.id": ["C2778407487", "C41008148"],
                "published_date": datetime(2023, 6, 15),
            }
        )

        params = filter_obj.to_params()
        filter_str = params["filter"]

        assert "authorships.author.id:A123|A456" in filter_str
        assert "has_doi:true" in filter_str
        assert "cited_by_count:>100" in filter_str
        assert "published_date:2023-06-15" in filter_str

    def test_empty_filter_values_ignored(self):
        """Test empty values are ignored in filters."""
        filter_obj = BaseFilter(
            filter={
                "is_oa": True,
                "empty_list": [],
                "none_value": None,
                "valid_list": ["A", "B"],
            }
        )

        params = filter_obj.to_params()
        filter_str = params["filter"]

        assert "is_oa:true" in filter_str
        assert "valid_list:A|B" in filter_str
        assert "empty_list" not in filter_str
        assert "none_value" not in filter_str
