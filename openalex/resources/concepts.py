"""Concepts resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import Resource
from ..models import BaseFilter, Concept
from ..utils import ensure_prefix
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncConceptsResource", "ConceptsResource"]

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class ConceptsResource(BaseResource[Concept, BaseFilter]):
    """Resource for accessing concepts endpoints."""

    endpoint = Resource.CONCEPTS.value
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
        if not wikidata_id.startswith("https://"):
            if not wikidata_id.startswith("Q"):
                wikidata_id = f"Q{wikidata_id}"
            wikidata_id = ensure_prefix(
                wikidata_id,
                "https://www.wikidata.org/entity/",
            )

        return self.get(wikidata_id)


class AsyncConceptsResource(AsyncBaseResource[Concept, BaseFilter]):
    """Async resource for accessing concepts endpoints."""

    endpoint = Resource.CONCEPTS.value
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
        if not wikidata_id.startswith("https://"):
            if not wikidata_id.startswith("Q"):
                wikidata_id = f"Q{wikidata_id}"
            wikidata_id = ensure_prefix(
                wikidata_id,
                "https://www.wikidata.org/entity/",
            )

        return await self.get(wikidata_id)
