"""Parameter serialization utilities."""

from __future__ import annotations

from typing import Any, Final
from urllib.parse import quote_plus

from ..query import _LogicalExpression, or_

KEY_MAP: Final[dict[str, str]] = {
    "per_page": "per-page",
    "group_by": "group-by",
}

__all__ = [
    "flatten_filter_dict",
    "normalize_params",
    "serialize_filter_value",
    "serialize_params",
]


def serialize_filter_value(value: Any) -> str:
    """Serialize a filter value for the API.

    Handles:
    - Logical expressions (not_, gt_, lt_)
    - Lists (converted to pipe-separated values)
    - Booleans (lowercase strings)
    - Regular values (URL encoded)
    """
    # Handle logical expressions
    if isinstance(value, _LogicalExpression):
        # Recursively serialize the inner value
        inner = serialize_filter_value(value.value)
        return f"{value.token}{inner}"

    # Handle booleans - OpenAlex expects lowercase
    if isinstance(value, bool):
        return str(value).lower()

    # Handle lists - join with pipe for OR operation
    if isinstance(value, list):
        return "|".join(serialize_filter_value(v) for v in value)

    # Handle None/null
    if value is None:
        return "null"

    # URL encode strings and other values
    return quote_plus(str(value))


def flatten_filter_dict(
    filters: dict[str, Any],
    prefix: str = "",
    logical: str = ",",
) -> str:
    """Flatten a nested filter dictionary into OpenAlex filter syntax.

    Args:
        filters: Dictionary of filters
        prefix: Prefix for nested keys
        logical: Logical operator ("," for AND, "|" for OR)

    Returns:
        Flattened filter string
    """
    if not filters:
        return ""

    if isinstance(filters, or_):
        logical = "|"

    parts: list[str] = []
    for key, value in filters.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict) and not isinstance(value, or_):
            nested = flatten_filter_dict(value, full_key, ",")
            if nested:
                parts.append(nested)
        else:
            serialized = serialize_filter_value(value)
            parts.append(f"{full_key}:{serialized}")

    return logical.join(parts)


def serialize_params(params: dict[str, Any]) -> dict[str, str]:
    """Serialize parameters for API requests.

    Handles special serialization for:
    - filter: Complex nested structures with logical operators
    - sort: Key:value pairs joined by commas
    - select: List to comma-separated string
    - Standard values: Convert to strings
    """
    serialized: dict[str, str] = {}

    for key, value in params.items():
        if key == "filter" and isinstance(value, dict):
            filter_str = flatten_filter_dict(value)
            if filter_str:
                serialized["filter"] = filter_str
        elif key == "sort" and isinstance(value, dict):
            sort_parts = [f"{k}:{v}" for k, v in value.items()]
            serialized["sort"] = ",".join(sort_parts)
        elif key == "select" and isinstance(value, list):
            serialized["select"] = ",".join(value)
        elif value is not None:
            if isinstance(value, bool):
                serialized[key] = str(value).lower()
            else:
                serialized[key] = str(value)

    return serialized


# Update existing normalize_params if it exists
def normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Normalize parameters for API requests."""
    # Remove None values
    cleaned = {k: v for k, v in params.items() if v is not None}

    # Serialize complex structures
    serialized = serialize_params(cleaned)

    return {KEY_MAP.get(k, k): v for k, v in serialized.items()}
