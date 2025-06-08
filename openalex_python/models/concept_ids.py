"""External identifiers for a concept."""
from __future__ import annotations

from collections.abc import Iterable


class ConceptIds:
    """Different identifier schemes used for a concept."""

    def __init__(
        self,
        *,
        openalex: str,
        wikidata: str | None = None,
        wikipedia: str | None = None,
        umls_cui: Iterable[str] | None = None,
        umls_aui: Iterable[str] | None = None,
        mag: int | None = None,
    ) -> None:
        self.openalex = openalex
        self.wikidata = wikidata
        self.wikipedia = wikipedia
        self.umls_cui = list(umls_cui) if umls_cui is not None else None
        self.umls_aui = list(umls_aui) if umls_aui is not None else None
        self.mag = mag

