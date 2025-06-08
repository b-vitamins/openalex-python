"""Topic model for OpenAlex API."""

from __future__ import annotations

from pydantic import Field, HttpUrl

from .base import OpenAlexEntity


class TopicLevel(OpenAlexEntity):
    """Topic hierarchy level (domain, field, subfield)."""

    pass


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

    subfield: TopicLevel | None = Field(
        None, description="Subfield level in hierarchy"
    )

    field: TopicLevel | None = Field(
        None, description="Field level in hierarchy"
    )

    domain: TopicLevel | None = Field(
        None, description="Domain level in hierarchy"
    )

    works_count: int = Field(0, description="Number of works")
    cited_by_count: int = Field(0, description="Total citations")

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
    def level(self) -> int:
        """Get hierarchy level (0=domain, 1=field, 2=subfield)."""
        if self.subfield:
            return 2
        if self.field:
            return 1
        if self.domain:
            return 0
        return -1

    def has_keyword(self, keyword: str) -> bool:
        """Check if topic has a specific keyword."""
        keyword_lower = keyword.lower()
        return any(k.lower() == keyword_lower for k in self.keywords)
