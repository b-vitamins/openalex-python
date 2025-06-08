"""External identifiers for a publisher."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PublisherIds:
    """Various ID systems used for a publisher."""

    openalex: str
    ror: str | None = None
    wikidata: str | None = None
