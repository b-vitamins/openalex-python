"""Utility helpers shared across the OpenAlex client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from collections.abc import Iterable

from ..constants import OPENALEX_ID_PREFIX
from ..models import ListResult, Meta

__all__ = [
    "OPENALEX_ID_PREFIX",
    "empty_list_result",
    "ensure_prefix",
    "extract_entity_type",
    "id_to_url",
    "ids_equal",
    "is_openalex_id",
    "normalize_entity_id",
    "normalize_id_batch",
    "parse_entity_ids",
    "strip_id_prefix",
    "validate_id_format",
]


@overload
def strip_id_prefix(value: None, prefix: str = OPENALEX_ID_PREFIX) -> None: ...


@overload
def strip_id_prefix(value: str, prefix: str = OPENALEX_ID_PREFIX) -> str: ...


def strip_id_prefix(
    value: str | None, prefix: str = OPENALEX_ID_PREFIX
) -> str | None:
    """Remove URL-style prefix from an OpenAlex identifier.

    If ``value`` is ``None`` an equivalent ``None`` is returned.  The
    remaining portion of the identifier is returned verbatim without
    splitting on ``/`` so keywords like ``"keywords/foo"`` are preserved.
    """
    if value is None:
        return None

    return value.removeprefix(prefix)


def is_openalex_id(value: str | None, prefix: str = OPENALEX_ID_PREFIX) -> bool:
    """Return ``True`` if ``value`` looks like an OpenAlex ID."""
    return bool(value) and isinstance(value, str) and value.startswith(prefix)


def ensure_prefix(value: str | None, prefix: str) -> str | None:
    """Return ``value`` with ``prefix`` added if missing.

    The check is case-insensitive so ``"w123"`` is considered to already
    have the ``"W"`` prefix and is returned unchanged.
    """
    if value is None:
        return None

    return value if value.lower().startswith(prefix.lower()) else prefix + value


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


_TYPE_PREFIX = {
    "work": "W",
    "author": "A",
    "institution": "I",
    "source": "S",
    "venue": "S",
    "concept": "C",
    "publisher": "P",
    "funder": "F",
    "topic": "T",
    "keyword": "keywords/",
}


def normalize_entity_id(value: str, entity_type: str) -> str:
    """Normalize an entity ID for a specific ``entity_type``."""
    entity_type = entity_type.lower()
    if entity_type not in _TYPE_PREFIX:
        message = f"Unknown entity type: {entity_type}"
        raise ValueError(message)

    prefix = _TYPE_PREFIX[entity_type]

    id_part = strip_id_prefix(value)

    if entity_type == "keyword":
        if id_part.startswith("keywords/"):
            slug = id_part.split("/", 1)[1]
        else:
            slug = id_part
        return f"keywords/{slug}"

    if id_part and id_part[0].isalpha():
        id_part = id_part[1:]

    return prefix + id_part


def extract_entity_type(value: str | None) -> str | None:
    """Return the entity type inferred from ``value``."""
    if not value:
        return None

    id_part = strip_id_prefix(value)

    if id_part.startswith("keywords/"):
        return "keyword"

    letter = id_part[0].upper() if id_part else ""
    for etype, pref in _TYPE_PREFIX.items():
        if pref.endswith("/"):
            continue
        if letter == pref:
            return etype
    return None


def validate_id_format(value: str | None, entity_type: str) -> bool:
    """Validate that ``value`` is a properly formatted ID for ``entity_type``."""
    if not value:
        return False

    entity_type = entity_type.lower()
    prefix = _TYPE_PREFIX.get(entity_type)
    if not prefix:
        return False

    id_part = strip_id_prefix(value)

    if entity_type == "keyword":
        return (
            id_part.startswith("keywords/")
            and len(id_part.split("/", 1)[1]) > 0
        )

    if len(id_part) <= 1 or not id_part[1:].isdigit():
        return False

    return id_part[0].upper() == prefix


def parse_entity_ids(
    ids: Iterable[str], *, entity_type: str, validate: bool = False
) -> list[str]:
    """Parse a list of IDs into normalized form."""

    result: list[str] = []
    for value in ids:
        if validate:
            id_part = strip_id_prefix(value)
            if (
                id_part
                and id_part[0].isalpha()
                and entity_type != "keyword"
                and id_part[0].upper() != _TYPE_PREFIX[entity_type]
            ):
                continue
        result.append(normalize_entity_id(value, entity_type))

    return result


def id_to_url(value: str | None) -> str | None:
    """Convert an ID to a full OpenAlex URL."""
    if not value:
        return None
    if value.startswith(OPENALEX_ID_PREFIX):
        return value

    id_part = strip_id_prefix(value)

    if id_part.startswith("keywords/"):
        return OPENALEX_ID_PREFIX + id_part

    if len(id_part) > 1 and id_part[0].isalpha() and id_part[1:].isdigit():
        return OPENALEX_ID_PREFIX + id_part.upper()

    return None


def normalize_id_batch(
    ids: Iterable[str | None], *, entity_type: str
) -> list[str | None]:
    """Normalize a batch of IDs preserving ``None`` or empty values."""

    normalized: list[str | None] = []
    for value in ids:
        if not value:
            normalized.append(value)
        else:
            normalized.append(normalize_entity_id(value, entity_type))
    return normalized


def ids_equal(id1: str | None, id2: str | None) -> bool:
    """Return ``True`` if two IDs represent the same entity."""
    if not id1 or not id2:
        return False

    return strip_id_prefix(id1).lower() == strip_id_prefix(id2).lower()
