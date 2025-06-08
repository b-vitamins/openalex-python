"""Information about a funding grant."""
from __future__ import annotations


class Grant:
    """Funding grant metadata."""

    def __init__(
        self,
        *,
        funder: str,
        funder_display_name: str | None = None,
        award_id: str | None = None,
    ) -> None:
        self.funder = funder
        self.funder_display_name = funder_display_name
        self.award_id = award_id
