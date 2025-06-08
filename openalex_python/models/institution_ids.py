"""External identifiers for an institution."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InstitutionIds:
    """Collection of identifier strings."""

    openalex: str
    ror: str | None = None
    grid: str | None = None
    wikipedia: str | None = None
    wikidata: str | None = None
    mag: int | None = None
