"""General API response models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RootResponse:
    """Basic information returned at the API root."""

    documentation_url: str
    msg: str
    version: str
