from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from ..models import ListResult

T = TypeVar("T")


class StreamingPaginator(Iterator[T]):
    """Memory-efficient streaming paginator."""

    def __init__(
        self,
        fetch_func: Callable[[dict[str, Any]], ListResult[T]],
        params: dict[str, Any],
        per_page: int = 200,
        max_results: int | None = None,
    ) -> None:
        self._fetch_func = fetch_func
        self._params = params.copy()
        self._per_page = per_page
        self._max_results = max_results
        self._cursor: str | None = "*"
        self._current_page: ListResult[T] | None = None
        self._current_index = 0
        self._total_yielded = 0
        self._exhausted = False

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self._exhausted:
            raise StopIteration

        if self._max_results is not None and self._total_yielded >= self._max_results:
            self._exhausted = True
            raise StopIteration

        if self._current_page is None or self._current_index >= len(self._current_page.results):
            self._fetch_next_page()

        if self._current_page is None or not self._current_page.results:
            self._exhausted = True
            raise StopIteration

        result = self._current_page.results[self._current_index]
        self._current_index += 1
        self._total_yielded += 1
        return result

    def _fetch_next_page(self) -> None:
        if self._cursor is None:
            self._exhausted = True
            return

        params = {
            **self._params,
            "per_page": self._per_page,
            "cursor": self._cursor,
        }

        self._current_page = self._fetch_func(params)
        self._current_index = 0
        self._cursor = self._current_page.meta.next_cursor


class AsyncStreamingPaginator(AsyncIterator[T]):
    """Async memory-efficient streaming paginator."""

    def __init__(
        self,
        fetch_func: Callable[[dict[str, Any]], Awaitable[ListResult[T]]],
        params: dict[str, Any],
        per_page: int = 200,
        max_results: int | None = None,
    ) -> None:
        self._fetch_func = fetch_func
        self._params = params.copy()
        self._per_page = per_page
        self._max_results = max_results
        self._cursor: str | None = "*"
        self._current_page: ListResult[T] | None = None
        self._current_index = 0
        self._total_yielded = 0
        self._exhausted = False

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        if self._exhausted:
            raise StopAsyncIteration

        if self._max_results is not None and self._total_yielded >= self._max_results:
            self._exhausted = True
            raise StopAsyncIteration

        if self._current_page is None or self._current_index >= len(self._current_page.results):
            await self._fetch_next_page()

        if self._current_page is None or not self._current_page.results:
            self._exhausted = True
            raise StopAsyncIteration

        result = self._current_page.results[self._current_index]
        self._current_index += 1
        self._total_yielded += 1
        return result

    async def _fetch_next_page(self) -> None:
        if self._cursor is None:
            self._exhausted = True
            return

        params = {
            **self._params,
            "per_page": self._per_page,
            "cursor": self._cursor,
        }

        self._current_page = await self._fetch_func(params)
        self._current_index = 0
        self._cursor = self._current_page.meta.next_cursor
