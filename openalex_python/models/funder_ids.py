"""External identifiers for a funder."""
from __future__ import annotations


class FunderIds:
    """Different identifier schemes used for a funder."""

    def __init__(
        self,
        *,
        openalex: str,
        ror: str | None = None,
        wikidata: str | None = None,
        crossref: str | None = None,
        doi: str | None = None,
    ) -> None:
        self.openalex = openalex
        self.ror = ror
        self.wikidata = wikidata
        self.crossref = crossref
        self.doi = doi
