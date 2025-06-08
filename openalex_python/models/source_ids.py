"""Identifier collection for a publication source."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceIds:
    """Identifiers used to reference a source across systems."""

    openalex: str
    issn_l: str | None = None
    issn: list[str] | None = None
    mag: int | None = None
    fatcat: str | None = None
    wikidata: str | None = None

    def __post_init__(self) -> None:
        """Normalize ISSN list."""
        self.issn = list(self.issn) if self.issn is not None else None
