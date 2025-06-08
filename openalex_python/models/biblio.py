"""Bibliographic information about a work."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Biblio:
    """Container for bibliographic fields."""

    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None

