"""Sources resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Source
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncSourcesResource", "SourcesResource"]

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
        # Normalise ISSN by stripping surrounding whitespace only.  The API
        # accepts ISSNs with the hyphen so keep the original formatting to
        # match expectations in tests and mock URLs.
        issn = issn.strip()
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
        # As with the synchronous variant keep the ISSN formatting intact so
        # that mocked URLs match exactly.
        issn = issn.strip()
        return await self.get(f"issn:{issn}")
