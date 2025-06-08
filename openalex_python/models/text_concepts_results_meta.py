"""Metadata about text concept extraction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextConceptsResultsMeta:
    """Counts accompanying concept extraction results."""

    concepts_count: int | None = None
