"""Topic model for OpenAlex API."""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import IntEnum
from typing import TYPE_CHECKING, cast

__all__ = ["Topic", "TopicHierarchy", "TopicIds", "TopicLevel"]

from dateutil import parser  # type: ignore
from pydantic import Field, field_validator, model_validator

from ..constants import MAX_SECONDS_IN_MINUTE

if TYPE_CHECKING:
    from .work import DehydratedTopic
from .base import OpenAlexBase, OpenAlexEntity, SummaryStats

MALFORMED_DATETIME_REGEX = re.compile(
    r"(?P<prefix>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}):(?P<sec>\d{2})(?P<rest>.*)"
)


class TopicHierarchy(OpenAlexEntity):
    """Represents a node in the topic hierarchy."""


class TopicLevel(IntEnum):
    """Enumeration of hierarchy levels for a topic."""

    DOMAIN = 0
    FIELD = 1
    SUBFIELD = 2


class TopicIds(OpenAlexBase):
    """External identifiers for a topic."""

    openalex: str | None = None
    wikipedia: str | None = None


class Topic(OpenAlexEntity):
    """Full topic model."""

    description: str | None = None

    keywords: list[str] = Field(
        default_factory=list, description="Keywords associated with the topic"
    )

    subfield: TopicHierarchy | None = Field(
        None, description="Subfield level in hierarchy"
    )

    field: TopicHierarchy | None = Field(
        None, description="Field level in hierarchy"
    )

    domain: TopicHierarchy | None = Field(
        None, description="Domain level in hierarchy"
    )

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

    summary_stats: SummaryStats | None = None

    siblings: list[DehydratedTopic] = Field(
        default_factory=list,
        description="Sibling topics",
        alias="sisters",
    )

    # Pydantic will populate ``siblings`` from the ``sisters`` key when
    # deserialising, but attribute access via ``topic.sisters`` would
    # normally fail.  Expose a read-only alias property for convenience so
    # that ``topic.sisters`` mirrors the underlying ``siblings`` field.
    @property
    def sisters(self) -> list[DehydratedTopic]:
        return self.siblings

    works_api_url: str | None = Field(
        None, description="API URL for topic's works"
    )

    ids: TopicIds | None = None

    @field_validator("updated_date", mode="before")
    @classmethod
    def parse_updated_date(cls, v: datetime | str | None) -> date | None:
        """Parse potentially malformed datetime strings."""
        if v is None:
            return None
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()

        try:
            return datetime.fromisoformat(v).date()
        except ValueError:
            try:
                return cast("datetime", parser.parse(v)).date()
            except (ValueError, TypeError):
                match = MALFORMED_DATETIME_REGEX.match(v)
                if match:
                    sec = int(match.group("sec"))
                    sec = min(sec, MAX_SECONDS_IN_MINUTE)
                    new_v = f"{match.group('prefix')}:{sec:02d}{match.group('rest')}"
                    try:
                        return datetime.fromisoformat(new_v).date()
                    except ValueError:
                        return cast("datetime", parser.parse(new_v)).date()

        return None

    @model_validator(mode="after")
    def validate_hierarchy(self) -> Topic:
        """Ensure subfield is not provided without a field."""
        if self.subfield is not None and self.field is None:
            msg = "subfield provided without field"
            raise ValueError(msg)
        return self

    @property
    def hierarchy_path(self) -> str:
        """Get full hierarchy path."""
        parts = []

        if self.domain and self.domain.display_name:
            parts.append(self.domain.display_name)
        if self.field and self.field.display_name:
            parts.append(self.field.display_name)
        if self.subfield and self.subfield.display_name:
            parts.append(self.subfield.display_name)

        return " > ".join(parts) if parts else ""

    @property
    def level(self) -> TopicLevel:
        """Get the topic's hierarchy level."""
        if self.subfield:
            return TopicLevel.SUBFIELD
        if self.field:
            return TopicLevel.FIELD
        return TopicLevel.DOMAIN

    def has_keyword(self, keyword: str) -> bool:
        """Check if topic has a specific keyword."""
        keyword_lower = keyword.lower()
        return any(keyword_lower in k.lower() for k in self.keywords)

    def get_hierarchy(self) -> dict[str, str | None]:
        """Return hierarchy display names."""
        return {
            "domain": self.domain.display_name if self.domain else None,
            "field": self.field.display_name if self.field else None,
            "subfield": self.subfield.display_name if self.subfield else None,
        }


from .work import DehydratedTopic  # noqa: E402,TC001

Topic.model_rebuild()
