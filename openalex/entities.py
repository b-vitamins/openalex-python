"""Convenience entity classes for PyAlex-style direct access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from .models import (
    Author,
    AuthorsFilter,
    BaseFilter,
    Concept,
    Funder,
    Institution,
    InstitutionsFilter,
    Keyword,
    Publisher,
    Source,
    Topic,
    Work,
    WorksFilter,
)

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .models import ListResult

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .query import Query
    from .resources.base import AsyncBaseResource, BaseResource
    from .utils import Paginator

from .client import AsyncOpenAlex, OpenAlex

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .config import OpenAlexConfig

T = TypeVar("T")
F = TypeVar("F", bound="BaseFilter")


class BaseEntity(Generic[T, F]):
    """Base class for entity convenience wrappers."""

    resource_name: str = ""

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        """Initialize entity with optional configuration."""
        self._config = config
        self._email = email
        self._api_key = api_key
        self._client: OpenAlex | None = None
        self._async_client: AsyncOpenAlex | None = None

    def __repr__(self) -> str:
        """String representation of entity."""
        config_parts = []
        if self._email:
            config_parts.append(f"email='{self._email}'")
        if self._api_key:
            config_parts.append("api_key='***'")

        config_str = f"({', '.join(config_parts)})" if config_parts else ""
        return f"<{self.__class__.__name__}{config_str}>"

    @property
    def _sync_client(self) -> OpenAlex:
        """Get or create sync client."""
        if self._client is None:
            self._client = OpenAlex(
                config=self._config,
                email=self._email,
                api_key=self._api_key,
            )
        return self._client

    @property
    def _get_async_client(self) -> AsyncOpenAlex:
        """Get or create async client."""
        if self._async_client is None:
            self._async_client = AsyncOpenAlex(
                config=self._config,
                email=self._email,
                api_key=self._api_key,
            )
        return self._async_client

    @property
    def _resource(self) -> BaseResource[T, F]:
        """Get the sync resource."""
        return cast(
            "BaseResource[T, F]", getattr(self._sync_client, self.resource_name)
        )

    @property
    def _async_resource(self) -> AsyncBaseResource[T, F]:
        """Get the async resource."""
        return cast(
            "AsyncBaseResource[T, F]",
            getattr(self._get_async_client, self.resource_name),
        )

    def __getitem__(self, record_id: str | list[str]) -> T | ListResult[T]:
        """Get entity by ID or list of IDs."""
        return self.query()[record_id]

    def query(self) -> Query[T, F]:
        """Create a query builder."""
        return self._resource.query()

    def filter(self, **kwargs: Any) -> Query[T, F]:
        """Create query with filters."""
        return self.query().filter(**kwargs)

    def filter_or(self, **kwargs: Any) -> Query[T, F]:
        """Create query with OR filters."""
        return self.query().filter_or(**kwargs)

    def filter_not(self, **kwargs: Any) -> Query[T, F]:
        """Create query with NOT filters."""
        return self.query().filter_not(**kwargs)

    def filter_gt(self, **kwargs: Any) -> Query[T, F]:
        """Create query with greater than filters."""
        return self.query().filter_gt(**kwargs)

    def filter_lt(self, **kwargs: Any) -> Query[T, F]:
        """Create query with less than filters."""
        return self.query().filter_lt(**kwargs)

    def search(self, query: str) -> Query[T, F]:
        """Create query with search."""
        return self.query().search(query)

    def search_filter(self, **kwargs: Any) -> Query[T, F]:
        """Create query with search filters."""
        return self.query().search_filter(**kwargs)

    def sort(self, **kwargs: str) -> Query[T, F]:
        """Create query with sorting."""
        return self.query().sort(**kwargs)

    def select(self, fields: list[str] | str) -> Query[T, F]:
        """Create query with field selection."""
        return self.query().select(fields)

    def sample(self, n: int, seed: int | None = None) -> Query[T, F]:
        """Create query with sampling."""
        return self.query().sample(n, seed)

    def group_by(self, key: str) -> Query[T, F]:
        """Create query with grouping."""
        return self.query().group_by(key)

    def get(self, id: str | None = None, **params: Any) -> T | ListResult[T]:
        """Get a single entity by ID or list entities."""
        if id is not None:
            return self._resource.get(id, **params)
        return self.query().get(**params)

    def list(self, **params: Any) -> ListResult[T]:
        """List entities."""
        return self.query().list(**params)

    def count(self) -> int:
        """Get count of all entities."""
        return self.query().count()

    def random(self) -> T:
        """Get a random entity."""
        return self._resource.random()

    def autocomplete(self, query: str, **params: Any) -> ListResult[Any]:
        """Autocomplete search."""
        return self._resource.autocomplete(query, **params)

    def paginate(self, **kwargs: Any) -> Paginator[T]:
        """Create paginator."""
        return self.query().paginate(**kwargs)

    async def __aenter__(self) -> BaseEntity[T, F]:
        """Async context manager entry."""
        await self._get_async_client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._async_client:
            await self._async_client.__aexit__(*args)


class Works(BaseEntity[Work, WorksFilter]):
    """Convenience class for Works resource."""

    resource_name = "works"


class Authors(BaseEntity[Author, AuthorsFilter]):
    """Convenience class for Authors resource."""

    resource_name = "authors"


class Institutions(BaseEntity[Institution, InstitutionsFilter]):
    """Convenience class for Institutions resource."""

    resource_name = "institutions"


class Sources(BaseEntity[Source, BaseFilter]):
    """Convenience class for Sources resource."""

    resource_name = "sources"


class Topics(BaseEntity[Topic, BaseFilter]):
    """Convenience class for Topics resource."""

    resource_name = "topics"


class Publishers(BaseEntity[Publisher, BaseFilter]):
    """Convenience class for Publishers resource."""

    resource_name = "publishers"


class Funders(BaseEntity[Funder, BaseFilter]):
    """Convenience class for Funders resource."""

    resource_name = "funders"


class Keywords(BaseEntity[Keyword, BaseFilter]):
    """Convenience class for Keywords resource."""

    resource_name = "keywords"


class Concepts(BaseEntity[Concept, BaseFilter]):
    """Convenience class for Concepts resource (deprecated)."""

    resource_name = "concepts"


People = Authors
Journals = Sources
