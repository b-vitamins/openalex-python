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
    normalized: dict[str, Any] = {}
    for key, value in params.items():
        if key == "per_page":
            key = "per-page"
        elif key == "group_by":
            key = "group-by"
        if key == "select" and isinstance(value, list):
            normalized[key] = ",".join(value)
        else:
            normalized[key] = value
    return normalized


def strip_id_prefix(value: str) -> str:
    """Remove URL style prefixes from an OpenAlex identifier."""
    if "/" in value:
        return value.split("/")[-1]
    return value


def ensure_prefix(value: str, prefix: str) -> str:
    """Return ``value`` with ``prefix`` if missing."""
    if value.startswith(prefix):
        return value
    return f"{prefix}{value}"
