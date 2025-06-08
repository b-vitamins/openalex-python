"""Keyword entry from text analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextKeyword:
    """Keyword associated with a work or query."""

    id: str
    display_name: str
    score: float
