"""Concepts resource for OpenAlex API."""
# pragma: no cover

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Concept
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class ConceptsResource(BaseResource[Concept, BaseFilter]):
    """Resource for accessing concepts endpoints."""

    endpoint = "concepts"
    model_class = Concept
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize concepts resource."""
        super().__init__(client)

    def by_wikidata(self, wikidata_id: str) -> Concept:
        """Get concept by Wikidata ID.

        Args:
            wikidata_id: Wikidata identifier (e.g., Q123456)

        Returns:
            Concept instance
        """
        # Ensure proper Wikidata URL format
        if not wikidata_id.startswith("https://"):
            if wikidata_id.startswith("Q"):
                wikidata_id = f"https://www.wikidata.org/entity/{wikidata_id}"
            else:
                wikidata_id = f"https://www.wikidata.org/entity/Q{wikidata_id}"

        return self.get(wikidata_id)


class AsyncConceptsResource(AsyncBaseResource[Concept, BaseFilter]):
    """Async resource for accessing concepts endpoints."""

    endpoint = "concepts"
    model_class = Concept
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async concepts resource."""
        super().__init__(client)

    async def by_wikidata(self, wikidata_id: str) -> Concept:
        """Get concept by Wikidata ID.

        Args:
            wikidata_id: Wikidata identifier (e.g., Q123456)

        Returns:
            Concept instance
        """
        # Ensure proper Wikidata URL format
        if not wikidata_id.startswith("https://"):
            if wikidata_id.startswith("Q"):
                wikidata_id = f"https://www.wikidata.org/entity/{wikidata_id}"
            else:
                wikidata_id = f"https://www.wikidata.org/entity/Q{wikidata_id}"

        return await self.get(wikidata_id)
