"""Works resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Work, WorksFilter
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class WorksResource(BaseResource[Work, WorksFilter]):
    """Resource for accessing works endpoints."""

    endpoint = "works"
    model_class = Work
    filter_class = WorksFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize works resource."""
        super().__init__(client)

    def cited_by(
        self, work_id: str, **params: Any
    ) -> BaseResource[Work, WorksFilter]:
        """Get works that cite this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by citations
        """
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["cites"] = work_id
        else:
            filter_params = {"cites": work_id}

        params["filter"] = filter_params
        return self

    def references(
        self, work_id: str, **params: Any
    ) -> BaseResource[Work, WorksFilter]:
        """Get works referenced by this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by references
        """
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["cited_by"] = work_id
        else:
            filter_params = {"cited_by": work_id}

        params["filter"] = filter_params
        return self

    def by_author(
        self, author_id: str, **params: Any
    ) -> BaseResource[Work, WorksFilter]:
        """Get works by a specific author.

        Args:
            author_id: Author ID
            **params: Additional parameters

        Returns:
            Works resource filtered by author
        """
        if "/" in author_id:
            author_id = author_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["authorships.author.id"] = author_id
        else:
            filter_params = {"authorships.author.id": author_id}

        params["filter"] = filter_params
        return self

    def by_institution(
        self, institution_id: str, **params: Any
    ) -> BaseResource[Work, WorksFilter]:
        """Get works from a specific institution.

        Args:
            institution_id: Institution ID
            **params: Additional parameters

        Returns:
            Works resource filtered by institution
        """
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["authorships.institutions.id"] = institution_id
        else:
            filter_params = {"authorships.institutions.id": institution_id}

        params["filter"] = filter_params
        return self

    def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001, FBT002
        **params: Any,
    ) -> BaseResource[Work, WorksFilter]:
        """Filter works by open access status.

        Args:
            is_oa: Whether to filter for OA works
            **params: Additional parameters

        Returns:
            Works resource filtered by OA status
        """
        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["is_oa"] = is_oa
        else:
            filter_params = {"is_oa": is_oa}

        params["filter"] = filter_params
        return self


class AsyncWorksResource(AsyncBaseResource[Work, WorksFilter]):
    """Async resource for accessing works endpoints."""

    endpoint = "works"
    model_class = Work
    filter_class = WorksFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async works resource."""
        super().__init__(client)

    async def cited_by(
        self, work_id: str, **params: Any
    ) -> AsyncBaseResource[Work, WorksFilter]:
        """Get works that cite this work."""
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["cites"] = work_id
        else:
            filter_params = {"cites": work_id}

        params["filter"] = filter_params
        return self

    async def references(
        self, work_id: str, **params: Any
    ) -> AsyncBaseResource[Work, WorksFilter]:
        """Get works referenced by this work."""
        if "/" in work_id:
            work_id = work_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["cited_by"] = work_id
        else:
            filter_params = {"cited_by": work_id}

        params["filter"] = filter_params
        return self

    async def by_author(
        self, author_id: str, **params: Any
    ) -> AsyncBaseResource[Work, WorksFilter]:
        """Get works by a specific author."""
        if "/" in author_id:
            author_id = author_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["authorships.author.id"] = author_id
        else:
            filter_params = {"authorships.author.id": author_id}

        params["filter"] = filter_params
        return self

    async def by_institution(
        self, institution_id: str, **params: Any
    ) -> AsyncBaseResource[Work, WorksFilter]:
        """Get works from a specific institution."""
        if "/" in institution_id:
            institution_id = institution_id.split("/")[-1]

        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["authorships.institutions.id"] = institution_id
        else:
            filter_params = {"authorships.institutions.id": institution_id}

        params["filter"] = filter_params
        return self

    async def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001, FBT002
        **params: Any,
    ) -> AsyncBaseResource[Work, WorksFilter]:
        """Filter works by open access status."""
        filter_params = params.get("filter", {})
        if isinstance(filter_params, dict):
            filter_params["is_oa"] = is_oa
        else:
            filter_params = {"is_oa": is_oa}

        params["filter"] = filter_params
        return self
