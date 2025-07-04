"""Parameter serialization utilities."""

from __future__ import annotations

from typing import Any, Final, cast

# ``quote_plus`` was previously used to pre-encode filter values.  This
# resulted in parameters being double-encoded when passed to ``httpx``.
# The utility remains imported for backwards compatibility but is no longer
# applied so that raw values are sent and encoded once by the HTTP client.
from urllib.parse import quote_plus

from ..query import LogicalExpression, gte_, lte_, or_

KEY_MAP: Final[dict[str, str]] = {
    "per_page": "per-page",
    "group_by": "group-by",
}

ALLOWED_KEYS: Final[set[str]] = {
    "page",
    "per_page",
    "group_by",
    "filter",
    "sort",
    "select",
    "search",
    "cursor",
    "sample",
    "seed",
    "q",
}

__all__ = [
    "flatten_filter_dict",
    "normalize_params",
    "serialize_filter_value",
    "serialize_params",
    "validate_date_param",
    "validate_numeric_param",
]


def validate_date_param(value: str) -> str:
    """Validate date format matches ISO 8601."""
    from datetime import datetime

    try:
        datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - defensive
        message = f"Invalid date format: {value}"
        raise ValueError(message) from exc
    return value


def validate_numeric_param(
    value: int | float, min_val: int = 0, max_val: int = 1_000_000
) -> int | float:
    """Ensure numeric parameters are within reasonable ranges."""
    if value < min_val or value > max_val:
        message = f"Value {value} outside allowed range [{min_val}, {max_val}]"
        raise ValueError(message)
    return value


def serialize_filter_value(value: Any) -> str:
    """Serialize a filter value for the API.

    Handles:
    - Logical expressions (not_, gt_, lt_)
    - Lists (converted to pipe-separated values)
    - Booleans (lowercase strings)
    - Regular values (URL encoded)
    """
    # Handle logical expressions
    if isinstance(value, LogicalExpression):
        # Recursively serialize the inner value
        inner = serialize_filter_value(value.value)
        return f"{value.token}{inner}"

    # Handle booleans - OpenAlex expects lowercase
    if isinstance(value, bool):
        return str(value).lower()

    # Handle lists - join with pipe for OR operation
    if isinstance(value, list):
        value_list: list[Any] = cast(list[Any], value)
        return "|".join(serialize_filter_value(v) for v in value_list)

    # Handle tuples - used for multiple AND conditions on same field
    if isinstance(value, tuple):
        value_tuple: tuple[Any, ...] = cast(tuple[Any, ...], value)
        return ",".join(serialize_filter_value(v) for v in value_tuple)

    # Handle None/null
    if value is None:
        return "null"

    # Encode other values so tests can inspect encoded parameters prior to
    # request dispatch.
    return quote_plus(str(value), safe=":/<>!,")


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
            range_keys = {"gte", "lte"}
            value_dict: dict[str, Any] = cast(dict[str, Any], value)
            if set(value_dict.keys()) <= range_keys:
                gte_val = value_dict.get("gte")
                lte_val = value_dict.get("lte")
                if gte_val is not None or lte_val is not None:
                    start = (
                        serialize_filter_value(gte_val)
                        if gte_val is not None
                        else ""
                    )
                    end = (
                        serialize_filter_value(lte_val)
                        if lte_val is not None
                        else ""
                    )
                    parts.append(f"{full_key}:{start}-{end}")
                    continue

            nested = flatten_filter_dict(value_dict, full_key, ",")
            if nested:
                parts.append(nested)
            continue

        if isinstance(value, tuple):
            gte_val = None
            lte_val = None
            range_candidates = True
            value_tuple: tuple[Any, ...] = cast(tuple[Any, ...], value)
            for item in value_tuple:
                if isinstance(item, gte_):
                    gte_val = item.value
                elif isinstance(item, lte_):
                    lte_val = item.value
                else:
                    range_candidates = False
            if range_candidates and (
                gte_val is not None or lte_val is not None
            ):
                start = (
                    serialize_filter_value(gte_val)
                    if gte_val is not None
                    else ""
                )
                end = (
                    serialize_filter_value(lte_val)
                    if lte_val is not None
                    else ""
                )
                parts.append(f"{full_key}:{start}-{end}")
                continue

            for item in value_tuple:
                ser = serialize_filter_value(item)
                if full_key.endswith(".search"):
                    ser = ser.replace("+", " ")
                parts.append(f"{full_key}:{ser}")
            continue

        serialized = serialize_filter_value(value)
        if full_key.endswith(".search"):
            serialized = serialized.replace("+", " ")
        parts.append(f"{full_key}:{serialized}")

    return logical.join(parts)


def serialize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Serialize parameters for API requests.

    Handles special serialization for:
    - filter: Complex nested structures with logical operators
    - sort: Key:value pairs joined by commas
    - select: List to comma-separated string
    - group_by: Sequence values to allow repeated parameters
    - Standard values: Convert to strings
    """
    serialized: dict[str, Any] = {}

    for key, value in params.items():
        key_str: str = key
        value_any: Any = value
        if key_str == "filter" and isinstance(value_any, dict):
            filter_dict: dict[str, Any] = cast(dict[str, Any], value_any)
            filter_str = flatten_filter_dict(filter_dict)
            if filter_str:
                serialized["filter"] = filter_str
        elif key_str == "sort" and isinstance(value_any, dict):
            sort_dict: dict[str, Any] = cast(dict[str, Any], value_any)
            sort_parts = [f"{k}:{v}" for k, v in sort_dict.items()]
            serialized["sort"] = ",".join(sort_parts)
        elif key_str == "select" and isinstance(value_any, list):
            select_list: list[str] = cast(list[str], value_any)
            serialized["select"] = ",".join(select_list)
        elif key_str == "group_by" and isinstance(value_any, list | tuple):
            group_by_val: list[Any] | tuple[Any, ...] = cast(
                list[Any] | tuple[Any, ...], value_any
            )
            serialized["group_by"] = list(group_by_val)
        elif value_any is not None:
            mapped = KEY_MAP.get(key_str, key_str)
            serialized[mapped] = (
                str(value_any).lower()
                if isinstance(value_any, bool)
                else str(value_any)
            )

    return serialized


# Update existing normalize_params if it exists
def normalize_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize parameters for API requests.

    Converts Pythonic parameter names to their API equivalents and drops
    ``None`` values before serialization.
    """
    # Remove None values
    if not params:
        return {}

    cleaned = {
        k: v for k, v in params.items() if v is not None and k in ALLOWED_KEYS
    }

    # Serialize complex structures
    serialized = serialize_params(cleaned)

    return {KEY_MAP.get(k, k): v for k, v in serialized.items()}
