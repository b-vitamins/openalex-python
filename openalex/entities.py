"""Direct entity access for PyAlex-style interface using DRY templates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models.base import ListResult
    from .models.work import Ngram

__all__ = [
    "AsyncAuthors",
    "AsyncConcepts",
    "AsyncFunders",
    "AsyncInstitutions",
    "AsyncKeywords",
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
    "_build_list_result",
]

# Import logger for behavior tests compatibility
from structlog import get_logger

from .models import (
    Author,
    Concept,
    Funder,
    Institution,
    Keyword,
    Publisher,
    Source,
    Topic,
    Work,
)
from .models.filters import BaseFilter
from .templates import AsyncEntityTemplate, SyncEntityTemplate

logger = get_logger(__name__)


# Sync Entity Classes using the template - use the template directly as BaseEntity
BaseEntity = SyncEntityTemplate


class Works(BaseEntity[Work, BaseFilter]):
    """Access works entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "works"
        self.model_class = Work

    def ngrams(self, work_id: str, **params: Any) -> ListResult[Ngram]:
        """Get n-grams for a specific work."""
        from pydantic import ValidationError
        from structlog import get_logger

        from .models.base import ListResult, Meta
        from .models.work import Ngram

        logger = get_logger(__name__)

        url = self._build_url(f"{work_id}/ngrams")
        params = self._prepare_params(params)

        response_data = self._execute_request(url, params)

        # Parse ngram results
        results: list[Ngram] = []
        for item in response_data.get("results", []):
            try:
                results.append(Ngram.model_validate(item))
            except ValidationError:
                try:
                    results.append(Ngram.model_construct(**item))
                except Exception as e:
                    logger.warning("Skipping invalid ngram item: %s", e)

        meta_data = response_data.get("meta", {})
        meta_defaults = {
            "count": meta_data.get("count", len(results)),
            "db_response_time_ms": meta_data.get("db_response_time_ms", 0),
            "page": meta_data.get("page", 1),
            "per_page": meta_data.get("per_page", len(results)),
            "groups_count": meta_data.get("groups_count"),
            "next_cursor": meta_data.get("next_cursor"),
        }

        try:
            meta = Meta.model_validate(meta_defaults)
        except ValidationError:
            meta = Meta.model_construct(**meta_defaults)

        try:
            return ListResult[Ngram](
                meta=meta,
                results=results,
            )
        except ValidationError:
            return ListResult[Ngram].model_construct(
                meta=meta,
                results=results,
            )


class Authors(BaseEntity[Author, BaseFilter]):
    """Access authors entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "authors"
        self.model_class = Author


class Institutions(BaseEntity[Institution, BaseFilter]):
    """Access institutions entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "institutions"
        self.model_class = Institution


class Sources(BaseEntity[Source, BaseFilter]):
    """Access sources entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "sources"
        self.model_class = Source


class Topics(BaseEntity[Topic, BaseFilter]):
    """Access topics entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "topics"
        self.model_class = Topic


class Publishers(BaseEntity[Publisher, BaseFilter]):
    """Access publishers entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "publishers"
        self.model_class = Publisher


class Funders(BaseEntity[Funder, BaseFilter]):
    """Access funders entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "funders"
        self.model_class = Funder


class Keywords(BaseEntity[Keyword, BaseFilter]):
    """Access keywords entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "keywords"
        self.model_class = Keyword


class Concepts(BaseEntity[Concept, BaseFilter]):
    """Access concepts entity with full API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "concepts"
        self.model_class = Concept


# Async Entity Classes using the template - use the template directly as AsyncBaseEntity
AsyncBaseEntity = AsyncEntityTemplate


class AsyncWorks(AsyncBaseEntity[Work, BaseFilter]):
    """Access works entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "works"
        self.model_class = Work

    async def ngrams(self, work_id: str, **params: Any) -> ListResult[Ngram]:
        """Get n-grams for a specific work asynchronously."""
        from pydantic import ValidationError
        from structlog import get_logger

        from .models.base import ListResult, Meta
        from .models.work import Ngram

        logger = get_logger(__name__)

        url = self._build_url(f"{work_id}/ngrams")
        params = self._prepare_params(params)

        response_data = await self._execute_request(url, params)

        # Parse ngram results
        results: list[Ngram] = []
        for item in response_data.get("results", []):
            try:
                results.append(Ngram.model_validate(item))
            except ValidationError:
                try:
                    results.append(Ngram.model_construct(**item))
                except Exception as e:
                    logger.warning("Skipping invalid ngram item: %s", e)

        meta_data = response_data.get("meta", {})
        meta_defaults = {
            "count": meta_data.get("count", len(results)),
            "db_response_time_ms": meta_data.get("db_response_time_ms", 0),
            "page": meta_data.get("page", 1),
            "per_page": meta_data.get("per_page", len(results)),
            "groups_count": meta_data.get("groups_count"),
            "next_cursor": meta_data.get("next_cursor"),
        }

        try:
            meta = Meta.model_validate(meta_defaults)
        except ValidationError:
            meta = Meta.model_construct(**meta_defaults)

        try:
            return ListResult[Ngram](
                meta=meta,
                results=results,
            )
        except ValidationError:
            return ListResult[Ngram].model_construct(
                meta=meta,
                results=results,
            )


class AsyncAuthors(AsyncBaseEntity[Author, BaseFilter]):
    """Access authors entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "authors"
        self.model_class = Author


class AsyncInstitutions(AsyncBaseEntity[Institution, BaseFilter]):
    """Access institutions entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "institutions"
        self.model_class = Institution


class AsyncSources(AsyncBaseEntity[Source, BaseFilter]):
    """Access sources entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "sources"
        self.model_class = Source


class AsyncTopics(AsyncBaseEntity[Topic, BaseFilter]):
    """Access topics entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "topics"
        self.model_class = Topic


class AsyncPublishers(AsyncBaseEntity[Publisher, BaseFilter]):
    """Access publishers entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "publishers"
        self.model_class = Publisher


class AsyncFunders(AsyncBaseEntity[Funder, BaseFilter]):
    """Access funders entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "funders"
        self.model_class = Funder


class AsyncKeywords(AsyncBaseEntity[Keyword, BaseFilter]):
    """Access keywords entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "keywords"
        self.model_class = Keyword


class AsyncConcepts(AsyncBaseEntity[Concept, BaseFilter]):
    """Access concepts entity with full async API."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.endpoint = "concepts"
        self.model_class = Concept


# Compatibility aliases - maintain backwards compatibility
def _build_list_result(
    data: dict[str, Any], model_class: type[Any]
) -> ListResult[Any]:
    """Compatibility function for old code."""
    from .config import OpenAlexConfig
    from .templates import EntityLogicBase

    logic = EntityLogicBase[Any, Any](config=OpenAlexConfig())
    logic.model_class = model_class
    return logic.parse_list_response(data)


# Legacy imports for backwards compatibility
