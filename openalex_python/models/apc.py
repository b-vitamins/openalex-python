"""Model representing article processing charge information."""
from __future__ import annotations


class APC:
    """Information about an article processing charge."""

    def __init__(
        self,
        *,
        value: int,
        currency: str,
        value_usd: int | None = None,
        provenance: str | None = None,
    ) -> None:
        self.value = value
        self.currency = currency
        self.value_usd = value_usd
        self.provenance = provenance

