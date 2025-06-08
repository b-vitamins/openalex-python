"""Sources resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Source
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class SourcesResource(BaseResource[Source, BaseFilter]):
    """Resource for accessing sources endpoints."""

    endpoint = "sources"
    model_class = Source
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize sources resource."""
        super().__init__(client)

    def by_issn(self, issn: str) -> Source:
        """Get source by ISSN.

        Args:
            issn: ISSN identifier

        Returns:
            Source instance
        """
        # Clean ISSN format
        issn = issn.replace("-", "").strip()
        return self.get(f"issn:{issn}")


class AsyncSourcesResource(AsyncBaseResource[Source, BaseFilter]):
    """Async resource for accessing sources endpoints."""

    endpoint = "sources"
    model_class = Source
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async sources resource."""
        super().__init__(client)

    async def by_issn(self, issn: str) -> Source:
        """Get source by ISSN.

        Args:
            issn: ISSN identifier

        Returns:
            Source instance
        """
        # Clean ISSN format
        issn = issn.replace("-", "").strip()
        return await self.get(f"issn:{issn}")
