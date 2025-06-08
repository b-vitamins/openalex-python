"""Model representing article processing charge information."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class APC:
    """Information about an article processing charge."""

    value: int
    currency: str
    value_usd: int | None = None
    provenance: str | None = None
