"""Model for institutions associated with an author."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AssociatedInstitution:
    """Institution linked with an author."""

    id: str
    display_name: str
    relationship: str
    ror: str | None = None
    country_code: str | None = None
    type: str | None = None
