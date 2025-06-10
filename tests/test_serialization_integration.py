"""Test filter serialization in actual API calls."""

from __future__ import annotations

from unittest.mock import Mock, patch

from openalex import Works


def test_complex_query_serialization() -> None:
    """Test that complex queries are properly serialized."""
    with patch("httpx.Client.request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "meta": {
                "count": 0,
                "db_response_time_ms": 1,
                "page": 1,
                "per_page": 50,
            },
        }
        mock_request.return_value = mock_response

        (
            Works()
            .filter_gt(cited_by_count=100)
            .filter_not(type="retracted")
            .filter(is_oa=True)
            .search("climate change")
            .sort(publication_year="desc")
            .get(per_page=50)
        )

        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        params = kwargs.get("params", {})
        assert "filter" in params
        assert "cited_by_count:>100" in params["filter"]
        assert "type:!retracted" in params["filter"]
        assert "is_oa:true" in params["filter"]
        assert params.get("search") == "climate change"
        assert params.get("sort") == "publication_year:desc"
        assert params.get("per-page") == "50"
