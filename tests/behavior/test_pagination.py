"""
Test pagination behavior from API perspective.
Tests how pagination works for users, not implementation details.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio


class TestPaginationBehavior:
    """Test pagination functionality from user perspective."""

    def test_default_pagination_parameters(self):
        """Default pagination should use sensible defaults."""
        from openalex import Works

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [{"id": "W1"}],
                    "meta": {
                        "count": 100,
                        "page": 1,
                        "per_page": 25,
                        "db_response_time_ms": 10
                    }
                })
            )

            Works().get()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            # Should not specify page/per_page if using defaults
            assert "page" not in params
            assert "per-page" not in params

    def test_explicit_pagination_parameters(self):
        """Explicit page and per_page should be respected."""
        from openalex import Authors

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [],
                    "meta": {"count": 0}
                })
            )

            Authors().get(page=3, per_page=50)

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            assert params["page"] == "3"
            assert params["per-page"] == "50"

    def test_paginate_returns_iterator(self):
        """Paginate should return an iterator over pages."""
        from openalex import Institutions

        page_count = 0

        def mock_response(*args, **kwargs):
            nonlocal page_count
            page_count += 1

            if page_count <= 3:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": f"I{page_count}"}],
                        "meta": {
                            "count": 3,
                            "page": page_count,
                            "per_page": 1,
                            "next_cursor": f"page{page_count+1}" if page_count < 3 else None
                        }
                    })
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            institutions = Institutions()
            pages = list(institutions.filter(country_code="US").paginate(per_page=1))

            assert len(pages) == 3
            assert pages[0].results[0]["id"] == "I1"
            assert pages[2].results[0]["id"] == "I3"

    def test_all_iterates_through_items(self):
        """all() should iterate through individual items, not pages."""
        from openalex import Sources

        def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))

            if page == 1:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [
                            {"id": "S1", "display_name": "Nature"},
                            {"id": "S2", "display_name": "Science"}
                        ],
                        "meta": {"count": 3, "page": 1, "next_cursor": "page2"}
                    })
                )
            elif page == 2:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [
                            {"id": "S3", "display_name": "Cell"}
                        ],
                        "meta": {"count": 3, "page": 2, "next_cursor": None}
                    })
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            sources = Sources()
            all_sources = list(sources.filter(type="journal").all())

            assert len(all_sources) == 3
            assert all_sources[0].id == "S1"
            assert all_sources[2].id == "S3"

    def test_cursor_based_pagination(self):
        """Should use cursor when provided by API."""
        from openalex import Works

        cursors_seen = []

        def mock_response(*args, **kwargs):
            cursor = kwargs["params"].get("cursor")
            cursors_seen.append(cursor)

            if cursor is None:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "W1"}],
                        "meta": {
                            "count": 30,
                            "page": 1,
                            "next_cursor": "abc123"
                        }
                    })
                )
            elif cursor == "abc123":
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "W2"}],
                        "meta": {
                            "count": 30,
                            "page": 2,
                            "next_cursor": "def456"
                        }
                    })
                )
            else:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "W3"}],
                        "meta": {
                            "count": 30,
                            "page": 3,
                            "next_cursor": None
                        }
                    })
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            works = Works()
            list(works.filter(is_oa=True).paginate(per_page=1))

            assert cursors_seen == [None, "abc123", "def456"]

    def test_page_based_pagination_fallback(self):
        """Should fall back to page numbers when no cursor."""
        from openalex import Concepts

        pages_seen = []

        def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))
            pages_seen.append(page)

            return Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [{"id": f"C{page}"}] if page <= 3 else [],
                    "meta": {
                        "count": 3,
                        "page": page,
                        "per_page": 1,
                        "next_cursor": None  # No cursor provided
                    }
                })
            )

        with patch("httpx.Client.request", side_effect=mock_response):
            concepts = Concepts()
            list(concepts.filter(level=0).paginate(per_page=1))

            assert pages_seen == [1, 2, 3, 4]  # Stops when empty

    def test_pagination_respects_max_results(self):
        """Pagination should stop at max_results if specified."""
        from openalex import Publishers

        items_returned = 0

        def mock_response(*args, **kwargs):
            nonlocal items_returned
            page = int(kwargs["params"].get("page", 1))

            # Simulate 10 items per page
            items = [{"id": f"P{i}"} for i in range((page-1)*10, page*10)]
            items_returned += len(items)

            return Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": items,
                    "meta": {
                        "count": 100,
                        "page": page,
                        "per_page": 10
                    }
                })
            )

        with patch("httpx.Client.request", side_effect=mock_response):
            publishers = Publishers()
            # Request max 25 items (should get 3 pages)
            all_items = list(publishers.all(max_results=25))

            assert len(all_items) == 25
            # Should have made 3 API calls (10 + 10 + 5)

    def test_first_helper_method(self):
        """first() should return first item or None."""
        from openalex import Funders

        # Test with results
        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [
                        {"id": "F1", "display_name": "NSF"},
                        {"id": "F2", "display_name": "NIH"}
                    ],
                    "meta": {"count": 10}
                })
            )

            funder = Funders().filter(country_code="US").first()
            assert funder is not None
            assert funder.id == "F1"

        # Test with no results
        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [],
                    "meta": {"count": 0}
                })
            )

            funder = Funders().filter(country_code="XX").first()
            assert funder is None

    def test_count_method_efficient(self):
        """count() should only request minimal data."""
        from openalex import Topics

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [],
                    "meta": {"count": 42}
                })
            )

            count = Topics().filter(domain={"id": "D123"}).count()

            _, kwargs = mock_request.call_args
            params = kwargs.get("params", {})

            # Should request minimal page size
            assert params["per-page"] == "1"
            assert count == 42

    def test_pagination_preserves_filters(self):
        """Pagination should preserve all query filters."""
        from openalex import Works

        def mock_response(*args, **kwargs):
            return Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [{"id": "W1"}],
                    "meta": {"count": 100, "page": 1}
                })
            )

        with patch("httpx.Client.request", side_effect=mock_response) as mock_request:
            works = (Works()
                    .filter(is_oa=True)
                    .filter_gt(cited_by_count=100)
                    .search("climate change"))

            # Get different pages
            works.get(page=1)
            works.get(page=2)

            # Both calls should have same filters
            for call in mock_request.call_args_list:
                _, kwargs = call
                params = kwargs["params"]
                assert "is_oa:true" in params["filter"]
                assert "cited_by_count:>100" in params["filter"]
                assert params["search"] == "climate change"

    def test_large_per_page_values(self):
        """Should handle large per_page values correctly."""
        from openalex import Keywords

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [{"id": f"K{i}"} for i in range(200)],
                    "meta": {"count": 500, "page": 1, "per_page": 200}
                })
            )

            results = Keywords().get(per_page=200)

            _, kwargs = mock_request.call_args
            assert kwargs["params"]["per-page"] == "200"
            assert len(results.results) == 200

    @pytest.mark.asyncio
    async def test_async_pagination_basic(self):
        """Async pagination should work like sync pagination."""
        from openalex import AsyncAuthors

        async def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))

            if page <= 2:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": f"A{page}"}],
                        "meta": {
                            "count": 2,
                            "page": page,
                            "next_cursor": "next" if page < 2 else None
                        }
                    })
                )

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = mock_response

            authors = AsyncAuthors()
            all_authors = []

            async for author in authors.filter(works_count=">10").all():
                all_authors.append(author)

            assert len(all_authors) == 2
            assert all_authors[0].id == "A1"
            assert all_authors[1].id == "A2"

    @pytest.mark.asyncio
    async def test_async_paginator_gather(self):
        """Async gather should fetch multiple pages concurrently."""
        from openalex import AsyncWorks
        import time

        call_times = []

        async def mock_response(*args, **kwargs):
            call_times.append(time.time())
            await asyncio.sleep(0.1)  # Simulate network delay

            page = int(kwargs["params"].get("page", 1))
            return Mock(
                status_code=200,
                json=Mock(return_value={
                    "results": [{"id": f"W{page}"}],
                    "meta": {"count": 5, "page": page}
                })
            )

        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = mock_response

            works = AsyncWorks()
            paginator = works.filter(is_oa=True).paginate(per_page=1)

            start = time.time()
            results = await paginator.gather(pages=3)
            duration = time.time() - start

            assert len(results) == 3
            # Should complete faster than sequential (0.3s)
            assert duration < 0.2

            # Verify concurrent execution
            assert max(call_times) - min(call_times) < 0.05

    def test_empty_page_stops_pagination(self):
        """Pagination should stop when receiving empty page."""
        from openalex import Institutions

        def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))

            if page == 1:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "I1"}],
                        "meta": {"count": 10, "page": 1}
                    })
                )
            else:
                # Empty page
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [],
                        "meta": {"count": 10, "page": page}
                    })
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            institutions = Institutions()
            all_items = list(institutions.all())

            # Should only get first page's item
            assert len(all_items) == 1
            assert all_items[0].id == "I1"

    def test_pagination_error_handling(self):
        """Pagination should handle errors gracefully."""
        from openalex import Authors
        from openalex.exceptions import ServerError

        def mock_response(*args, **kwargs):
            page = int(kwargs["params"].get("page", 1))

            if page == 2:
                # Error on second page
                return Mock(
                    status_code=500,
                    json=Mock(return_value={"error": "Server error"})
                )
            else:
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": f"A{page}"}],
                        "meta": {"count": 10, "page": page}
                    })
                )

        with patch("httpx.Client.request", side_effect=mock_response):
            authors = Authors()

            # Should raise error when hitting bad page
            with pytest.raises(ServerError):
                list(authors.paginate(per_page=1))
