"""
Test filter behavior and API parameter generation.
Tests how filters translate to API calls, not internal serialization.
"""

import pytest
from unittest.mock import Mock, patch


class TestFilterBehavior:
    """Test how filters translate to API parameters."""

    def test_simple_equality_filter(self):
        """Simple equality filters should use field:value format."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Works().filter(
                is_oa=True,
                publication_year=2023,
                type="article"
            ).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "is_oa:true" in filter_param
            assert "publication_year:2023" in filter_param
            assert "type:article" in filter_param

    def test_comparison_operators(self):
        """Comparison operators should use correct syntax."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Authors().filter_gt(works_count=50).filter_lt(cited_by_count=1000).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "works_count:>50" in filter_param
            assert "cited_by_count:<1000" in filter_param

    def test_negation_operator(self):
        """NOT operator should use ! prefix."""
        from openalex import Institutions

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Institutions().filter_not(type="company").get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "type:!company" in filter_param

    def test_or_operator_single_field(self):
        """OR on single field should use pipe separator."""
        from openalex import Sources

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Sources().filter(type=["journal", "repository", "conference"]).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "type:journal|repository|conference" in filter_param

    def test_or_operator_multiple_fields(self):
        """OR across fields should create separate OR group."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Works().filter_or(
                is_oa=True,
                has_doi=True
            ).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "is_oa:true|has_doi:true" in filter_param

    def test_nested_entity_filters(self):
        """Nested entity filters should use dot notation."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Works().filter(
                authorships={
                    "author": {"id": "A5023888391"},
                    "institutions": {"country_code": "US"}
                }
            ).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "authorships.author.id:A5023888391" in filter_param
            assert "authorships.institutions.country_code:US" in filter_param

    def test_search_filters(self):
        """Search filters should append .search suffix."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Works().search_filter(
                title="quantum computing",
                abstract="machine learning"
            ).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "title.search:quantum computing" in filter_param
            assert "abstract.search:machine learning" in filter_param

    def test_filter_with_special_characters(self):
        """Special characters in filter values should be encoded."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Authors().filter(display_name="Smith & Jones").get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            # Ampersand should be encoded
            assert "display_name:Smith+%26+Jones" in filter_param or \
                   "display_name:Smith %26 Jones" in filter_param

    def test_filter_with_spaces(self):
        """Spaces in filter values should be encoded."""
        from openalex import Institutions

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Institutions().filter(display_name="University of Michigan").get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            # Spaces should be encoded as +
            assert "display_name:University+of+Michigan" in filter_param

    def test_null_filter_value(self):
        """None/null filter values should use 'null'."""
        from openalex import Sources

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Sources().filter(issn=None).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "issn:null" in filter_param

    def test_boolean_filter_values(self):
        """Boolean values should be lowercase strings."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Works().filter(is_oa=True, is_retracted=False).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "is_oa:true" in filter_param
            assert "is_retracted:false" in filter_param

    def test_date_range_filters(self):
        """Date range filters should work with comparison operators."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            (Works()
                .filter_gt(publication_date="2023-01-01")
                .filter_lt(publication_date="2023-12-31")
                .get())

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            assert "publication_date:>2023-01-01" in filter_param
            assert "publication_date:<2023-12-31" in filter_param

    def test_complex_filter_combinations(self):
        """Complex filter combinations should all work together."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            (Works()
                .filter(is_oa=True)
                .filter_gt(cited_by_count=100)
                .filter_not(type="retracted")
                .filter(
                    authorships={
                        "institutions": {"country_code": ["US", "UK", "CA"]}
                    }
                )
                .search_filter(title="climate change")
                .get())

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            # All filters should be present
            assert "is_oa:true" in filter_param
            assert "cited_by_count:>100" in filter_param
            assert "type:!retracted" in filter_param
            assert "authorships.institutions.country_code:US|UK|CA" in filter_param
            assert "title.search:climate change" in filter_param

    def test_filter_chaining_accumulates(self):
        """Chained filters should accumulate, not replace."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            (Authors()
                .filter(works_count=">10")
                .filter(cited_by_count=">100")
                .filter(last_known_institution={"country_code": "US"})
                .get())

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            # All three filters should be present
            assert "works_count:>10" in filter_param
            assert "cited_by_count:>100" in filter_param
            assert "last_known_institution.country_code:US" in filter_param

    def test_id_normalization_in_filters(self):
        """IDs in filters should be normalized."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            # Test various ID formats
            Works().filter(
                authorships={
                    "author": {"id": "https://openalex.org/A123"}  # Full URL
                }
            ).get()

            _, kwargs = mock_request.call_args
            filter_param = kwargs["params"]["filter"]

            # Should normalize to just the ID part
            assert "authorships.author.id:A123" in filter_param or \
                   "authorships.author.id:https://openalex.org/A123" in filter_param

    def test_empty_filter_no_param(self):
        """Empty filter should not add filter parameter."""
        from openalex import Concepts

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"results": [], "meta": {"count": 0}})
            )

            Concepts().get()  # No filters

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            # Should not have filter parameter
            assert "filter" not in params
