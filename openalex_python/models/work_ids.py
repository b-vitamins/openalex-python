"""External identifiers for a work."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkIds:
    """Various IDs referencing a work."""

    openalex: str
    doi: str | None = None
    mag: int | None = None
    pmid: str | None = None
    pmcid: str | None = None
