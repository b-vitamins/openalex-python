from __future__ import annotations

from typing import Any

import pytest

from openalex.exceptions import APIError
from openalex.models import ListResult, Meta, Work
from openalex.utils import AsyncPaginator, Paginator


def _make_page(start: int, per_page: int, total: int, cursor: str | None = None) -> ListResult[Work]:
    meta = Meta(
        count=total,
        db_response_time_ms=1,
        page=start // per_page + 1,
        per_page=per_page,
        next_cursor=cursor,
    )
    results = [Work(id=f"W{i}", display_name=f"Work {i}") for i in range(start, start + per_page)]
    return ListResult(meta=meta, results=results)


def test_paginator_iteration() -> None:
    total = 5

    def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        next_cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, next_cursor)

    paginator = Paginator(fetch, per_page=2)
    items = list(paginator)
    assert [w.id for w in items] == ["W0", "W1", "W2", "W3", "W4"]
    assert paginator.first().id == "W0"
    assert paginator.count() == total


@pytest.mark.asyncio
async def test_async_paginator_gather() -> None:
    total = 5

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        page = int(params.get("page", 1))
        per_page = int(params.get("per-page", 2))
        start = (page - 1) * per_page
        cursor = "next" if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=2)
    results = await paginator.gather()
    assert len(results) == total
    assert results[0].id == "W0"


def test_paginator_pages_and_max_results() -> None:
    total = 6

    def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = Paginator(fetch, per_page=2, max_results=3)
    items = list(paginator)
    assert len(items) == 3

    paginator2 = Paginator(fetch, per_page=2)
    pages = list(paginator2.pages())
    assert len(pages) == 3


def test_paginator_error() -> None:
    def fetch(_: dict[str, Any]) -> ListResult[Work]:
        msg = "oops"
        raise APIError(msg, status_code=500)

    paginator = Paginator(fetch)
    with pytest.raises(APIError):
        list(paginator)


@pytest.mark.asyncio
async def test_async_paginator_pages_first_all() -> None:
    total = 5

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        per_page = int(params.get("per-page", 2))
        page = int(params.get("cursor", params.get("page", 1)))
        start = (page - 1) * per_page
        cursor = str(page + 1) if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=2)
    pages = []
    async for p in paginator.pages():
        pages.append(p)
    assert len(pages) == 3
    assert await paginator.first()
    results = await paginator.all()
    assert len(results) == total


@pytest.mark.asyncio
async def test_async_paginator_error() -> None:
    async def fetch(_: dict[str, Any]) -> ListResult[Work]:
        msg = "bad"
        raise APIError(msg, status_code=500)

    paginator = AsyncPaginator(fetch)
    # Ruff's PT012 rule expects a simple statement inside ``pytest.raises``.
    # However, we need to iterate to trigger the exception.
    with pytest.raises(APIError):  # noqa: PT012
        async for _ in paginator:
            pass


@pytest.mark.asyncio
async def test_async_paginator_gather_max_results() -> None:
    total = 10

    async def fetch(params: dict[str, Any]) -> ListResult[Work]:
        page = int(params.get("page", 1))
        per_page = int(params.get("per-page", 3))
        start = (page - 1) * per_page
        cursor = "next" if start + per_page < total else None
        return _make_page(start, min(per_page, total - start), total, cursor)

    paginator = AsyncPaginator(fetch, per_page=3, concurrency=2)
    results = await paginator.gather(pages=2)
    assert len(results) == 6
