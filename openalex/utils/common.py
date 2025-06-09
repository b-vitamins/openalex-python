"""Utility helpers shared across the OpenAlex client."""

from __future__ import annotations

from typing import Any

__all__ = [
    "ensure_prefix",
    "normalize_params",
    "strip_id_prefix",
]


def normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Normalize parameter keys and values for API requests."""
    key_map = {"per_page": "per-page", "group_by": "group-by"}
    return {
        key_map.get(k, k): ",".join(v)
        if k == "select" and isinstance(v, list)
        else v
        for k, v in params.items()
    }


def strip_id_prefix(value: str) -> str:
    """Remove URL style prefixes from an OpenAlex identifier."""
    return value.rsplit("/", 1)[-1]


def ensure_prefix(value: str, prefix: str) -> str:
    """Return ``value`` with ``prefix`` if missing."""
    if value.startswith(prefix):
        return value
    return f"{prefix}{value}"
