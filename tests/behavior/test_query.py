"""
Test query building behavior based on expected API parameters.
Focuses on what queries should produce, not how they're built internally.
"""

import pytest
from unittest.mock import Mock, patch


class TestQueryBehavior:
    """Test query construction produces correct API parameters."""

    @pytest.fixture
    def mock_api_response(self):
        """Standard mock API response."""
        return {
            "results": [],
            "meta": {
                "count": 0,
                "db_response_time_ms": 10,
                "page": 1,
                "per_page": 25,
            },
        }

    def test_filter_creates_correct_api_params(self, mock_api_response):
        """Filters should translate to correct API filter parameters."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().filter(
                publication_year=2023, is_oa=True, type="article"
            ).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "publication_year:2023" in params["filter"]
            assert "is_oa:true" in params["filter"]
            assert "type:article" in params["filter"]

    def test_search_creates_search_param(self, mock_api_response):
        """Search should create search parameter."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Authors().search("machine learning").get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("search") == "machine learning"

    def test_sort_creates_sort_param(self, mock_api_response):
        """Sort should create properly formatted sort parameter."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().sort(cited_by_count="desc").get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("sort") == "cited_by_count:desc"

    def test_select_creates_select_param(self, mock_api_response):
        """Select should create comma-separated field list."""
        from openalex import Institutions

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Institutions().select(["id", "display_name", "works_count"]).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("select") == "id,display_name,works_count"

    def test_group_by_creates_group_by_param(self, mock_api_response):
        """Group by should create group-by parameter."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().group_by("is_oa").get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("group-by") == "is_oa"

    def test_complex_filters_with_operators(self, mock_api_response):
        """Complex filters with operators should format correctly."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            (
                Works()
                .filter_gt(cited_by_count=100)
                .filter_lt(publication_year=2020)
                .filter_not(type="retracted")
                .get()
            )

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "cited_by_count:>100" in params["filter"]
            assert "publication_year:<2020" in params["filter"]
            assert "type:!retracted" in params["filter"]

    def test_or_filter_creates_pipe_separated_values(self, mock_api_response):
        """OR filters should use pipe separator."""
        from openalex import Sources

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Sources().filter_or(type="journal", is_oa=True).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "type:journal|is_oa:true" in params["filter"]

    def test_nested_attribute_filters(self, mock_api_response):
        """Nested attributes should use dot notation."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().filter(
                authorships={"institutions": {"country_code": "US"}}
            ).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert (
                "authorships.institutions.country_code:US" in params["filter"]
            )

    def test_search_filter_creates_search_suffix(self, mock_api_response):
        """Search filters should add .search suffix."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().search_filter(
                title="quantum computing", abstract="neural networks"
            ).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "title.search:quantum computing" in params["filter"]
            assert "abstract.search:neural networks" in params["filter"]

    def test_pagination_parameters(self, mock_api_response):
        """Pagination should set correct page and per-page parameters."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Works().get(page=3, per_page=50)

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("page") == "3"
            assert params.get("per-page") == "50"

    def test_sample_creates_sample_params(self, mock_api_response):
        """Sample should create sample and seed parameters."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Authors().sample(100, seed=42).get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("sample") == "100"
            assert params.get("seed") == "42"

    def test_random_endpoint_called(self):
        """Random should call the /random endpoint."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"id": "W123", "title": "Random Work"}),
            )

            work = Works().random()

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/works/random")
            assert work.id == "W123"

    def test_autocomplete_endpoint_with_query(self):
        """Autocomplete should call autocomplete endpoint with q parameter."""
        from openalex import Institutions

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [{"id": "I123", "display_name": "MIT"}],
                        "meta": {"count": 1},
                    }
                ),
            )

            results = Institutions().autocomplete("massachus")

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/autocomplete/institutions")
            assert kwargs["params"]["q"] == "massachus"
            assert len(results.results) == 1

    def test_count_uses_minimal_page_size(self, mock_api_response):
        """Count should request minimal data with per_page=1."""
        from openalex import Works

        mock_api_response["meta"]["count"] = 42

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            count = Works().filter(is_oa=True).count()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params.get("per-page") == "1"
            assert count == 42

    def test_getitem_single_id_fetches_entity(self):
        """Getting single item by ID should fetch that entity."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": "https://openalex.org/W123",
                        "title": "Test Work",
                    }
                ),
            )

            work = Works()["W123"]

            _, kwargs = mock_request.call_args
            assert kwargs["url"].endswith("/works/W123")
            assert work.id == "https://openalex.org/W123"

    def test_getitem_multiple_ids_creates_filter(self, mock_api_response):
        """Getting multiple items by ID should create openalex_id filter."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            Authors()[["A123", "A456", "A789"]]

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert "filter" in params
            assert "openalex_id:A123|A456|A789" in params["filter"]

    def test_first_returns_first_result(self):
        """First should return first result or None."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [{"id": "W1", "title": "First"}],
                        "meta": {"count": 10},
                    }
                ),
            )

            work = Works().filter(is_oa=True).first()

            assert work is not None
            assert work.id == "W1"

    def test_first_returns_none_when_no_results(self, mock_api_response):
        """First should return None when no results."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200, json=Mock(return_value=mock_api_response)
            )

            work = Works().filter(title="nonexistent").first()

            assert work is None
