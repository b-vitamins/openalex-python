"""Direct entity access for PyAlex-style interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:  # pragma: no cover
    import builtins
    from collections.abc import AsyncIterator

    from .models.work import Ngram
    from .query import AsyncQuery

from pydantic import ValidationError

__all__ = [
    "AsyncAuthors",
    "AsyncConcepts",
    "AsyncFunders",
    "AsyncInstitutions",
    "AsyncJournals",
    "AsyncKeywords",
    "AsyncPeople",
    "AsyncPublishers",
    "AsyncSources",
    "AsyncTopics",
    "AsyncWorks",
    "Authors",
    "BaseEntity",
    "Concepts",
    "Funders",
    "Institutions",
    "Keywords",
    "Publishers",
    "Sources",
    "Topics",
    "Works",
]

from .api import AsyncBaseAPI, get_connection
from .cache.manager import get_cache_manager
from .constants import (
    AUTOCOMPLETE_PATH,
    HTTP_METHOD_GET,
    PARAM_Q,
    RANDOM_PATH,
)
from .exceptions import raise_for_status
from .models import (
    Author,
    AutocompleteResult,
    BaseFilter,
    Concept,
    Funder,
    Institution,
    Keyword,
    ListResult,
    Publisher,
    Source,
    Topic,
    Work,
)
from .query import Query
from .utils import Paginator, strip_id_prefix
from .utils.params import normalize_params

if TYPE_CHECKING:  # pragma: no cover
    from .config import OpenAlexConfig
    from .query import AsyncQuery

T = TypeVar("T")
F = TypeVar("F", bound="BaseFilter")


class BaseEntity(Generic[T, F]):
    """Base class for entity direct access."""

    __slots__ = ("_config", "_connection")

    endpoint: str = ""
    model_class: type[T] = None  # type: ignore

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        from .config import OpenAlexConfig

        if config is None:
            config = OpenAlexConfig()
        if email is not None:
            config = config.model_copy(update={"email": email})
        if api_key is not None:
            config = config.model_copy(update={"api_key": api_key})

        self._config = config
        self._connection = get_connection(config)

    @property
    def config(self) -> OpenAlexConfig:
        """Return configuration for this entity."""
        return self._config

    def __repr__(self) -> str:
        config_parts = []
        if self._config.email:
            config_parts.append(f"email='{self._config.email}'")
        if self._config.api_key:
            config_parts.append("api_key='***'")
        cfg = f"({', '.join(config_parts)})" if config_parts else ""
        return f"<{self.__class__.__name__}{cfg}>"

    def _build_url(self, path: str = "") -> str:
        base = f"{self._connection.base_url}/{self.endpoint}"
        if path:
            return f"{base}/{path.lstrip('/')}"
        return base

    def _parse_response(self, data: dict[str, Any]) -> T:
        try:
            return self.model_class(**data)
        except ValidationError:
            return self.model_class.model_construct(**data)  # type: ignore

    def _parse_list_response(self, data: dict[str, Any]) -> ListResult[T]:
        results = [self._parse_response(it) for it in data.get("results", [])]
        try:
            return ListResult[T](
                meta=data.get("meta", {}),
                results=results,
                group_by=data.get("group_by"),
            )
        except ValidationError:
            return ListResult[T].model_construct(
                meta=data.get("meta", {}),
                results=results,
                group_by=data.get("group_by"),
            )

    def query(self, **filter_params: Any) -> Query[T, F]:
        from .query import Query

        params: dict[str, Any] = {}
        if filter_params:
            params["filter"] = filter_params
        return Query(self, params)

    def __getitem__(self, record_id: str | list[str]) -> T | ListResult[T]:
        return self.query()[record_id]

    def _get_single_entity(
        self, entity_id: str, params: dict[str, Any] | None = None
    ) -> T:
        cache_manager = get_cache_manager(self._config)
        entity_id = strip_id_prefix(entity_id)

        def fetch() -> dict[str, Any]:
            url = self._build_url(entity_id)
            norm_params = normalize_params(params or {})
            response = self._connection.request(
                HTTP_METHOD_GET, url, params=norm_params
            )
            raise_for_status(response)
            return cast("dict[str, Any]", response.json())

        data = cache_manager.get_or_fetch(
            endpoint=self.endpoint,
            fetch_func=fetch,
            entity_id=entity_id,
            params=params,
        )
        return self._parse_response(data)

    def get(self, id: str | None = None, **params: Any) -> T | ListResult[T]:
        if id is not None:
            return self._get_single_entity(id, params)
        return self.query().get(**params)

    def list(
        self, filter: dict[str, Any] | None = None, **params: Any
    ) -> ListResult[T]:
        if filter:
            params["filter"] = filter
        params = normalize_params(params)
        url = self._build_url()
        response = self._connection.request(HTTP_METHOD_GET, url, params=params)
        raise_for_status(response)
        return self._parse_list_response(response.json())

    def search(
        self, query: str, filter: dict[str, Any] | None = None, **params: Any
    ) -> Query[T, F]:
        """Return a :class:`Query` with a search term applied."""
        q = self.query()
        if filter:
            q = q.filter(**filter)
        q = q.search(query)
        if params:
            # create a new query with any additional parameters
            q = Query(q.entity, {**q.params, **params})
        return q

    def random(self, **params: Any) -> T:
        url = self._build_url(RANDOM_PATH)
        params = normalize_params(params)
        response = self._connection.request(HTTP_METHOD_GET, url, params=params)
        raise_for_status(response)
        return self._parse_response(response.json())

    def autocomplete(self, query: str, **params: Any) -> ListResult[AutocompleteResult]:
        """Return autocomplete suggestions for this entity."""
        # The autocomplete endpoint follows ``/{entity}/autocomplete``
        url = self._build_url(f"{AUTOCOMPLETE_PATH}")
        params_norm = normalize_params(params)
        params_norm[PARAM_Q] = query
        response = self._connection.request(HTTP_METHOD_GET, url, params=params_norm)
        raise_for_status(response)
        data = response.json()
        results = [AutocompleteResult(**item) for item in data.get("results", [])]
        try:
            return ListResult[AutocompleteResult](
                meta=data.get("meta", {}),
                results=results,
            )
        except ValidationError:
            return ListResult[AutocompleteResult].model_construct(
                meta=data.get("meta", {}),
                results=results,
            )

    def paginate(
        self, filter: dict[str, Any] | None = None, **kwargs: Any
    ) -> Paginator[T]:
        if filter:
            kwargs["filter"] = filter

        def fetch_page(page_params: dict[str, Any]) -> ListResult[T]:
            all_params = {**kwargs, **page_params}
            return self.list(**all_params)

        return Paginator(
            fetch_func=fetch_page,
            params=kwargs,
            per_page=kwargs.get("per_page", 25),
            max_results=kwargs.get("max_results"),
        )

    def filter(self, **kwargs: Any) -> Query[T, F]:
        return self.query().filter(**kwargs)

    def filter_or(self, **kwargs: Any) -> Query[T, F]:
        return self.query().filter_or(**kwargs)

    def filter_not(self, **kwargs: Any) -> Query[T, F]:
        return self.query().filter_not(**kwargs)

    def filter_gt(self, **kwargs: Any) -> Query[T, F]:
        return self.query().filter_gt(**kwargs)

    def filter_lt(self, **kwargs: Any) -> Query[T, F]:
        return self.query().filter_lt(**kwargs)

    def search_filter(self, **kwargs: Any) -> Query[T, F]:
        return self.query().search_filter(**kwargs)

    def sort(self, **kwargs: str) -> Query[T, F]:
        return self.query().sort(**kwargs)

    def select(self, fields: builtins.list[str] | str) -> Query[T, F]:
        return self.query().select(fields)

    def sample(self, n: int, seed: int | None = None) -> Query[T, F]:
        return self.query().sample(n, seed)

    def group_by(self, key: str) -> Query[T, F]:
        return self.query().group_by(key)

    def count(self) -> int:
        return self.query().count()

    def clear_cache(self) -> None:
        """Clear cache for this entity type."""
        cache_manager = get_cache_manager(self._config)
        cache_manager.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for this entity type."""
        cache_manager = get_cache_manager(self._config)
        return cache_manager.stats()


class AsyncBaseEntity(AsyncBaseAPI[T], Generic[T, F]):
    """Base class for async entity access."""

    __slots__ = ("_config",)

    model_class: type[T]

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        from .config import OpenAlexConfig

        if config is None:
            config = OpenAlexConfig()
        if email is not None:
            config = config.model_copy(update={"email": email})
        if api_key is not None:
            config = config.model_copy(update={"api_key": api_key})

        super().__init__(config)

    async def get(self, entity_id: str) -> T:
        data = await self.get_single_entity(entity_id)
        return self.model_class(**data)

    def filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        from .query import AsyncQuery

        return AsyncQuery(
            entity=self,
            model_class=self.model_class,
            config=self._config,
        ).filter(**kwargs)

    def search(self, query: str) -> AsyncQuery[T, F]:
        return self.filter(search=query)

    def search_filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        from .query import AsyncQuery

        return AsyncQuery(
            entity=self,
            model_class=self.model_class,
            config=self._config,
        ).search_filter(**kwargs)

    async def all(self) -> AsyncIterator[T]:
        page = 1
        while True:
            data = await self.get_list(params={"page": page})
            results = ListResult[T](
                meta=data.get("meta", {}),
                results=[
                    self.model_class(**item) for item in data.get("results", [])
                ],
            )

            for item in results.results:
                yield item

            if len(results.results) == 0:
                break

            page += 1

    async def random(self) -> T:  # type: ignore[override]
        data = await super().random()
        return self.model_class(**data)

    async def autocomplete(  # type: ignore[override]
        self,
        query: str,
        params: dict[str, Any] | None = None,
    ) -> ListResult[AutocompleteResult]:
        data = await super().autocomplete(query, params)
        return ListResult[AutocompleteResult](
            meta=data.get("meta", {}),
            results=[
                AutocompleteResult(**item) for item in data.get("results", [])
            ],
        )

    def clear_cache(self) -> None:
        from .cache.manager import get_cache_manager

        cache_manager = get_cache_manager(self._config)
        cache_manager.clear()

    def cache_stats(self) -> dict[str, Any]:
        from .cache.manager import get_cache_manager

        cache_manager = get_cache_manager(self._config)
        return cache_manager.stats()


class Works(BaseEntity[Work, BaseFilter]):
    endpoint = "works"
    model_class = Work
    __slots__ = ()

    def ngrams(self, work_id: str, **params: Any) -> ListResult[Any]:
        """Return ngram statistics for a given work."""
        from .models.work import Ngram

        work_id = strip_id_prefix(work_id)
        url = self._build_url(f"{work_id}/ngrams")
        params = normalize_params(params)
        response = self._connection.request(HTTP_METHOD_GET, url, params=params)
        raise_for_status(response)
        data = response.json()
        results = [Ngram(**item) for item in data.get("ngrams", [])]
        return ListResult[Ngram](meta=data.get("meta", {}), results=results)


class Authors(BaseEntity[Author, BaseFilter]):
    endpoint = "authors"
    model_class = Author
    __slots__ = ()


class Institutions(BaseEntity[Institution, BaseFilter]):
    endpoint = "institutions"
    model_class = Institution
    __slots__ = ()


class Sources(BaseEntity[Source, BaseFilter]):
    endpoint = "sources"
    model_class = Source
    __slots__ = ()


class Topics(BaseEntity[Topic, BaseFilter]):
    endpoint = "topics"
    model_class = Topic
    __slots__ = ()


class Publishers(BaseEntity[Publisher, BaseFilter]):
    endpoint = "publishers"
    model_class = Publisher
    __slots__ = ()


class Funders(BaseEntity[Funder, BaseFilter]):
    endpoint = "funders"
    model_class = Funder
    __slots__ = ()


class Keywords(BaseEntity[Keyword, BaseFilter]):
    endpoint = "keywords"
    model_class = Keyword
    __slots__ = ()


class Concepts(BaseEntity[Concept, BaseFilter]):
    endpoint = "concepts"
    model_class = Concept
    __slots__ = ()


People = Authors
Journals = Sources


# Async entity classes
class AsyncWorks(AsyncBaseEntity[Work, BaseFilter]):
    """Async Works entity."""

    endpoint = "works"
    model_class = Work
    __slots__ = ()

    async def ngrams(
        self,
        work_id: str,
        params: dict[str, Any] | None = None,
    ) -> ListResult[Ngram]:
        from .models.work import Ngram

        work_id = strip_id_prefix(work_id)
        endpoint = f"{self.endpoint}/{work_id}/ngrams"
        connection = await self._get_connection()
        url = self._build_url(endpoint)
        params_norm = normalize_params(params or {})
        response = await connection.request(
            HTTP_METHOD_GET, url, params=params_norm
        )
        raise_for_status(response)
        data = response.json()
        return ListResult[Ngram](
            meta=data.get("meta", {}),
            results=[Ngram(**item) for item in data.get("ngrams", [])],
        )


class AsyncAuthors(AsyncBaseEntity[Author, BaseFilter]):
    """Async Authors entity."""

    endpoint = "authors"
    model_class = Author
    __slots__ = ()


class AsyncInstitutions(AsyncBaseEntity[Institution, BaseFilter]):
    """Async Institutions entity."""

    endpoint = "institutions"
    model_class = Institution
    __slots__ = ()


class AsyncSources(AsyncBaseEntity[Source, BaseFilter]):
    """Async Sources entity."""

    endpoint = "sources"
    model_class = Source
    __slots__ = ()


class AsyncTopics(AsyncBaseEntity[Topic, BaseFilter]):
    """Async Topics entity."""

    endpoint = "topics"
    model_class = Topic
    __slots__ = ()


class AsyncPublishers(AsyncBaseEntity[Publisher, BaseFilter]):
    """Async Publishers entity."""

    endpoint = "publishers"
    model_class = Publisher
    __slots__ = ()


class AsyncFunders(AsyncBaseEntity[Funder, BaseFilter]):
    """Async Funders entity."""

    endpoint = "funders"
    model_class = Funder
    __slots__ = ()


class AsyncKeywords(AsyncBaseEntity[Keyword, BaseFilter]):
    """Async Keywords entity."""

    endpoint = "keywords"
    model_class = Keyword
    __slots__ = ()


class AsyncConcepts(AsyncBaseEntity[Concept, BaseFilter]):
    """Async Concepts entity."""

    endpoint = "concepts"
    model_class = Concept
    __slots__ = ()


# Async aliases
AsyncPeople = AsyncAuthors
AsyncJournals = AsyncSources
