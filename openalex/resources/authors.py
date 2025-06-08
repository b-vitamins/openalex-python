"""Authors resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Author, AuthorsFilter, ListResult
from ..utils import AsyncPaginator, Paginator
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class AuthorsResource(BaseResource[Author, AuthorsFilter]):
    """Resource for accessing authors endpoints."""

    endpoint = "authors"
    model_class = Author
    filter_class = AuthorsFilter

    def __init__(
        self, client: OpenAlex, default_filter: AuthorsFilter | None = None
    ) -> None:
        """Initialize authors resource."""
        super().__init__(client)
        self._default_filter = default_filter

    def _clone_with(self, filter_update: dict[str, Any]) -> AuthorsResource:
        base_filter = self._default_filter or AuthorsFilter()  # type: ignore[call-arg]
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return AuthorsResource(self.client, default_filter=new_filter)

    def by_mag(self, mag_id: str) -> Author:
        """Get author by Microsoft Academic Graph ID."""
        if not str(mag_id).startswith("mag:"):
            mag_id = f"mag:{mag_id}"
        return self.get(mag_id)

    def by_institution(self, institution_id: str) -> AuthorsResource:
        """Filter authors by institution."""
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]
        return self._clone_with({"affiliations.institution.id": institution_id})

    def list(
        self, filter: AuthorsFilter | dict[str, Any] | None = None, **params: Any
    ) -> ListResult[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().list(filter=filter, **params)

    def search(
        self,
        query: str,
        filter: AuthorsFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().search(query, filter=filter, **params)

    def paginate(
        self,
        filter: AuthorsFilter | dict[str, Any] | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **params: Any,
    ) -> Paginator[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().paginate(
            filter=filter,
            per_page=per_page,
            max_results=max_results,
            **params,
        )

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

    def __init__(
        self, client: AsyncOpenAlex, default_filter: AuthorsFilter | None = None
    ) -> None:
        """Initialize async authors resource."""
        super().__init__(client)
        self._default_filter = default_filter

    def _clone_with(self, filter_update: dict[str, Any]) -> AsyncAuthorsResource:
        base_filter = self._default_filter or AuthorsFilter()  # type: ignore[call-arg]
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return AsyncAuthorsResource(self.client, default_filter=new_filter)

    async def by_mag(self, mag_id: str) -> Author:
        """Get author by Microsoft Academic Graph ID."""
        if not str(mag_id).startswith("mag:"):
            mag_id = f"mag:{mag_id}"
        return await self.get(mag_id)

    async def by_institution(self, institution_id: str) -> AsyncAuthorsResource:
        """Filter authors by institution."""
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]
        return self._clone_with({"affiliations.institution.id": institution_id})

    async def list(
        self, filter: AuthorsFilter | dict[str, Any] | None = None, **params: Any
    ) -> ListResult[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return await super().list(filter=filter, **params)

    async def search(
        self,
        query: str,
        filter: AuthorsFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return await super().search(query, filter=filter, **params)

    def paginate(
        self,
        filter: AuthorsFilter | dict[str, Any] | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **params: Any,
    ) -> AsyncPaginator[Author]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().paginate(
            filter=filter,
            per_page=per_page,
            max_results=max_results,
            **params,
        )

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
