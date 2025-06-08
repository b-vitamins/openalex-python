"""Topic model for OpenAlex API."""

from __future__ import annotations

from enum import IntEnum

from pydantic import Field, HttpUrl

from .base import OpenAlexEntity, SummaryStats


class TopicHierarchy(OpenAlexEntity):
    """Represents a node in the topic hierarchy."""

    pass


class TopicLevel(IntEnum):
    """Enumeration of hierarchy levels for a topic."""

    DOMAIN = 0
    FIELD = 1
    SUBFIELD = 2


class TopicIds(OpenAlexEntity):
    """External identifiers for a topic."""

    openalex: str | None = None
    wikipedia: HttpUrl | None = None


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

    sisters: list[DehydratedTopic] = Field(
        default_factory=list, description="Sister topics"
    )

    works_api_url: HttpUrl | None = Field(
        None, description="API URL for topic's works"
    )

    ids: TopicIds | None = None

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
    def level(self) -> TopicLevel | None:
        """Get the topic's hierarchy level."""
        if self.subfield:
            return TopicLevel.SUBFIELD
        if self.field:
            return TopicLevel.FIELD
        if self.domain:
            return TopicLevel.DOMAIN
        return None

    def has_keyword(self, keyword: str) -> bool:
        """Check if topic has a specific keyword."""
        keyword_lower = keyword.lower()
        return any(k.lower() == keyword_lower for k in self.keywords)


from .work import DehydratedTopic  # noqa: E402,TC001

Topic.model_rebuild()
