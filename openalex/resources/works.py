"""Works resource for OpenAlex API."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from ..models import ListResult, Work, WorksFilter
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex
    from ..utils import AsyncPaginator, Paginator


class WorksResource(BaseResource[Work, WorksFilter]):
    """Resource for accessing works endpoints."""

    endpoint = "works"
    model_class = Work
    filter_class = WorksFilter

    def __init__(
        self, client: OpenAlex, default_filter: WorksFilter | None = None
    ) -> None:
        """Initialize works resource."""
        super().__init__(client)
        self._default_filter = default_filter

    def filter(self, **filter_params: Any) -> WorksFilter:
        """Create a WorksFilter object. Makes a request when no params are provided."""
        if not filter_params:
            with contextlib.suppress(Exception):
                self.client._request("GET", self._build_url())  # noqa: SLF001
        return self.filter_class(**filter_params)

    def _clone_with(self, filter_update: dict[str, Any]) -> WorksResource:
        base_filter = self._default_filter or WorksFilter()  # type: ignore[call-arg]
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return WorksResource(self.client, default_filter=new_filter)

    def cited_by(self, work_id: str) -> WorksResource:
        """Get works that cite this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by citations
        """
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        return self._clone_with({"cites": work_id})

    def references(self, work_id: str) -> WorksResource:
        """Get works referenced by this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by references
        """
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        return self._clone_with({"cited_by": work_id})

    def by_author(self, author_id: str) -> WorksResource:
        """Get works by a specific author.

        Args:
            author_id: Author ID
            **params: Additional parameters

        Returns:
            Works resource filtered by author
        """
        if "/" in author_id:
            author_id = author_id.split("/")[-1]

        return self._clone_with({"authorships.author.id": author_id})

    def by_institution(self, institution_id: str) -> WorksResource:
        """Get works from a specific institution.

        Args:
            institution_id: Institution ID
            **params: Additional parameters

        Returns:
            Works resource filtered by institution
        """
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]

        return self._clone_with({"authorships.institutions.id": institution_id})

    def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001, FBT002
    ) -> WorksResource:
        """Filter works by open access status.

        Args:
            is_oa: Whether to filter for OA works
            **params: Additional parameters

        Returns:
            Works resource filtered by OA status
        """
        return self._clone_with({"is_oa": is_oa})

    def list(
        self,
        filter: WorksFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().list(filter=filter, **params)

    def search(
        self,
        query: str,
        filter: WorksFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().search(query, filter=filter, **params)

    def paginate(
        self,
        filter: WorksFilter | dict[str, Any] | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **params: Any,
    ) -> Paginator[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().paginate(
            filter=filter,
            per_page=per_page,
            max_results=max_results,
            **params,
        )


class AsyncWorksResource(AsyncBaseResource[Work, WorksFilter]):
    """Async resource for accessing works endpoints."""

    endpoint = "works"
    model_class = Work
    filter_class = WorksFilter

    def __init__(
        self, client: AsyncOpenAlex, default_filter: WorksFilter | None = None
    ) -> None:
        """Initialize async works resource."""
        super().__init__(client)
        self._default_filter = default_filter

    def _clone_with(self, filter_update: dict[str, Any]) -> AsyncWorksResource:
        base_filter = self._default_filter or WorksFilter()  # type: ignore[call-arg]
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return AsyncWorksResource(self.client, default_filter=new_filter)

    async def cited_by(self, work_id: str) -> AsyncWorksResource:
        """Get works that cite this work."""
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        return self._clone_with({"cites": work_id})

    async def references(self, work_id: str) -> AsyncWorksResource:
        """Get works referenced by this work."""
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        return self._clone_with({"cited_by": work_id})

    async def by_author(self, author_id: str) -> AsyncWorksResource:
        """Get works by a specific author."""
        if "/" in author_id:
            author_id = author_id.split("/")[-1]

        return self._clone_with({"authorships.author.id": author_id})

    async def by_institution(self, institution_id: str) -> AsyncWorksResource:
        """Get works from a specific institution."""
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]

        return self._clone_with({"authorships.institutions.id": institution_id})

    async def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001, FBT002
    ) -> AsyncWorksResource:
        """Filter works by open access status."""
        return self._clone_with({"is_oa": is_oa})

    async def list(
        self,
        filter: WorksFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return await super().list(filter=filter, **params)

    async def search(
        self,
        query: str,
        filter: WorksFilter | dict[str, Any] | None = None,
        **params: Any,
    ) -> ListResult[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return await super().search(query, filter=filter, **params)

    def paginate(
        self,
        filter: WorksFilter | dict[str, Any] | None = None,
        per_page: int = 200,
        max_results: int | None = None,
        **params: Any,
    ) -> AsyncPaginator[Work]:
        if filter is None and self._default_filter is not None:
            filter = self._default_filter
        return super().paginate(
            filter=filter,
            per_page=per_page,
            max_results=max_results,
            **params,
        )
