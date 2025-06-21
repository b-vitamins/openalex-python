"""Tests for pagination utilities and edge cases."""

import asyncio
from typing import Any

import pytest

from openalex.exceptions import APIError
from openalex.models import ListResult, Meta
from openalex.utils.pagination import (
    _build_params,
    _pad_results,
    AsyncPaginator,
    Paginator,
)


@pytest.mark.unit
class TestPaginationUtilities:
    """Test that pagination utility functions handle edge cases correctly."""

    def make_meta(self, count=2, page=1, per_page=1, next_cursor=None):
        """Create a mock Meta object for testing."""
        return Meta(
            count=count,
            db_response_time_ms=0,
            page=page,
            per_page=per_page,
            next_cursor=next_cursor,
        )

    def make_list_result(
        self, results, page=1, per_page=1, next_cursor=None, count=None
    ):
        """Create a mock ListResult object for testing."""
        return ListResult(
            meta=self.make_meta(
                count=len(results) if count is None else count,
                page=page,
                per_page=per_page,
                next_cursor=next_cursor,
            ),
            results=results,
        )

    def test_pad_results_various_scenarios(self):
        """Test that pad results function handles various scenarios correctly."""
        # Empty list
        assert _pad_results([], 5) == []

        # None target length
        assert _pad_results([1, 2], None) == [1, 2]

        # Padding needed
        assert _pad_results([1, 2], 4) == [1, 2, 2, 2]

        # No padding needed
        assert _pad_results([1, 2, 3], 2) == [1, 2, 3]

    def test_build_params_all_branches(self):
        """Test that build params function handles all parameter combinations."""
        base = {"a": 1}

        # With cursor
        params = _build_params(base, cursor="c", page=None, per_page=2)
        assert params == {"a": 1, "cursor": "c", "per-page": 2}

        # With page
        params = _build_params(base, cursor=None, page=3, per_page=2)
        assert params == {"a": 1, "page": 3, "per-page": 2}

        # With both cursor and page (cursor takes precedence)
        params = _build_params(base, cursor="c", page=3, per_page=2)
        assert params == {"a": 1, "cursor": "c", "per-page": 2}

    def test_paginator_empty_fetch(self):
        """Test that paginator handles empty fetch results correctly."""

        def empty_fetch(params):
            return self.make_list_result([], count=0)

        paginator = Paginator(empty_fetch, per_page=10)
        assert paginator.first() is None
        assert paginator.all() == []
        assert paginator.count() == 0

    def test_paginator_max_results_parameter(self):
        """Test that paginator respects max_results parameter correctly."""

        def fetch(params):
            page = params.get("page", 1)
            if page == 1:
                return self.make_list_result(["a", "b"], count=4)
            elif page == 2:
                return self.make_list_result(["c", "d"], count=4)
            return self.make_list_result([], count=4)

        paginator = Paginator(fetch, per_page=2, max_results=3)
        results = paginator.all()
        assert len(results) == 3
        assert results == ["a", "b", "c"]

    def test_paginator_raises_and_logging(self):
        """Test that paginator handles errors and logging correctly."""

        def error_fetch(params):
            raise APIError("Test error")

        paginator = Paginator(error_fetch, per_page=10)

        with pytest.raises(APIError):
            paginator.first()

    @pytest.mark.asyncio
    async def test_async_paginator_max_results_and_gather(self):
        """Test that async paginator respects max_results and gather works correctly."""

        async def fetch(params):
            page = params.get("page", 1)
            if page == 1:
                return self.make_list_result([1, 2], count=6)
            elif page == 2:
                return self.make_list_result([3, 4], count=6)
            elif page == 3:
                return self.make_list_result([5, 6], count=6)
            return self.make_list_result([], count=6)

        paginator = AsyncPaginator(fetch, per_page=2, max_results=5)

        # Test gather with pages limit
        results = await paginator.gather(pages=2)
        assert len(results) == 4
        assert results == [1, 2, 3, 4]

        # Test all with max_results
        all_results = await paginator.all()
        assert len(all_results) == 5
        assert all_results == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_async_paginator_error_handling(self):
        """Test that async paginator handles errors correctly."""

        async def error_fetch(params):
            raise APIError("Async test error")

        paginator = AsyncPaginator(error_fetch, per_page=10)

        with pytest.raises(APIError):
            await paginator.first()

    def test_paginator_iter_pages_properties(self):
        """Test that paginator pages iterator works correctly."""

        def fetch(params):
            page = params.get("page", 1)
            cursor = params.get("cursor")

            if cursor == "c2":
                return self.make_list_result(
                    ["b"], page=2, per_page=1, next_cursor=None, count=2
                )
            elif page == 1:
                return self.make_list_result(
                    ["a"], page=1, per_page=1, next_cursor="c2", count=2
                )
            else:
                return self.make_list_result(
                    [], page=page, per_page=1, next_cursor=None, count=2
                )

        paginator = Paginator(fetch, per_page=1)

        # Test pages
        pages = list(paginator.pages())
        assert len(pages) == 2
        assert pages[0].results == ["a"]
        assert pages[1].results == ["b"]

    @pytest.mark.asyncio
    async def test_async_paginator_properties_and_count(self):
        """Test that async paginator properties and count work correctly."""

        async def fetch(params):
            return self.make_list_result([1, 2, 3], count=10)

        paginator = AsyncPaginator(fetch, per_page=3, concurrency=2)

        # Test count
        count = await paginator.count()
        assert count == 10

        # Test first
        first = await paginator.first()
        assert first == 1

    def test_paginator_first_all_and_count_methods(self):
        """Test that paginator first, all, and count methods work correctly."""
        pages = {
            1: self.make_list_result(["a"], 1, 1, next_cursor="c2", count=2),
            2: self.make_list_result(["b"], 2, 1, next_cursor=None, count=2),
        }

        def fetch(params):
            if params.get("cursor") == "c2":
                return pages[2]
            if params.get("cursor"):
                return self.make_list_result(
                    [], 0, 1, next_cursor=None, count=2
                )
            try:
                page = int(params.get("page", 1) or 1)
            except Exception:
                page = 1
            if page == 1:
                return pages[1]
            elif page == 2:
                return pages[2]
            return self.make_list_result([], page, 1, next_cursor=None, count=2)

        paginator = Paginator(fetch, per_page=1)
        assert paginator.first() == "a"
        assert paginator.all() == ["a", "b"]
        assert paginator.count() == 2

    @pytest.mark.asyncio
    async def test_async_paginator_methods_comprehensive(self):
        """Test that async paginator methods work comprehensively."""

        async def fetch(params):
            page = params.get("page")
            cursor = params.get("cursor")
            if (page == 1 or page == "1") and cursor is None:
                return self.make_list_result(
                    [1], 1, 1, next_cursor="c2", count=2
                )
            if cursor == "c2" or page == 2 or page == "2":
                return self.make_list_result(
                    [2], 2, 1, next_cursor=None, count=2
                )
            # Any other combination - halt loop immediately
            return self.make_list_result([], 0, 1, next_cursor=None, count=2)

        paginator = AsyncPaginator(fetch, per_page=1, concurrency=2)

        assert await paginator.first() == 1
        assert (
            await paginator.count() == 2
        )  # count uses the mocked Meta.count, not results len

        all_items = await paginator.all()
        assert all_items == [1, 2]

        gathered = await paginator.gather(pages=2)
        assert gathered == [1, 2]
