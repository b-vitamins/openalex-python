"""
Test parameter handling utilities.
Tests utils/params.py functionality for API parameter preparation.
"""

import pytest


class TestParameterNormalization:
    """Test parameter normalization for API calls."""

    def test_normalize_params_basic(self):
        """Basic parameter normalization."""
        from openalex.utils.params import normalize_params

        params = {
            "page": 2,
            "per_page": 50,
            "select": ["id", "title"],
            "unknown_param": "ignored"
        }

        normalized = normalize_params(params)

        assert normalized["page"] == "2"
        assert normalized["per-page"] == "50"  # Underscore to hyphen
        assert normalized["select"] == "id,title"  # List to comma-separated
        assert "unknown_param" not in normalized  # Unknown params dropped

    def test_normalize_params_group_by(self):
        """Group-by parameter normalization."""
        from openalex.utils.params import normalize_params

        params = {"group_by": "publication_year"}
        normalized = normalize_params(params)

        assert normalized["group-by"] == "publication_year"

    def test_normalize_params_empty(self):
        """Empty parameters should return empty dict."""
        from openalex.utils.params import normalize_params

        assert normalize_params({}) == {}
        assert normalize_params(None) == {}

    def test_normalize_params_preserves_strings(self):
        """String parameters should be preserved."""
        from openalex.utils.params import normalize_params

        params = {
            "search": "climate change",
            "cursor": "abc123",
            "seed": "42"
        }

        normalized = normalize_params(params)

        assert normalized["search"] == "climate change"
        assert normalized["cursor"] == "abc123"
        assert normalized["seed"] == "42"


class TestFilterSerialization:
    """Test filter parameter serialization."""

    def test_serialize_filter_value_basic_types(self):
        """Basic type serialization."""
        from openalex.utils.params import serialize_filter_value

        # Strings
        assert serialize_filter_value("hello") == "hello"
        assert serialize_filter_value("hello world") == "hello+world"

        # Numbers
        assert serialize_filter_value(123) == "123"
        assert serialize_filter_value(45.67) == "45.67"

        # Booleans
        assert serialize_filter_value(True) == "true"
        assert serialize_filter_value(False) == "false"

        # None
        assert serialize_filter_value(None) == "null"

    def test_serialize_filter_value_lists(self):
        """List serialization with pipe separator."""
        from openalex.utils.params import serialize_filter_value

        assert serialize_filter_value(["A", "B", "C"]) == "A|B|C"
        assert serialize_filter_value([1, 2, 3]) == "1|2|3"
        assert serialize_filter_value([True, False]) == "true|false"
        assert serialize_filter_value([]) == ""

    def test_serialize_filter_value_special_chars(self):
        """Special character handling."""
        from openalex.utils.params import serialize_filter_value

        assert serialize_filter_value("test@example.com") == "test%40example.com"
        assert serialize_filter_value("A & B") == "A+%26+B"
        assert serialize_filter_value("C++ Programming") == "C%2B%2B+Programming"
        assert serialize_filter_value("100%") == "100%25"

    def test_serialize_filter_value_logical_expressions(self):
        """Logical expression serialization."""
        from openalex.utils.params import serialize_filter_value
        from openalex.query import not_, gt_, lt_

        assert serialize_filter_value(not_("article")) == "!article"
        assert serialize_filter_value(gt_(100)) == ">100"
        assert serialize_filter_value(lt_(2020)) == "<2020"

        # Nested in lists
        assert serialize_filter_value([not_("A"), "B"]) == "!A|B"
        assert serialize_filter_value([gt_(10), lt_(20)]) == ">10|<20"

    def test_flatten_filter_dict_simple(self):
        """Simple filter dictionary flattening."""
        from openalex.utils.params import flatten_filter_dict

        filters = {
            "is_oa": True,
            "publication_year": 2023,
            "type": "article"
        }

        result = flatten_filter_dict(filters)

        assert "is_oa:true" in result
        assert "publication_year:2023" in result
        assert "type:article" in result

        # Should be comma-separated
        assert result.count(",") == 2

    def test_flatten_filter_dict_nested(self):
        """Nested filter dictionary flattening."""
        from openalex.utils.params import flatten_filter_dict

        filters = {
            "authorships": {
                "author": {"id": "A123"},
                "institutions": {
                    "country_code": "US",
                    "type": "education"
                }
            }
        }

        result = flatten_filter_dict(filters)

        assert "authorships.author.id:A123" in result
        assert "authorships.institutions.country_code:US" in result
        assert "authorships.institutions.type:education" in result

    def test_flatten_filter_dict_or_operator(self):
        """OR operator handling in filter dict."""
        from openalex.utils.params import flatten_filter_dict
        from openalex.query import or_

        filters = or_({"type": "article", "is_oa": True})

        result = flatten_filter_dict(filters)

        assert result == "type:article|is_oa:true"

    def test_flatten_filter_dict_empty(self):
        """Empty filter dict handling."""
        from openalex.utils.params import flatten_filter_dict

        assert flatten_filter_dict({}) == ""
        assert flatten_filter_dict(None) == ""

    def test_serialize_params_complete(self):
        """Complete parameter serialization."""
        from openalex.utils.params import serialize_params
        from openalex.query import gt_, not_

        params = {
            "filter": {
                "is_oa": True,
                "publication_year": gt_(2020),
                "type": not_("retracted"),
                "institutions": {"country_code": ["US", "UK"]}
            },
            "sort": {"cited_by_count": "desc", "publication_year": "asc"},
            "select": ["id", "title", "doi"],
            "search": "machine learning",
            "per_page": 50,
            "page": 2
        }

        result = serialize_params(params)

        # Check filter serialization
        assert "filter" in result
        assert "is_oa:true" in result["filter"]
        assert "publication_year:>2020" in result["filter"]
        assert "type:!retracted" in result["filter"]
        assert "institutions.country_code:US|UK" in result["filter"]

        # Check other params
        assert result["sort"] == "cited_by_count:desc,publication_year:asc"
        assert result["select"] == "id,title,doi"
        assert result["search"] == "machine learning"
        assert result["per-page"] == "50"
        assert result["page"] == "2"

    def test_sort_parameter_serialization(self):
        """Sort parameter special handling."""
        from openalex.utils.params import serialize_params

        # Dict format
        params = {"sort": {"cited_by_count": "desc", "publication_year": "asc"}}
        result = serialize_params(params)
        assert result["sort"] == "cited_by_count:desc,publication_year:asc"

        # String format (passthrough)
        params = {"sort": "cited_by_count:desc"}
        result = serialize_params(params)
        assert result["sort"] == "cited_by_count:desc"

    def test_parameter_type_conversion(self):
        """All parameters should be strings."""
        from openalex.utils.params import serialize_params

        params = {
            "page": 1,
            "per_page": 25,
            "sample": 100,
            "seed": 42
        }

        result = serialize_params(params)

        assert result["page"] == "1"
        assert result["per-page"] == "25"
        assert result["sample"] == "100"
        assert result["seed"] == "42"

        # All values should be strings
        assert all(isinstance(v, str) for v in result.values())

    def test_search_filter_suffix(self):
        """Search filters should add .search suffix."""
        from openalex.utils.params import flatten_filter_dict

        filters = {
            "title.search": "quantum computing",
            "abstract.search": "neural networks",
            "fulltext.search": "machine learning"
        }

        result = flatten_filter_dict(filters)

        assert "title.search:quantum computing" in result
        assert "abstract.search:neural networks" in result
        assert "fulltext.search:machine learning" in result

    def test_complex_nested_filters(self):
        """Complex nested filter structures."""
        from openalex.utils.params import flatten_filter_dict

        filters = {
            "authorships": {
                "author": {
                    "id": "A123",
                    "last_known_institution": {
                        "country_code": "US",
                        "type": "education"
                    }
                },
                "institutions": {
                    "ror": "https://ror.org/123"
                }
            },
            "topics": {
                "id": ["T123", "T456"]
            }
        }

        result = flatten_filter_dict(filters)

        assert "authorships.author.id:A123" in result
        assert "authorships.author.last_known_institution.country_code:US" in result
        assert "authorships.author.last_known_institution.type:education" in result
        assert "authorships.institutions.ror:https://ror.org/123" in result
        assert "topics.id:T123|T456" in result
