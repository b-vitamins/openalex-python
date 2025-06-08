"""Localized display names."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InternationalNames:
    """Display names keyed by language code."""

    display_name: dict[str, str] | None = None
