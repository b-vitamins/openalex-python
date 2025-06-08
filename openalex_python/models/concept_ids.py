"""External identifiers for a concept."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(slots=True)
class ConceptIds:
    """Different identifier schemes used for a concept."""

    openalex: str
    wikidata: str | None = None
    wikipedia: str | None = None
    umls_cui: Iterable[str] | None = None
    umls_aui: Iterable[str] | None = None
    mag: int | None = None

    def __post_init__(self) -> None:
        """Convert UMLS iterables to lists."""
        if self.umls_cui is not None:
            self.umls_cui = list(self.umls_cui)
        if self.umls_aui is not None:
            self.umls_aui = list(self.umls_aui)

