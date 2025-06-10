"""Works resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from ..constants import DOI_URL_PREFIX, HTTP_METHOD_GET, PMID_PREFIX, Resource
from ..exceptions import raise_for_status
from ..models import ListResult, Work, WorksFilter
from ..utils import ensure_prefix, strip_id_prefix
from ..utils.pagination import MAX_PER_PAGE
from ..utils.params import normalize_params
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncWorksResource", "WorksResource"]

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex
    from ..models.work import Ngram
    from ..utils import AsyncPaginator, Paginator


class WorksResource(BaseResource[Work, WorksFilter]):
    """Resource for accessing works endpoints."""

    endpoint = Resource.WORKS.value
    model_class = Work
    filter_class = WorksFilter

    def __init__(
        self, client: OpenAlex, default_filter: WorksFilter | None = None
    ) -> None:
        """Initialize works resource."""
        super().__init__(client)
        self._default_filter = default_filter

    def by_doi(self, doi: str) -> Work:
        """Retrieve a work by DOI."""

        return self.get(ensure_prefix(doi, DOI_URL_PREFIX))

    def by_pmid(self, pmid: str) -> Work:
        """Retrieve a work by PubMed ID."""

        return self.get(ensure_prefix(str(pmid), PMID_PREFIX))

    def filter(self, **filter_params: Any) -> Self | WorksFilter:
        """Add filter parameters or return a ``WorksFilter`` builder.

        When called without parameters, this behaves like the base ``filter``
        method and returns a :class:`WorksFilter` instance that can be used to
        build complex filter dictionaries.  When called with parameters that are
        not recognised as ``WorksFilter`` fields, it returns a new
        :class:`WorksResource` instance pre-configured with those parameters so
        the calls can be chained, e.g. ``client.works.filter(is_oa=True)``.
        """

        if not filter_params:
            return self.filter_class.model_validate({})

        known_fields = set(self.filter_class.model_fields)
        if set(filter_params).issubset(known_fields):
            return self.filter_class(**filter_params)

        normalized: dict[str, Any] = {}
        for key, value in filter_params.items():
            if (
                isinstance(value, list)
                and value
                and all(isinstance(v, int) for v in value)
            ):
                min_val = min(value)
                max_val = max(value)
                if value == list(range(min_val, max_val + 1)):
                    normalized[key] = f"{min_val}-{max_val}"
                else:
                    normalized[key] = value
            else:
                normalized[key] = value

        return self._clone_with(normalized)

    def _clone_with(self, filter_update: dict[str, Any]) -> Self:
        base_filter = self._default_filter or WorksFilter.model_validate({})
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return self.__class__(self.client, default_filter=new_filter)

    def cited_by(self, work_id: str) -> WorksResource:
        """Get works that cite this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by citations
        """
        work_id = strip_id_prefix(work_id)

        return self._clone_with({"cites": work_id})

    def references(self, work_id: str) -> WorksResource:
        """Get works referenced by this work.

        Args:
            work_id: Work ID
            **params: Additional parameters

        Returns:
            Works resource filtered by references
        """
        work_id = strip_id_prefix(work_id)

        return self._clone_with({"cited_by": work_id})

    def by_author(self, author_id: str) -> WorksResource:
        """Get works by a specific author.

        Args:
            author_id: Author ID
            **params: Additional parameters

        Returns:
            Works resource filtered by author
        """
        author_id = strip_id_prefix(author_id)

        return self._clone_with({"authorships.author.id": author_id})

    def by_concept(self, concept_id: str) -> WorksResource:
        """Filter works associated with a concept."""

        concept_id = strip_id_prefix(concept_id)

        return self._clone_with({"concepts.id": concept_id})

    def by_institution(self, institution_id: str) -> WorksResource:
        """Get works from a specific institution.

        Args:
            institution_id: Institution ID
            **params: Additional parameters

        Returns:
            Works resource filtered by institution
        """
        institution_id = strip_id_prefix(institution_id)

        return self._clone_with({"authorships.institutions.id": institution_id})

    def related_to(self, work_id: str) -> WorksResource:
        """Get works related to a specific work."""

        work_id = strip_id_prefix(work_id)

        return self._clone_with({"related_to": work_id})

    def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001,FBT002
    ) -> WorksResource:
        """Filter works by open access status.

        Args:
            is_oa: Whether to filter for OA works
            **params: Additional parameters

        Returns:
            Works resource filtered by OA status
        """
        return self._clone_with({"is_oa": is_oa})

    def ngrams(self, work_id: str, **params: Any) -> ListResult[Ngram]:
        """Get n-grams for a work."""
        from ..models.work import Ngram

        work_id = strip_id_prefix(work_id)
        url = self._build_url(f"{work_id}/ngrams")
        params = normalize_params(params)

        response = self.client._request(HTTP_METHOD_GET, url, params=params)  # noqa: SLF001
        raise_for_status(response)

        data = response.json()
        results = [Ngram(**item) for item in data.get("ngrams", [])]

        return ListResult[Ngram](meta=data.get("meta", {}), results=results)

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
        per_page: int = MAX_PER_PAGE,
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

    endpoint = Resource.WORKS.value
    model_class = Work
    filter_class = WorksFilter

    def __init__(
        self, client: AsyncOpenAlex, default_filter: WorksFilter | None = None
    ) -> None:
        """Initialize async works resource."""
        super().__init__(client)
        self._default_filter = default_filter

    async def by_doi(self, doi: str) -> Work:
        """Retrieve a work by DOI."""

        return await self.get(ensure_prefix(doi, DOI_URL_PREFIX))

    async def by_pmid(self, pmid: str) -> Work:
        """Retrieve a work by PubMed ID."""

        return await self.get(ensure_prefix(str(pmid), PMID_PREFIX))

    def _clone_with(self, filter_update: dict[str, Any]) -> Self:
        base_filter = self._default_filter or WorksFilter.model_validate({})
        current = base_filter.filter or {}
        if isinstance(current, str):
            current = {"raw": current}
        current.update(filter_update)
        new_filter = base_filter.model_copy(update={"filter": current})
        return self.__class__(self.client, default_filter=new_filter)

    async def cited_by(self, work_id: str) -> AsyncWorksResource:
        """Get works that cite this work."""
        work_id = strip_id_prefix(work_id)

        return self._clone_with({"cites": work_id})

    async def references(self, work_id: str) -> AsyncWorksResource:
        """Get works referenced by this work."""
        work_id = strip_id_prefix(work_id)

        return self._clone_with({"cited_by": work_id})

    async def by_author(self, author_id: str) -> AsyncWorksResource:
        """Get works by a specific author."""
        author_id = strip_id_prefix(author_id)

        return self._clone_with({"authorships.author.id": author_id})

    async def by_concept(self, concept_id: str) -> AsyncWorksResource:
        """Filter works associated with a concept."""

        concept_id = strip_id_prefix(concept_id)

        return self._clone_with({"concepts.id": concept_id})

    async def by_institution(self, institution_id: str) -> AsyncWorksResource:
        """Get works from a specific institution."""
        institution_id = strip_id_prefix(institution_id)

        return self._clone_with({"authorships.institutions.id": institution_id})

    async def related_to(self, work_id: str) -> AsyncWorksResource:
        """Get works related to a specific work."""

        work_id = strip_id_prefix(work_id)

        return self._clone_with({"related_to": work_id})

    async def open_access(
        self,
        is_oa: bool = True,  # noqa: FBT001,FBT002
    ) -> AsyncWorksResource:
        """Filter works by open access status."""
        return self._clone_with({"is_oa": is_oa})

    async def ngrams(self, work_id: str, **params: Any) -> ListResult[Ngram]:
        """Get n-grams for a work asynchronously."""
        from ..models.work import Ngram

        work_id = strip_id_prefix(work_id)
        url = self._build_url(f"{work_id}/ngrams")
        params = normalize_params(params)

        response = await self.client._request(  # noqa: SLF001
            HTTP_METHOD_GET, url, params=params
        )
        raise_for_status(response)

        data = response.json()
        results = [Ngram(**item) for item in data.get("ngrams", [])]

        return ListResult[Ngram](meta=data.get("meta", {}), results=results)

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
        per_page: int = MAX_PER_PAGE,
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
