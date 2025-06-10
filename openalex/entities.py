"""Direct entity access for PyAlex-style interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    import builtins

from pydantic import ValidationError

__all__ = [
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

from .api import get_connection
from .constants import (
    AUTOCOMPLETE_PATH,
    HTTP_METHOD_GET,
    OPENALEX_ID_PREFIX,
    PARAM_Q,
    RANDOM_PATH,
)
from .exceptions import raise_for_status
from .models import (
    Author,
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
from .utils import Paginator, strip_id_prefix
from .utils.params import normalize_params

if TYPE_CHECKING:  # pragma: no cover
    from .config import OpenAlexConfig
    from .query import Query

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
        return ListResult[T](
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

    def get(self, id: str | None = None, **params: Any) -> T | ListResult[T]:
        if id is not None:
            if id.startswith(OPENALEX_ID_PREFIX):
                id = id[len(OPENALEX_ID_PREFIX) :]
            url = self._build_url(id)
            response = self._connection.request(
                HTTP_METHOD_GET, url, params=params
            )
            raise_for_status(response)
            return self._parse_response(response.json())
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
    ) -> ListResult[T]:
        params["search"] = query
        return self.list(filter=filter, **params)

    def random(self, **params: Any) -> T:
        url = self._build_url(RANDOM_PATH)
        params = normalize_params(params)
        response = self._connection.request(HTTP_METHOD_GET, url, params=params)
        raise_for_status(response)
        return self._parse_response(response.json())

    def autocomplete(self, query: str, **params: Any) -> ListResult[Any]:
        params[PARAM_Q] = query
        url = f"{self._connection.base_url}/{AUTOCOMPLETE_PATH}/{self.endpoint}"
        params = normalize_params(params)
        response = self._connection.request(HTTP_METHOD_GET, url, params=params)
        raise_for_status(response)
        return self._parse_list_response(response.json())

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
