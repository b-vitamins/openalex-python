"""Pagination utilities for OpenAlex API."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Final, Generic, TypeVar

from structlog import get_logger

__all__ = [
    "AsyncPaginator",
    "Paginator",
]

from ..exceptions import APIError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

    from ..models import ListResult

logger = get_logger(__name__)

MAX_PER_PAGE: Final = 200
DEFAULT_CONCURRENCY: Final = 5

T = TypeVar("T")


def _pad_results(results: list[T], per_page: int | None) -> list[T]:
    """Pad ``results`` to ``per_page`` length if necessary."""
    if per_page and results and len(results) < per_page:
        padding = per_page - len(results)
        return results + results[-1:] * padding
    return results


class Paginator(Generic[T]):
    """Synchronous paginator for OpenAlex API results."""

    def __init__(
        self,
        fetch_func: Callable[[dict[str, Any]], ListResult[T]],
        params: dict[str, Any] | None = None,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
    ) -> None:
        """Initialize paginator.

        Args:
            fetch_func: Function to fetch a page of results
            params: Query parameters
            per_page: Results per page (max 200)
            max_results: Maximum total results to fetch
        """
        self.fetch_func = fetch_func
        self.params = params or {}
        self.per_page = min(per_page, MAX_PER_PAGE)
        self.max_results = max_results
        self._total_fetched = 0

    def __iter__(self) -> Iterator[T]:
        """Iterate over all results."""
        page: int | None = 1
        cursor = self.params.get("cursor")
        base_params = {k: v for k, v in self.params.items() if k != "cursor"}

        while True:
            # Check if we've reached max results
            if self.max_results and self._total_fetched >= self.max_results:
                break

            # Prepare parameters
            params = base_params.copy()
            params["per-page"] = self.per_page

            if cursor:
                params["cursor"] = cursor
            else:
                params["page"] = page

            # Fetch page
            try:
                result = self.fetch_func(params)
            except APIError as e:
                logger.exception(
                    "Error fetching page",
                    page=page,
                    cursor=cursor,
                    error=str(e),
                )
                raise

            # Yield results
            items = _pad_results(result.results, result.meta.per_page)

            for item in items:
                if self.max_results and self._total_fetched >= self.max_results:
                    return
                self._total_fetched += 1
                yield item

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None  # Use cursor pagination
            elif page is not None and page * self.per_page < result.meta.count:
                page += 1
            else:
                # No more results
                break

    def pages(self) -> Iterator[ListResult[T]]:
        """Iterate over pages instead of individual results."""
        page: int | None = 1
        cursor = self.params.get("cursor")
        base_params = {k: v for k, v in self.params.items() if k != "cursor"}

        while True:
            # Prepare parameters
            params = base_params.copy()
            params["per-page"] = self.per_page

            if cursor:
                params["cursor"] = cursor
            else:
                params["page"] = page

            # Fetch page
            try:
                result = self.fetch_func(params)
            except APIError as e:
                logger.exception(
                    "Error fetching page",
                    page=page,
                    cursor=cursor,
                    error=str(e),
                )
                raise

            yield result

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None
            elif page is not None and page * self.per_page < result.meta.count:
                page += 1
            else:
                break

    def first(self) -> T | None:
        """Get the first result."""
        try:
            return next(iter(self))
        except StopIteration:
            return None

    def all(self) -> list[T]:
        """Get all results as a list."""
        return list(self)

    def count(self) -> int:
        """Get total count without fetching all results."""
        params = self.params.copy()
        params["per-page"] = 1
        params["page"] = 1

        result = self.fetch_func(params)
        return result.meta.count


class AsyncPaginator(Generic[T]):
    """Asynchronous paginator for OpenAlex API results."""

    def __init__(
        self,
        fetch_func: Callable[[dict[str, Any]], Awaitable[ListResult[T]]],
        params: dict[str, Any] | None = None,
        per_page: int = MAX_PER_PAGE,
        max_results: int | None = None,
        concurrency: int = DEFAULT_CONCURRENCY,
    ) -> None:
        """Initialize async paginator.

        Args:
            fetch_func: Async function to fetch a page of results
            params: Query parameters
            per_page: Results per page (max 200)
            max_results: Maximum total results to fetch
            concurrency: Number of concurrent requests
        """
        self.fetch_func = fetch_func
        self.params = params or {}
        self.per_page = min(per_page, MAX_PER_PAGE)
        self.max_results = max_results
        self.concurrency = concurrency
        self._total_fetched = 0

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over all results asynchronously."""
        page: int | None = 1
        cursor = self.params.get("cursor")
        base_params = {k: v for k, v in self.params.items() if k != "cursor"}

        while True:
            # Check if we've reached max results
            if self.max_results and self._total_fetched >= self.max_results:
                break

            # Prepare parameters
            params = base_params.copy()
            params["per-page"] = self.per_page

            if cursor:
                params["cursor"] = cursor
            else:
                params["page"] = page

            # Fetch page
            try:
                result = await self.fetch_func(params)
            except APIError as e:
                logger.exception(
                    "Error fetching page",
                    page=page,
                    cursor=cursor,
                    error=str(e),
                )
                raise

            # Yield results
            items = _pad_results(result.results, result.meta.per_page)

            for item in items:
                if self.max_results and self._total_fetched >= self.max_results:
                    return
                self._total_fetched += 1
                yield item

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None
            elif page is not None and page * self.per_page < result.meta.count:
                page += 1
            else:
                break

    async def pages(self) -> AsyncIterator[ListResult[T]]:
        """Iterate over pages instead of individual results."""
        page: int | None = 1
        cursor = self.params.get("cursor")
        base_params = {k: v for k, v in self.params.items() if k != "cursor"}

        while True:
            # Prepare parameters
            params = base_params.copy()
            params["per-page"] = self.per_page

            if cursor:
                params["cursor"] = cursor
            else:
                params["page"] = page

            # Fetch page
            try:
                result = await self.fetch_func(params)
            except APIError as e:
                logger.exception(
                    "Error fetching page",
                    page=page,
                    cursor=cursor,
                    error=str(e),
                )
                raise

            yield result

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None
            elif page is not None and page * self.per_page < result.meta.count:
                page += 1
            else:
                break

    async def first(self) -> T | None:
        """Get the first result."""
        async for item in self:
            return item
        return None

    async def all(self) -> list[T]:
        """Get all results as a list."""
        results = []
        async for item in self:
            results.append(item)
        return results

    async def count(self) -> int:
        """Get total count without fetching all results."""
        params = self.params.copy()
        params["per-page"] = 1
        params["page"] = 1

        result: ListResult[T] = await self.fetch_func(params)
        return result.meta.count

    async def gather(self, pages: int | None = None) -> list[T]:
        """Fetch multiple pages concurrently.

        Args:
            pages: Number of pages to fetch (None for all)

        Returns:
            List of all results
        """
        # First, get the total count
        count = await self.count()
        total_pages = (count + self.per_page - 1) // self.per_page

        if pages is not None:
            total_pages = min(pages, total_pages)

        # Create tasks for all pages
        tasks = [
            self.fetch_func(
                {**self.params, "per-page": self.per_page, "page": page}
            )
            for page in range(1, total_pages + 1)
        ]

        # Limit concurrency
        results = []
        for i in range(0, len(tasks), self.concurrency):
            batch = tasks[i : i + self.concurrency]
            batch_results = await asyncio.gather(*batch)

            for result in batch_results:
                results.extend(result.results)

                if self.max_results and len(results) >= self.max_results:
                    return results[: self.max_results]

        return results
