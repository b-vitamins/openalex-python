"""Funders resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Funder
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class FundersResource(BaseResource[Funder, BaseFilter]):
    """Resource for accessing funders endpoints."""

    endpoint = "funders"
    model_class = Funder
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize funders resource."""
        super().__init__(client)

    def by_ror(self, ror: str) -> Funder:
        """Get funder by ROR ID.

        Args:
            ror: ROR identifier

        Returns:
            Funder instance
        """
        # Ensure ROR is properly formatted
        if not ror.startswith("https://ror.org/"):
            ror = f"https://ror.org/{ror}"

        return self.get(ror)


class AsyncFundersResource(AsyncBaseResource[Funder, BaseFilter]):
    """Async resource for accessing funders endpoints."""

    endpoint = "funders"
    model_class = Funder
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async funders resource."""
        super().__init__(client)

    async def by_ror(self, ror: str) -> Funder:
        """Get funder by ROR ID.

        Args:
            ror: ROR identifier

        Returns:
            Funder instance
        """
        # Ensure ROR is properly formatted
        if not ror.startswith("https://ror.org/"):
            ror = f"https://ror.org/{ror}"

        return await self.get(ror)
