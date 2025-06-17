"""Test pagination edge cases and cursor behavior."""

from unittest.mock import Mock, patch

import pytest

from openalex import Works
from tests.fixtures.api_responses import APIResponseFixtures


class TestPaginationEdgeCases:
    """Test pagination edge cases."""

    @pytest.fixture
    def fixtures(self):
        return APIResponseFixtures()

    def test_empty_results(self, fixtures):
        """Test handling of empty result sets."""
        empty_response = {
            "meta": {"count": 0, "page": 1, "per_page": 25},
            "results": [],
            "group_by": [],
        }

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                json=lambda: empty_response, status_code=200
            )
            paginator = (
                Works().filter(title="nonexistent_paper_12345").paginate()
            )
            page1 = next(paginator)
            assert page1.meta.count == 0
            assert len(page1.results) == 0
            with pytest.raises(StopIteration):
                next(paginator)

    def test_single_page_results(self, fixtures):
        """Test results that fit in a single page."""
        response = fixtures.search_response("test", page=1, per_page=200)
        response["meta"]["count"] = 15
        response["results"] = response["results"][:15]

        empty_page = {
            "meta": {"count": 15, "page": 2, "per_page": 200},
            "results": [],
            "group_by": [],
        }

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(json=lambda: response, status_code=200),
                Mock(json=lambda: empty_page, status_code=200),
            ]
            paginator = Works().search("test").paginate(per_page=200)
            page1 = next(paginator)
            assert page1.meta.count == 15
            assert len(page1.results) == 15
            page2 = next(paginator)
            assert len(page2.results) == 0
            with pytest.raises(StopIteration):
                next(paginator)

    def test_cursor_pagination(self, fixtures):
        """Test cursor-based pagination."""
        page1 = {
            "meta": {
                "count": 1000,
                "page": 1,
                "per_page": 100,
                "next_cursor": "cursor_abc123",
            },
            "results": [
                {"id": f"W{i}", "display_name": f"Work {i}"} for i in range(100)
            ],
        }
        page2 = {
            "meta": {
                "count": 1000,
                "page": 2,
                "per_page": 100,
                "next_cursor": "cursor_def456",
            },
            "results": [
                {"id": f"W{i}", "display_name": f"Work {i}"}
                for i in range(100, 200)
            ],
        }
        page3 = {
            "meta": {
                "count": 1000,
                "page": 10,
                "per_page": 100,
                "next_cursor": None,
            },
            "results": [
                {"id": f"W{i}", "display_name": f"Work {i}"}
                for i in range(900, 1000)
            ],
        }

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(json=lambda: page1, status_code=200),
                Mock(json=lambda: page2, status_code=200),
                Mock(json=lambda: page3, status_code=200),
            ]
            paginator = (
                Works().filter(publication_year=2023).paginate(per_page=100)
            )
            first = next(paginator)
            assert first.meta.next_cursor == "cursor_abc123"

            second = next(paginator)
            assert second.meta.next_cursor == "cursor_def456"

            third = next(paginator)
            assert third.meta.next_cursor is None
            with pytest.raises(StopIteration):
                next(paginator)

    def test_paginate_max_results(self, fixtures):
        """Test paginate() with max_results limit."""
        responses = []
        for i in range(5):
            response = fixtures.search_response("test", page=i + 1, per_page=50)
            response["meta"]["count"] = 500
            responses.append(Mock(json=lambda r=response: r, status_code=200))

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = responses
            paginator = (
                Works().search("test").paginate(per_page=50, max_results=125)
            )
            all_results = list(paginator)

            total_results = sum(len(page.results) for page in all_results)
            assert total_results == 150
            assert len(all_results) == 3
            assert paginator.total_fetched == 125

    def test_large_per_page_limit(self, fixtures):
        """Test per_page limits."""
        large_response = {
            "meta": {"count": 500, "page": 1, "per_page": 200},
            "results": [{"id": f"W{i}"} for i in range(200)],
        }

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                json=lambda: large_response, status_code=200
            )
            results = Works().get(per_page=1000)
            assert results.meta.per_page == 200
