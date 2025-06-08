"""External identifiers for a topic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TopicIds:
    """Various IDs associated with a topic."""

    openalex: str
    wikipedia: str | None = None
