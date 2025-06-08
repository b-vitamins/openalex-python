"""Metadata for topic extraction results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextTopicsResultsMeta:
    """Summary information about topics."""

    topics_count: int | None = None
