"""Utility helpers shared across the OpenAlex client."""

from __future__ import annotations

from typing import Any

from ..constants import OPENALEX_ID_PREFIX
from ..models import ListResult, Meta

__all__ = [
    "OPENALEX_ID_PREFIX",
    "empty_list_result",
    "ensure_prefix",
    "is_openalex_id",
    "strip_id_prefix",
]


def strip_id_prefix(value: str, prefix: str = OPENALEX_ID_PREFIX) -> str:
    """Remove URL-style prefix from an OpenAlex identifier."""
    trimmed = value.removeprefix(prefix)
    return trimmed.rsplit("/", 1)[-1]


def is_openalex_id(value: str, prefix: str = OPENALEX_ID_PREFIX) -> bool:
    """Return ``True`` if ``value`` looks like an OpenAlex ID."""
    return isinstance(value, str) and value.startswith(prefix)


def ensure_prefix(value: str, prefix: str) -> str:
    """Ensure ``value`` starts with ``prefix``."""
    return value if value.startswith(prefix) else f"{prefix}{value}"


def empty_list_result() -> ListResult[Any]:
    """Return an empty ``ListResult`` instance with ``Meta`` stub."""
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
