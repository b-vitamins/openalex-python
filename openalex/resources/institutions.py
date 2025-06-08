"""Institutions resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Institution, InstitutionsFilter
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class InstitutionsResource(BaseResource[Institution, InstitutionsFilter]):
    """Resource for accessing institutions endpoints."""

    endpoint = "institutions"
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
        # Ensure ROR is properly formatted
        if not ror.startswith("https://ror.org/"):
            ror = f"https://ror.org/{ror}"

        return self.get(ror)


class AsyncInstitutionsResource(
    AsyncBaseResource[Institution, InstitutionsFilter]
):
    """Async resource for accessing institutions endpoints."""

    endpoint = "institutions"
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
        # Ensure ROR is properly formatted
        if not ror.startswith("https://ror.org/"):
            ror = f"https://ror.org/{ror}"

        return await self.get(ror)
