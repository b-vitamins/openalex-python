"""Title and abstract text for analysis."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextBody:
    """Input text to be analyzed."""

    title: str
    abstract: str | None = None
