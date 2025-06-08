"""Hierarchy levels for topics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TopicLevel:
    """Represents one level in the topic hierarchy."""

    id: str
    display_name: str
