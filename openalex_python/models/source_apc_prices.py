"""APC pricing information for a source."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceApcPrices:
    """APC price in a specific currency."""

    price: int | None = None
    currency: str | None = None
