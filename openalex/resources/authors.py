"""Authors resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Author, AuthorsFilter
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class AuthorsResource(BaseResource[Author, AuthorsFilter]):
    """Resource for accessing authors endpoints."""

    endpoint = "authors"
    model_class = Author
    filter_class = AuthorsFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize authors resource."""
        super().__init__(client)

    def by_orcid(self, orcid: str) -> Author:
        """Get author by ORCID.

        Args:
            orcid: ORCID identifier

        Returns:
            Author instance
        """
        # Ensure ORCID is properly formatted
        if not orcid.startswith("https://orcid.org/"):
            orcid = f"https://orcid.org/{orcid}"

        return self.get(orcid)


class AsyncAuthorsResource(AsyncBaseResource[Author, AuthorsFilter]):
    """Async resource for accessing authors endpoints."""

    endpoint = "authors"
    model_class = Author
    filter_class = AuthorsFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async authors resource."""
        super().__init__(client)

    async def by_orcid(self, orcid: str) -> Author:
        """Get author by ORCID.

        Args:
            orcid: ORCID identifier

        Returns:
            Author instance
        """
        # Ensure ORCID is properly formatted
        if not orcid.startswith("https://orcid.org/"):
            orcid = f"https://orcid.org/{orcid}"

        return await self.get(orcid)
