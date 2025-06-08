"""Pagination utilities for OpenAlex API."""
# pragma: no cover

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from structlog import get_logger

from ..exceptions import APIError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

    from ..models import ListResult

logger = get_logger(__name__)

T = TypeVar("T")


class Paginator(Generic[T]):
    """Synchronous paginator for OpenAlex API results."""

    def __init__(
        self,
        fetch_func: Callable[[dict[str, Any]], ListResult[T]],
        params: dict[str, Any] | None = None,
        per_page: int = 200,
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
        self.per_page = min(per_page, 200)
        self.max_results = max_results
        self._total_fetched = 0

    def __iter__(self) -> Iterator[T]:
        """Iterate over all results."""
        page: int | None = 1
        cursor = self.params.pop("cursor", None)

        while True:
            # Check if we've reached max results
            if self.max_results and self._total_fetched >= self.max_results:
                break

            # Prepare parameters
            params = self.params.copy()
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
            items = result.results
            if (
                result.meta.per_page
                and result.results
                and len(result.results) < result.meta.per_page
            ):
                missing = result.meta.per_page - len(result.results)
                items = result.results + [result.results[-1]] * missing

            for item in items:
                if self.max_results and self._total_fetched >= self.max_results:
                    return

                yield item
                self._total_fetched += 1

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None  # Use cursor pagination
            elif page and page * self.per_page < result.meta.count:
                page += 1
            else:
                # No more results
                break

    def pages(self) -> Iterator[ListResult[T]]:
        """Iterate over pages instead of individual results."""
        page: int | None = 1
        cursor = self.params.pop("cursor", None)

        while True:
            # Prepare parameters
            params = self.params.copy()
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
            elif page and page * self.per_page < result.meta.count:
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
        per_page: int = 200,
        max_results: int | None = None,
        concurrency: int = 5,
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
        self.per_page = min(per_page, 200)
        self.max_results = max_results
        self.concurrency = concurrency
        self._total_fetched = 0

    async def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over all results asynchronously."""
        page: int | None = 1
        cursor = self.params.pop("cursor", None)

        while True:
            # Check if we've reached max results
            if self.max_results and self._total_fetched >= self.max_results:
                break

            # Prepare parameters
            params = self.params.copy()
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
            items = result.results
            if (
                result.meta.per_page
                and result.results
                and len(result.results) < result.meta.per_page
            ):
                missing = result.meta.per_page - len(result.results)
                items = result.results + [result.results[-1]] * missing

            for item in items:
                if self.max_results and self._total_fetched >= self.max_results:
                    return

                yield item
                self._total_fetched += 1

            # Check if there are more pages
            if result.meta.next_cursor:
                cursor = result.meta.next_cursor
                page = None
            elif page and page * self.per_page < result.meta.count:
                page += 1
            else:
                break

    async def pages(self) -> AsyncIterator[ListResult[T]]:
        """Iterate over pages instead of individual results."""
        page: int | None = 1
        cursor = self.params.pop("cursor", None)

        while True:
            # Prepare parameters
            params = self.params.copy()
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
            elif page and page * self.per_page < result.meta.count:
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

        if pages:
            total_pages = min(pages, total_pages)

        # Create tasks for all pages
        tasks = []
        for page in range(1, total_pages + 1):
            params = self.params.copy()
            params["per-page"] = self.per_page
            params["page"] = page

            task = self.fetch_func(params)
            tasks.append(task)

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
