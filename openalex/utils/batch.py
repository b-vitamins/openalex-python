from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from collections.abc import Iterator

__all__ = ["chunk_list"]


def chunk_list(items: list[Any], chunk_size: int) -> Iterator[list[Any]]:
    """Split list into chunks of specified size."""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]
