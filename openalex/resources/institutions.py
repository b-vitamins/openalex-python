"""Institutions resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import ROR_URL_PREFIX, Resource
from ..models import Institution, InstitutionsFilter
from ..utils import ensure_prefix
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncInstitutionsResource", "InstitutionsResource"]

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class InstitutionsResource(BaseResource[Institution, InstitutionsFilter]):
    """Resource for accessing institutions endpoints."""

    endpoint = Resource.INSTITUTIONS.value
    model_class = Institution
    filter_class = InstitutionsFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize institutions resource."""
        super().__init__(client)

    def by_ror(self, ror: str) -> Institution:
        """Get institution by ROR ID.

        Args:
            ror: ROR identifier

        Returns:
            Institution instance
        """
        return self.get(ensure_prefix(ror, ROR_URL_PREFIX))


class AsyncInstitutionsResource(
    AsyncBaseResource[Institution, InstitutionsFilter]
):
    """Async resource for accessing institutions endpoints."""

    endpoint = Resource.INSTITUTIONS.value
    model_class = Institution
    filter_class = InstitutionsFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async institutions resource."""
        super().__init__(client)

    async def by_ror(self, ror: str) -> Institution:
        """Get institution by ROR ID.

        Args:
            ror: ROR identifier

        Returns:
            Institution instance
        """
        return await self.get(ensure_prefix(ror, ROR_URL_PREFIX))
