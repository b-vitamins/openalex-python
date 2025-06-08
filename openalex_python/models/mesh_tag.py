"""Medical Subject Heading information for a work."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MeshTag:
    """MeSH descriptor and qualifier."""

    descriptor_ui: str
    descriptor_name: str
    is_major_topic: bool
    qualifier_ui: str | None = None
    qualifier_name: str | None = None
