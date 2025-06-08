"""Metadata about text results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextMeta:
    """Counts of text entities returned from the API."""

    keywords_count: int | None = None
    topics_count: int | None = None
    concepts_count: int | None = None
