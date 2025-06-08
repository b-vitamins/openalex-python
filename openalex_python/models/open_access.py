"""Open access information for a work."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpenAccess:
    """Details about a work's OA status."""

    is_oa: bool
    oa_status: str
    oa_url: str | None = None
    any_repository_has_fulltext: bool | None = None
