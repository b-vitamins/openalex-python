"""Compact representation of a concept."""
from __future__ import annotations


class DehydratedConcept:
    """Core information about a concept."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        level: int | None = None,
        score: float | None = None,
        wikidata: str | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.level = level
        self.score = score
        self.wikidata = wikidata
