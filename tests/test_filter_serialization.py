"""Test filter serialization for API requests."""

from __future__ import annotations

from openalex.query import gt_, lt_, not_, or_
from openalex.utils.params import (
    flatten_filter_dict,
    serialize_filter_value,
    serialize_params,
)


class TestFilterValueSerialization:
    """Test individual filter value serialization."""

    def test_logical_expressions(self) -> None:
        """Test logical expression serialization."""
        assert serialize_filter_value(not_("article")) == "!article"
        assert serialize_filter_value(gt_(100)) == ">100"
        assert serialize_filter_value(lt_(2020)) == "<2020"

    def test_boolean_values(self) -> None:
        """Test boolean serialization to lowercase."""
        assert serialize_filter_value(True) == "true"
        assert serialize_filter_value(False) == "false"

    def test_list_values(self) -> None:
        """Test list serialization with pipe separator."""
        assert serialize_filter_value(["A", "B", "C"]) == "A|B|C"
        assert serialize_filter_value([1, 2, 3]) == "1|2|3"

    def test_none_value(self) -> None:
        """Test None serialization."""
        assert serialize_filter_value(None) == "null"

    def test_url_encoding(self) -> None:
        """Test URL encoding of special characters."""
        assert serialize_filter_value("hello world") == "hello+world"
        assert (
            serialize_filter_value("test@example.com") == "test%40example.com"
        )

    def test_nested_logical_expressions(self) -> None:
        """Test nested logical expressions."""
        assert serialize_filter_value([not_("A"), "B"]) == "!A|B"
        assert serialize_filter_value(gt_("hello world")) == ">hello+world"


class TestFilterDictFlattening:
    """Test filter dictionary flattening."""

    def test_simple_filters(self) -> None:
        """Test simple filter flattening."""
        filters = {"is_oa": True, "type": "article"}
        result = flatten_filter_dict(filters)
        assert result == "is_oa:true,type:article"

    def test_nested_filters(self) -> None:
        """Test nested filter flattening."""
        filters = {
            "authorships": {
                "author": {"id": "A123"},
                "institutions": {"country_code": "US"},
            }
        }
        result = flatten_filter_dict(filters)
        assert "authorships.author.id:A123" in result
        assert "authorships.institutions.country_code:US" in result

    def test_or_filters(self) -> None:
        """Test OR filter flattening."""
        filters = or_({"type": "article", "is_oa": True})
        result = flatten_filter_dict(filters)
        assert result == "type:article|is_oa:true"

    def test_complex_filters(self) -> None:
        """Test complex filter combinations."""
        filters = {
            "is_oa": True,
            "publication_year": gt_(2020),
            "cited_by_count": lt_(100),
            "type": not_("retracted"),
            "institutions": {"country_code": ["US", "UK", "CA"]},
        }
        result = flatten_filter_dict(filters)
        assert "is_oa:true" in result
        assert "publication_year:>2020" in result
        assert "cited_by_count:<100" in result
        assert "type:!retracted" in result
        assert "institutions.country_code:US|UK|CA" in result

    def test_search_filters(self) -> None:
        """Test search filter syntax."""
        filters = {
            "title.search": "quantum computing",
            "abstract.search": "machine learning",
        }
        result = flatten_filter_dict(filters)
        assert "title.search:quantum+computing" in result
        assert "abstract.search:machine+learning" in result


class TestParamSerialization:
    """Test full parameter serialization."""

    def test_full_params(self) -> None:
        """Test serialization of all parameter types."""
        params = {
            "filter": {
                "is_oa": True,
                "publication_year": gt_(2020),
                "type": ["article", "dataset"],
            },
            "sort": {"cited_by_count": "desc", "publication_year": "asc"},
            "select": ["id", "title", "doi"],
            "per_page": 50,
            "page": 2,
            "search": "climate change",
        }
        result = serialize_params(params)
        assert "filter" in result
        assert "is_oa:true" in result["filter"]
        assert "publication_year:>2020" in result["filter"]
        assert "type:article|dataset" in result["filter"]
        assert result["sort"] == "cited_by_count:desc,publication_year:asc"
        assert result["select"] == "id,title,doi"
        assert result["per_page"] == "50"
        assert result["page"] == "2"
        assert result["search"] == "climate change"

    def test_empty_params(self) -> None:
        """Test empty parameter handling."""
        assert serialize_params({}) == {}
        assert serialize_params({"filter": {}}) == {}
        assert serialize_params({"filter": None}) == {}


class TestIntegration:
    """Test integration with Query class."""

    def test_query_to_params(self) -> None:
        """Test Query object parameter generation."""
        from openalex.query import Query

        class MockResource:
            def list(self, filter=None, **params):
                return {"filter": filter, "params": params}

        resource = MockResource()
        query = (
            Query(resource)
            .filter_gt(cited_by_count=100)
            .filter_not(type="retracted")
            .filter_or(is_oa=True, has_doi=True)
            .search("neuroscience")
            .sort(publication_year="desc")
        )
        assert "filter" in query.params
        assert "search" in query.params
        assert "sort" in query.params
