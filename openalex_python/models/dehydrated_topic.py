"""Minimal representation of a topic."""
from __future__ import annotations

from .topic_level import TopicLevel


class DehydratedTopic:
    """Basic topic details."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        score: float | None = None,
        subfield: TopicLevel | None = None,
        field: TopicLevel | None = None,
        domain: TopicLevel | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.score = score
        self.subfield = subfield
        self.field = field
        self.domain = domain
