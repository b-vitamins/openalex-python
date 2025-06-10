"""Utility helpers shared across the OpenAlex client."""

from __future__ import annotations

from typing import Any, Final

from ..constants import OPENALEX_ID_PREFIX
from ..models import ListResult, Meta

__all__ = [
    "OPENALEX_ID_PREFIX",
    "empty_list_result",
    "ensure_prefix",
    "normalize_params",
    "strip_id_prefix",
]


KEY_MAP: Final[dict[str, str]] = {
    "per_page": "per-page",
    "group_by": "group-by",
}


def _normalize_keys(params: dict[str, Any]) -> dict[str, Any]:
    """Return a new mapping with API parameter names normalized."""
    return {KEY_MAP.get(k, k): v for k, v in params.items()}


def normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Normalize parameter keys and values for API requests."""
    cleaned = _normalize_keys(params)
    normalized: dict[str, Any] = {}
    for key, value in cleaned.items():
        if key == "select" and isinstance(value, list):
            normalized[key] = ",".join(value)
        else:
            normalized[key] = value
    return normalized


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
