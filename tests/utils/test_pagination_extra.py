import asyncio
from typing import Any

import pytest

from openalex.models import ListResult, Meta
from openalex.utils.pagination import (
    _build_params,
    _pad_results,
    AsyncPaginator,
    Paginator,
)


class DummyMeta(Meta):
    pass


def make_list_result(results: list[Any], page: int, per_page: int, next_cursor: str | None = None, count: int | None = None) -> ListResult[Any]:
    meta = Meta(
        count=count if count is not None else len(results),
        db_response_time_ms=0,
        page=page,
        per_page=per_page,
        next_cursor=next_cursor,
    )
    return ListResult[Any](meta=meta, results=results)


def test_pad_results_and_build_params() -> None:
    assert _pad_results([], 5) == []
    assert _pad_results([1, 2], None) == [1, 2]
    assert _pad_results([1, 2], 4) == [1, 2, 2, 2]

    base = {"a": 1}
    params = _build_params(base, cursor="c", page=None, per_page=2)
    assert params == {"a": 1, "cursor": "c", "per_page": 2}
    params = _build_params(base, cursor=None, page=3, per_page=2)
    assert params == {"a": 1, "page": 3, "per_page": 2}


def test_paginator_first_all_and_count() -> None:
    pages = {
        1: make_list_result(["a"], 1, 1, next_cursor="c2", count=2),
        2: make_list_result(["b"], 2, 1, next_cursor=None, count=2),
    }

    def fetch(params: dict[str, Any]) -> ListResult[str]:
        page = int(params.get("page", 1))
        return pages[page]

    paginator = Paginator(fetch, per_page=1)
    assert paginator.first() == "a"
    assert paginator.all() == ["a", "b"]
    assert paginator.count() == 2


@pytest.mark.asyncio
async def test_async_paginator_methods() -> None:
    async def fetch(params: dict[str, Any]) -> ListResult[int]:
        page = int(params.get("page", 1))
        next_cursor = "c2" if page == 1 else None
        return make_list_result([page], page, 1, next_cursor=next_cursor, count=2)

    paginator = AsyncPaginator(fetch, per_page=1, concurrency=2)
    assert await paginator.first() == 1
    assert await paginator.count() == 1  # count uses SINGLE_PER_PAGE

    all_items = await paginator.all()
    assert all_items == [1, 2]

    gathered = await paginator.gather(pages=2)
    assert gathered == [1, 2]
