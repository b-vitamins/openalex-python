"""Funders resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Funder
from ..utils import ensure_prefix
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncFundersResource", "FundersResource"]

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
        return self.get(ensure_prefix(ror, "https://ror.org/"))


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
        return await self.get(ensure_prefix(ror, "https://ror.org/"))
