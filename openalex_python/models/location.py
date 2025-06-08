"""Host location for a work."""
from __future__ import annotations

from dataclasses import dataclass

from .dehydrated_source import DehydratedSource


@dataclass(slots=True)
class Location:
    """Details about where a work can be found."""

    is_oa: bool | None = None
    landing_page_url: str | None = None
    pdf_url: str | None = None
    source: DehydratedSource | None = None
    license: str | None = None
    license_id: str | None = None
    version: str | None = None
    is_accepted: bool | None = None
    is_published: bool | None = None
