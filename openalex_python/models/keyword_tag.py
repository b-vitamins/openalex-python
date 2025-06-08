"""Keyword identified in a text query."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class KeywordTag:
    """Keyword with relevance score."""

    id: str
    display_name: str
    score: float
