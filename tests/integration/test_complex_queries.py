"""Integration tests for complex query scenarios."""

import pytest
from unittest.mock import Mock, patch
import httpx
from openalex import Works, Authors
from openalex.exceptions import APIError
from tests.fixtures.api_responses import APIResponseFixtures


class TestComplexQueries:
    """Test complex query scenarios with mocked API."""

    @pytest.fixture
    def fixtures(self):
        """Get API response fixtures."""
        return APIResponseFixtures()

    def test_search_with_filters_and_pagination(self, fixtures):
        """Test search with multiple filters and pagination."""
        page1_response = fixtures.search_response(
            "machine learning", page=1, per_page=50
        )
        page2_response = fixtures.search_response(
            "machine learning", page=2, per_page=50
        )

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(json=lambda: page1_response, status_code=200),
                Mock(json=lambda: page2_response, status_code=200),
            ]

            paginator = (
                Works()
                .search("machine learning")
                .filter(publication_year=2023)
                .filter(open_access={"is_oa": True})
                .filter(type="article")
                .sort(cited_by_count="desc")
                .paginate(per_page=50)
            )

            page1 = next(paginator)
            assert page1.meta.count == 150
            assert len(page1.results) == 50
            assert page1.meta.page == 1

            page2 = next(paginator)
            assert page2.meta.page == 2
            assert len(page2.results) == 50

    def test_group_by_with_filters(self, fixtures):
        """Test group-by queries with filters."""
        group_response = fixtures.group_by_response("publication_year")

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                json=lambda: group_response, status_code=200
            )
            results = (
                Works()
                .filter(institutions={"country_code": "US"})
                .filter(is_open_access=True)
                .group_by("publication_year")
                .get()
            )

            assert len(results.groups) == 4
            assert results.groups[-1].key == "2023"
            assert sum(g.count for g in results.groups) == results.meta.count

    def test_chained_entity_queries(self, fixtures):
        """Test following relationships between entities."""
        author_response = fixtures.author_response()
        work_response = fixtures.work_response()

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(json=lambda: author_response, status_code=200),
                Mock(
                    json=lambda: {
                        "results": [work_response],
                        "meta": {"count": 1},
                    },
                    status_code=200,
                ),
            ]
            author = Authors()["A2150889177"]
            assert author.display_name == "B. P. Abbott"

            author_works = (
                Works()
                .filter(author={"id": author.id})
                .filter(publication_year=2023)
                .get()
            )
            assert author_works.meta.count == 1

    def test_retry_on_rate_limit(self, fixtures):
        """Test retry logic on rate limit errors."""
        error_response = fixtures.error_response(429)
        success_response = fixtures.work_response()
        headers = fixtures.rate_limit_headers(remaining=0, reset_time=1)

        from openalex.cache.manager import CacheManager
        from openalex.config import OpenAlexConfig

        with (
            patch("httpx.Client.request") as mock_request,
            patch(
                "openalex.entities.get_cache_manager",
                return_value=CacheManager(OpenAlexConfig()),
            ),
            patch("time.sleep") as mock_sleep,
        ):
            mock_request.side_effect = [
                Mock(
                    json=lambda: error_response,
                    status_code=429,
                    headers=headers,
                ),
                Mock(json=lambda: success_response, status_code=200),
            ]

            work = Works()["W2755950973"]
            assert work.display_name is not None
            assert mock_sleep.called
            assert mock_request.call_count == 2

    def test_error_handling_cascade(self, fixtures):
        """Test various error scenarios."""
        from openalex.exceptions import (
            ValidationError,
            NotFoundError,
            ServerError,
            TemporaryError,
        )

        test_cases = [
            (400, ValidationError, "invalid filter"),
            (404, NotFoundError, "not found"),
            (500, ServerError, "server error"),
            (503, ServerError, "unavailable"),
        ]

        for status_code, expected_error, expected_msg in test_cases:
            error_response = fixtures.error_response(status_code)
            with patch("httpx.Client.request") as mock_request:
                mock_request.return_value = Mock(
                    json=lambda er=error_response: er,
                    status_code=status_code,
                )
                with pytest.raises(expected_error) as exc_info:
                    Works()["W123456789"]

            assert expected_msg in str(exc_info.value).lower()

    def test_select_fields_performance(self, fixtures):
        """Test that select reduces response size."""
        full_response = fixtures.work_response()
        minimal_response = {
            "id": full_response["id"],
            "display_name": full_response["display_name"],
            "publication_year": full_response["publication_year"],
        }

        from openalex.cache.manager import CacheManager
        from openalex.config import OpenAlexConfig

        with (
            patch("httpx.Client.request") as mock_request,
            patch(
                "openalex.entities.get_cache_manager",
                return_value=CacheManager(OpenAlexConfig()),
            ),
        ):
            mock_request.side_effect = [
                Mock(json=lambda: full_response, status_code=200),
                Mock(json=lambda: minimal_response, status_code=200),
            ]
            Works().select(
                [
                    "id",
                    "display_name",
                    "publication_year",
                ]
            ).get(per_page=1)

            calls = mock_request.call_args_list
            params = calls[0].kwargs.get("params", {})
            assert params.get("select") == "id,display_name,publication_year"
