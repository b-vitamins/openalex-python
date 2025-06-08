"""Role of an entity in relation to a publisher."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Role:
    """Association role with counts."""

    role: str
    id: str
    works_count: int
