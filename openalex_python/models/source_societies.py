"""Professional societies associated with a source."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceSocieties:
    """Organization membership for a source."""

    url: str | None = None
    organization: str | None = None
