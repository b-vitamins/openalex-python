"""Affiliation details for an authorship record."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
@dataclass(slots=True)
    """Stores raw affiliation string and related institution IDs."""

    raw_affiliation_string: str | None = None
    institution_ids: Iterable[str] | None = None

    def __post_init__(self) -> None:
        """Normalize the institution ID list."""
        if self.institution_ids:
            self.institution_ids = list(self.institution_ids)
        else:
            self.institution_ids = []
