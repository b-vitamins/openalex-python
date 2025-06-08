"""Metadata for keyword extraction results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextKeywordsResultsMeta:
    """Counts accompanying keyword results."""

    keywords_count: int | None = None
