"""Compact representation of an institution."""
from __future__ import annotations

from collections.abc import Iterable


class DehydratedInstitution:
    """Minimal institution record."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        ror: str | None = None,
        country_code: str | None = None,
        type: str | None = None,
        lineage: Iterable[str] | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.ror = ror
        self.country_code = country_code
        self.type = type
        self.lineage = list(lineage) if lineage is not None else None
