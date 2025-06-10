"""Utility helpers shared across the OpenAlex client."""

from __future__ import annotations

from typing import Any

from ..constants import OPENALEX_ID_PREFIX
from ..models import ListResult, Meta

__all__ = [
    "OPENALEX_ID_PREFIX",
    "empty_list_result",
    "ensure_prefix",
    "strip_id_prefix",
]


def strip_id_prefix(value: str, prefix: str = OPENALEX_ID_PREFIX) -> str:
    """Remove URL-style prefix from an OpenAlex identifier."""
    trimmed = value.removeprefix(prefix)
    return trimmed.rsplit("/", 1)[-1]


def ensure_prefix(value: str, prefix: str) -> str:
    """Return ``value`` with ``prefix`` if missing."""
    return value if value.startswith(prefix) else f"{prefix}{value}"


def empty_list_result() -> ListResult[Any]:
    """Return an empty ``ListResult`` instance."""
    return ListResult(
        meta=Meta(
            count=0,
            db_response_time_ms=0,
            page=1,
            per_page=0,
            groups_count=0,
            next_cursor=None,
        ),
        results=[],
    )
