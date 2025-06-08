"""A repository hosting works."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Repository:
    """Institutional or subject repository details."""

    id: str | None = None
    display_name: str | None = None
    host_organization: str | None = None
    host_organization_name: str | None = None
    host_organization_lineage: list[str] | None = None

    def __post_init__(self) -> None:
        """Ensure lineage is a list."""
        self.host_organization_lineage = (
            list(self.host_organization_lineage)
            if self.host_organization_lineage is not None
            else None
        )
