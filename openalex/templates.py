"""Abstract templates for DRY entity implementation."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from .metrics import MetricsReport
    from .query import AsyncQuery, Query

from pydantic import BaseModel, ValidationError
from structlog import get_logger

from .cache.manager import get_cache_manager
from .constants import (
    AUTOCOMPLETE_PATH,
    HTTP_METHOD_GET,
    PARAM_Q,
    RANDOM_PATH,
)
from .exceptions import raise_for_status
from .models import (
    AutocompleteResult,
    BaseFilter,
    ListResult,
    Meta,
)
from .utils.params import normalize_params
from .utils.validation import validate_entity_id

if TYPE_CHECKING:
    from .config import OpenAlexConfig

T = TypeVar("T", bound=BaseModel)
F = TypeVar("F", bound=BaseFilter)

logger = get_logger(__name__)


class EntityLogicBase(Generic[T, F]):
    """Shared business logic for entity operations (not abstract)."""

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        from .config import OpenAlexConfig

        if config is None:
            config = OpenAlexConfig()

        # Override with provided params
        updates: dict[str, Any] = {}
        if email is not None:
            updates["email"] = email
        if api_key is not None:
            updates["api_key"] = api_key

        if updates:
            config = config.model_copy(update=updates)

        self._config = config
        self.endpoint: str = ""
        self.model_class: type[T] = None  # type: ignore

    def _build_url(self, path: str = "") -> str:
        """Build URL for API requests."""
        base_url = str(self._config.base_url).rstrip("/")
        endpoint = self.endpoint.strip("/")
        path = path.strip("/")

        if path:
            return f"{base_url}/{endpoint}/{path}"
        return f"{base_url}/{endpoint}"

    def _parse_response(self, data: dict[str, Any]) -> T:
        """Parse single entity response."""
        try:
            return self.model_class.model_validate(data)
        except ValidationError as e:
            logger.warning(
                "Validation failed, attempting model_construct: %s", e
            )
            try:
                # Use model_construct as fallback
                return self.model_class.model_construct(**data)  # type: ignore
            except Exception as fallback_error:
                logger.exception("Failed to parse response with fallback")
                raise e from fallback_error

    def parse_list_response(self, data: dict[str, Any]) -> ListResult[T]:
        """Parse list response with full query.py compatibility."""
        return self._parse_list_response(data)

    def _parse_list_response(self, data: dict[str, Any]) -> ListResult[T]:
        """Parse list response with full query.py compatibility."""
        results: list[T] = []
        for item in data.get("results", []):
            try:
                results.append(self.model_class(**item))
            except ValidationError:
                try:
                    # Use model_construct as fallback
                    results.append(self.model_class.model_construct(**item))  # type: ignore
                except Exception as e:
                    logger.warning("Skipping invalid item: %s", e)

        meta_data = data.get("meta", {})
        per_page_value = meta_data.get("per_page", len(results))
        meta_defaults = {
            "count": meta_data.get("count", 0),
            "db_response_time_ms": meta_data.get("db_response_time_ms", 0),
            "page": meta_data.get("page", 1),
            "per_page": per_page_value,
            "groups_count": meta_data.get("groups_count"),
            "next_cursor": meta_data.get("next_cursor"),
        }

        try:
            meta = Meta.model_validate(meta_defaults)
        except ValidationError:
            meta = Meta.model_construct(**meta_defaults)

        try:
            return ListResult[self.model_class](  # type: ignore
                meta=meta,
                results=results,
                group_by=data.get("group_by"),
            )
        except ValidationError:
            return ListResult[self.model_class].model_construct(  # type: ignore
                meta=meta,
                results=results,
                group_by=data.get("group_by"),
            )

    def _normalize_and_validate_id(self, entity_id: str) -> str:
        """Validate and normalize entity ID."""
        return validate_entity_id(entity_id, self.endpoint.rstrip("s"))

    def _prepare_params(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Normalize parameters for API request."""
        return normalize_params(params or {})

    def clear_cache(self) -> None:
        """Clear the cache for this entity."""
        cache_manager = get_cache_manager(self._config)
        cache_manager.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        cache_manager = get_cache_manager(self._config)
        return cache_manager.stats()

    def metrics(self) -> MetricsReport:
        """Get performance metrics for this entity."""
        from .metrics import get_metrics_collector

        collector = get_metrics_collector(self._config)
        return collector.get_report()

    def get_metrics(self) -> MetricsReport | None:
        """Get performance metrics for this entity (alias for metrics)."""
        if not self._config.collect_metrics:
            return None
        return self.metrics()


class SyncEntityTemplate(EntityLogicBase[T, F]):
    """Template for synchronous entity operations."""

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        super().__init__(email, api_key, config)
        from .connection import get_connection

        self._connection = get_connection(self._config)

    @property
    def config(self) -> OpenAlexConfig:
        """Get the current configuration."""
        return self._config

    def _execute_request(
        self, url: str, params: dict[str, Any], operation: str | None = None
    ) -> dict[str, Any]:
        """Execute a single HTTP request."""
        response = self._connection.request(
            HTTP_METHOD_GET,
            url,
            params=params,
            operation=operation,
        )
        raise_for_status(response)
        return cast("dict[str, Any]", response.json())

    def _get_single_entity(
        self, entity_id: str, params: dict[str, Any] | None = None
    ) -> T:
        """Get a single entity by ID."""
        valid_id = self._normalize_and_validate_id(entity_id)
        norm_params = self._prepare_params(params)
        url = self._build_url(valid_id)

        cache_manager = get_cache_manager(self._config)

        def fetch() -> dict[str, Any]:
            return self._execute_request(url, norm_params, operation="get")

        data = cache_manager.get_or_fetch(
            endpoint=self.endpoint,
            fetch_func=fetch,
            entity_id=entity_id,
            params=params or {},
        )
        if isinstance(data, self.model_class):
            return data
        return self._parse_response(data)

    def get_many(self, ids: list[str], max_concurrent: int = 10) -> list[T]:
        """Fetch multiple entities efficiently using concurrent requests."""
        import concurrent.futures

        # Validate all IDs first
        validated_ids: list[str] = []
        for entity_id in ids:
            try:
                valid_id = self._normalize_and_validate_id(entity_id)
                validated_ids.append(valid_id)
            except ValueError as e:
                # Try to use the entities logger for consistency with tests
                try:
                    from .entities import logger as entities_logger

                    entities_logger.warning(
                        "Skipping invalid ID %s: %s", entity_id, e
                    )
                except ImportError:
                    logger.warning("Skipping invalid ID %s: %s", entity_id, e)

        results: list[T] = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
            future_to_id = {
                executor.submit(self.get, vid): vid for vid in validated_ids
            }

            for future in concurrent.futures.as_completed(future_to_id):
                vid = future_to_id[future]
                try:
                    result = future.result()
                    # get() returns T | ListResult[T], but with ID it should always be T
                    if isinstance(result, ListResult):
                        # This shouldn't happen, but handle gracefully
                        continue
                    results.append(result)
                except Exception:
                    try:
                        from .entities import logger as entities_logger

                        entities_logger.exception("Failed to fetch %s", vid)
                    except (ImportError, TypeError):
                        logger.exception("Failed to fetch %s", vid)

        return results

    def get(self, id: str | None = None, **params: Any) -> T | ListResult[T]:
        """Retrieve a single entity or list results."""
        if id is not None:
            return self._get_single_entity(id, params)
        return self.query().get(**params)

    def list(self, **params: Any) -> ListResult[T]:
        """Get a list of entities with parameters."""
        norm_params = self._prepare_params(params)
        url = self._build_url()

        # Determine operation based on parameters
        operation = "list"
        if norm_params and (
            (
                isinstance(norm_params.get("filter"), dict)
                and "search" in norm_params["filter"]
            )
            or norm_params.get("search")
        ):
            operation = "search"

        # Add caching for list operations
        cache_manager = get_cache_manager(self._config)

        if cache_manager.enabled:
            from .cache.base import CacheKeyBuilder

            # Use a special entity_id for list operations that includes parameters
            params_str = str(sorted(norm_params.items()))
            list_key = (
                f"list_{hashlib.md5(params_str.encode()).hexdigest()[:8]}"
            )
            cache_key = CacheKeyBuilder.build_key(
                self.endpoint, list_key, norm_params
            )

            # Try cache first
            cache = cache_manager.cache
            cached_data = cache.get(cache_key) if cache is not None else None
            if cached_data is not None:
                logger.debug(
                    "cache_hit", endpoint=self.endpoint, list_key=list_key
                )
                return self._parse_list_response(cached_data)

            # Fetch and cache
            response_data = self._execute_request(
                url, norm_params, operation=operation
            )
            ttl = cache_manager.get_ttl_for_endpoint(self.endpoint)
            cache = cache_manager.cache
            if cache is not None:
                cache.set(cache_key, response_data, ttl)
            logger.debug(
                "cache_miss", endpoint=self.endpoint, list_key=list_key
            )

            return self._parse_list_response(response_data)
        # No cache, fetch directly
        response_data = self._execute_request(
            url, norm_params, operation=operation
        )
        return self._parse_list_response(response_data)

    def get_list(self, **params: Any) -> dict[str, Any]:
        """Get raw list data for streaming and other internal uses."""
        norm_params = self._prepare_params(params)
        url = self._build_url()

        # Determine operation based on parameters
        operation = "list"
        if norm_params and (
            (
                isinstance(norm_params.get("filter"), dict)
                and "search" in norm_params["filter"]
            )
            or norm_params.get("search")
        ):
            operation = "search"

        return self._execute_request(url, norm_params, operation=operation)

    def query(self) -> Query[T, F]:
        """Return a query builder for this entity."""
        from .query import Query

        return Query(self, {})

    def filter(self, **kwargs: Any) -> Query[T, F]:
        """Return a query with filters applied."""
        return self.query().filter(**kwargs)

    def search(
        self,
        query: str,
        filter: dict[str, Any] | None = None,
        **params: Any,
    ) -> Query[T, F]:
        """Return a query with a search term applied."""
        from .query import Query

        q = self.query()
        if filter:
            q = q.filter(**filter)
        q = q.search(query)
        if params:
            q = Query(q.entity, {**q.params, **params})
        return q

    # Query delegation methods for chaining
    def filter_gt(self, **kwargs: Any) -> Query[T, F]:
        """Filter with greater than conditions."""
        return self.query().filter_gt(**kwargs)

    def filter_gte(self, **kwargs: Any) -> Query[T, F]:
        """Filter with greater than or equal conditions."""
        return self.query().filter_gte(**kwargs)

    def filter_lt(self, **kwargs: Any) -> Query[T, F]:
        """Filter with less than conditions."""
        return self.query().filter_lt(**kwargs)

    def filter_lte(self, **kwargs: Any) -> Query[T, F]:
        """Filter with less than or equal conditions."""
        return self.query().filter_lte(**kwargs)

    def filter_not(self, **kwargs: Any) -> Query[T, F]:
        """Filter with NOT conditions."""
        return self.query().filter_not(**kwargs)

    def filter_or(self, **kwargs: Any) -> Query[T, F]:
        """Filter with OR conditions."""
        return self.query().filter_or(**kwargs)

    def search_filter(self, **kwargs: Any) -> Query[T, F]:
        """Filter with search conditions on specific fields."""
        return self.query().search_filter(**kwargs)

    def sort(self, **kwargs: str) -> Query[T, F]:
        """Sort results."""
        return self.query().sort(**kwargs)

    def group_by(self, *keys: str) -> Query[T, F]:
        """Group results by keys."""
        return self.query().group_by(*keys)

    def select(self, fields: list[str] | str) -> Query[T, F]:
        """Select specific fields."""
        return self.query().select(fields)

    def sample(self, n: int, seed: int | None = None) -> Query[T, F]:
        """Sample random results."""
        return self.query().sample(n, seed)

    def paginate(
        self, per_page: int = 25, max_results: int | None = None, **kwargs: Any
    ):
        """Get paginator for results."""
        from .utils.pagination import Paginator

        params = kwargs

        def fetch_page(page_params: dict[str, Any]):
            all_params = {**params, **page_params}
            return self.list(**all_params)

        return Paginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    def all(
        self, per_page: int = 1, max_results: int | None = None, **kwargs: Any
    ):
        """Iterate over all results."""
        paginator = self.paginate(per_page, max_results, **kwargs)
        yielded_count = 0
        for page in paginator:
            for item in page.results:
                if max_results and yielded_count >= max_results:
                    return
                yield item
                yielded_count += 1

    def count(self) -> int:
        """Count results."""
        result = self.list(per_page=1)
        return result.meta.count

    def first(self):
        """Get first result."""
        results = self.list(per_page=1)
        return results.results[0] if results.results else None

    def __getitem__(self, key: str) -> T:
        """Support indexing for ID lookup."""
        result = self.query()[key]
        if isinstance(result, list):
            # This shouldn't happen for single key lookup, but handle it
            msg = "Single key lookup returned multiple results"
            raise TypeError(msg)
        return result  # type: ignore

    def autocomplete(
        self, query: str, **params: Any
    ) -> ListResult[AutocompleteResult]:
        """Get autocomplete suggestions."""
        params = self._prepare_params({PARAM_Q: query, **params})

        # Build autocomplete URL: /autocomplete/{entity}
        base_url = str(self._config.base_url).rstrip("/")
        url = f"{base_url}/{AUTOCOMPLETE_PATH}/{self.endpoint}"

        response_data = self._execute_request(
            url, params, operation="autocomplete"
        )

        # Parse autocomplete results
        results: list[AutocompleteResult] = []
        for item in response_data.get("results", []):
            try:
                results.append(AutocompleteResult.model_validate(item))
            except ValidationError:
                try:
                    results.append(AutocompleteResult.model_construct(**item))
                except Exception as e:
                    logger.warning("Skipping invalid autocomplete item: %s", e)

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
            return ListResult[AutocompleteResult](
                meta=meta,
                results=results,
            )
        except ValidationError:
            return ListResult[AutocompleteResult].model_construct(
                meta=meta,
                results=results,
            )

    def random(self, **params: Any) -> T:
        """Get a random entity."""
        url = self._build_url(RANDOM_PATH)
        params = self._prepare_params(params)

        response_data = self._execute_request(url, params, operation="get")
        return self._parse_response(response_data)

    def warm_cache(
        self,
        ids: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        **params: Any,
    ) -> dict[str, T | None]:
        """Warm the cache with frequently accessed data."""
        results: dict[str, T | None] = {}

        if ids:
            for entity_id in ids:
                try:
                    entity = self._get_single_entity(entity_id, params)
                    results[entity_id] = entity
                except Exception as e:
                    logger.warning(
                        "Failed to warm cache for %s: %s", entity_id, e
                    )
                    results[entity_id] = None

        if filters:
            try:
                list_params = {**params}
                if filters:
                    list_params["filter"] = filters
                list_params = self._prepare_params(list_params)
                url = self._build_url()
                self._execute_request(url, list_params, operation="list")
            except Exception as e:
                logger.warning("Failed to warm cache for filters: %s", e)

        return results


class AsyncEntityTemplate(EntityLogicBase[T, F]):
    """Template for asynchronous entity operations."""

    def __init__(
        self,
        email: str | None = None,
        api_key: str | None = None,
        config: OpenAlexConfig | None = None,
    ) -> None:
        super().__init__(email, api_key, config)
        self._connection = None

    async def _get_connection(self):
        """Get or create async connection."""
        if self._connection is None:
            from .connection import get_async_connection

            self._connection = await get_async_connection(self._config)
        return self._connection

    async def _execute_request(
        self, url: str, params: dict[str, Any], operation: str | None = None
    ) -> dict[str, Any]:
        """Execute a single HTTP request asynchronously."""
        connection = await self._get_connection()
        response = await connection.request(
            HTTP_METHOD_GET,
            url,
            params=params,
            operation=operation,
        )
        raise_for_status(response)
        return cast("dict[str, Any]", response.json())

    async def _get_single_entity(
        self, entity_id: str, params: dict[str, Any] | None = None
    ) -> T:
        """Get a single entity by ID asynchronously."""
        valid_id = self._normalize_and_validate_id(entity_id)
        norm_params = self._prepare_params(params)
        url = self._build_url(valid_id)

        # Simple async cache implementation
        cache_manager = get_cache_manager(self._config)

        if cache_manager.enabled:
            from .cache.base import CacheKeyBuilder

            cache_key = CacheKeyBuilder.build_key(
                self.endpoint, entity_id, params or {}
            )

            # Try cache first
            cache = cache_manager.cache
            cached_data = cache.get(cache_key) if cache is not None else None
            if cached_data is not None:
                logger.debug(
                    "cache_hit", endpoint=self.endpoint, entity_id=entity_id
                )
                if isinstance(cached_data, self.model_class):
                    return cached_data
                return self._parse_response(cached_data)

            # Fetch and cache
            response_data = await self._execute_request(
                url, norm_params, operation="get"
            )
            ttl = cache_manager.get_ttl_for_endpoint(self.endpoint)
            cache = cache_manager.cache
            if cache is not None:
                cache.set(cache_key, response_data, ttl)
            logger.debug(
                "cache_miss", endpoint=self.endpoint, entity_id=entity_id
            )

            return self._parse_response(response_data)
        # No cache, fetch directly
        response_data = await self._execute_request(
            url, norm_params, operation="get"
        )
        return self._parse_response(response_data)

    async def get_many(
        self, ids: list[str], max_concurrent: int = 10
    ) -> list[T]:
        """Fetch multiple entities efficiently using concurrent requests."""
        import asyncio

        validated_ids: list[str] = []
        for entity_id in ids:
            try:
                valid_id = self._normalize_and_validate_id(entity_id)
                validated_ids.append(valid_id)
            except ValueError as e:
                # Try to use the entities logger for consistency with tests
                try:
                    from .entities import logger as entities_logger

                    entities_logger.warning(
                        "Skipping invalid ID %s: %s", entity_id, e
                    )
                except ImportError:
                    logger.warning("Skipping invalid ID %s: %s", entity_id, e)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(entity_id: str) -> T | None:
            async with semaphore:
                try:
                    result = await self.get(entity_id)
                    # get() returns T | ListResult[T], but with ID it should always be T
                    if isinstance(result, ListResult):
                        # This shouldn't happen, but handle gracefully
                        return None
                    return result  # noqa: TRY300
                except Exception:
                    try:
                        from .entities import logger as entities_logger

                        entities_logger.exception(
                            "Failed to fetch %s", entity_id
                        )
                    except (ImportError, TypeError):
                        logger.exception("Failed to fetch %s", entity_id)
                    return None

        results = await asyncio.gather(
            *[fetch_with_semaphore(vid) for vid in validated_ids]
        )
        return [r for r in results if r is not None]

    async def get(
        self, id: str | None = None, **params: Any
    ) -> T | ListResult[T]:
        """Retrieve a single entity or list results."""
        if id is not None:
            return await self._get_single_entity(id, params)
        result = await self.query().get(**params)
        # AsyncQuery.get() returns ListResult or GroupByResult, never T
        if isinstance(result, ListResult):
            return result
        # For GroupByResult, we need to handle this case
        msg = "GroupBy results not supported in this context"
        raise TypeError(msg)

    async def list(self, **params: Any) -> ListResult[T]:
        """Get a list of entities with parameters."""
        norm_params = self._prepare_params(params)
        url = self._build_url()

        # Determine operation based on parameters
        operation = "list"
        if norm_params and (
            (
                isinstance(norm_params.get("filter"), dict)
                and "search" in norm_params["filter"]
            )
            or norm_params.get("search")
        ):
            operation = "search"

        # Add caching for list operations
        cache_manager = get_cache_manager(self._config)

        if cache_manager.enabled:
            from .cache.base import CacheKeyBuilder

            # Use a special entity_id for list operations that includes parameters
            params_str = str(sorted(norm_params.items()))
            list_key = (
                f"list_{hashlib.md5(params_str.encode()).hexdigest()[:8]}"
            )
            cache_key = CacheKeyBuilder.build_key(
                self.endpoint, list_key, norm_params
            )

            # Try cache first
            cache = cache_manager.cache
            cached_data = cache.get(cache_key) if cache is not None else None
            if cached_data is not None:
                logger.debug(
                    "cache_hit", endpoint=self.endpoint, list_key=list_key
                )
                return self._parse_list_response(cached_data)

            # Fetch and cache
            response_data = await self._execute_request(
                url, norm_params, operation=operation
            )
            ttl = cache_manager.get_ttl_for_endpoint(self.endpoint)
            cache = cache_manager.cache
            if cache is not None:
                cache.set(cache_key, response_data, ttl)
            logger.debug(
                "cache_miss", endpoint=self.endpoint, list_key=list_key
            )

            return self._parse_list_response(response_data)
        # No cache, fetch directly
        response_data = await self._execute_request(
            url, norm_params, operation=operation
        )
        return self._parse_list_response(response_data)

    async def get_list(self, **params: Any) -> dict[str, Any]:
        """Get raw list data for streaming and other internal uses."""
        norm_params = self._prepare_params(params)
        url = self._build_url()

        # Determine operation based on parameters
        operation = "list"
        if norm_params and (
            (
                isinstance(norm_params.get("filter"), dict)
                and "search" in norm_params["filter"]
            )
            or norm_params.get("search")
        ):
            operation = "search"

        return await self._execute_request(
            url, norm_params, operation=operation
        )

    def query(self) -> AsyncQuery[T, F]:
        """Return an async query builder for this entity."""
        from .query import AsyncQuery

        return AsyncQuery(self, self.model_class, self._config)

    def filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Return a query with filters applied."""
        return self.query().filter(**kwargs)

    def search(
        self,
        query: str,
        filter: dict[str, Any] | None = None,
        **params: Any,
    ) -> AsyncQuery[T, F]:
        """Return a query with a search term applied."""
        q = self.query()
        if filter:
            q = q.filter(**filter)
        q = q.search(query)
        if params:
            # Use public method to update parameters
            q = q.update_params(**params)
        return q

    async def autocomplete(
        self, query: str, **params: Any
    ) -> ListResult[AutocompleteResult]:
        """Get autocomplete suggestions."""
        params = self._prepare_params({PARAM_Q: query, **params})

        # Build autocomplete URL: /autocomplete/{entity}
        base_url = str(self._config.base_url).rstrip("/")
        url = f"{base_url}/{AUTOCOMPLETE_PATH}/{self.endpoint}"

        response_data = await self._execute_request(
            url, params, operation="autocomplete"
        )

        # Parse autocomplete results
        results: list[AutocompleteResult] = []
        for item in response_data.get("results", []):
            try:
                results.append(AutocompleteResult.model_validate(item))
            except ValidationError:
                try:
                    results.append(AutocompleteResult.model_construct(**item))
                except Exception as e:
                    logger.warning("Skipping invalid autocomplete item: %s", e)

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
            return ListResult[AutocompleteResult](
                meta=meta,
                results=results,
            )
        except ValidationError:
            return ListResult[AutocompleteResult].model_construct(
                meta=meta,
                results=results,
            )

    async def random(self, **params: Any) -> T:
        """Get a random entity."""
        url = self._build_url(RANDOM_PATH)
        params = self._prepare_params(params)

        response_data = await self._execute_request(
            url, params, operation="get"
        )
        return self._parse_response(response_data)

    # Query delegation methods for chaining
    def filter_gt(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with greater than conditions."""
        return self.query().filter_gt(**kwargs)

    def filter_gte(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with greater than or equal conditions."""
        return self.query().filter_gte(**kwargs)

    def filter_lt(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with less than conditions."""
        return self.query().filter_lt(**kwargs)

    def filter_lte(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with less than or equal conditions."""
        return self.query().filter_lte(**kwargs)

    def filter_not(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with NOT conditions."""
        return self.query().filter_not(**kwargs)

    def filter_or(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with OR conditions."""
        return self.query().filter_or(**kwargs)

    def search_filter(self, **kwargs: Any) -> AsyncQuery[T, F]:
        """Filter with search conditions on specific fields."""
        return self.query().search_filter(**kwargs)

    def sort(self, **kwargs: str) -> AsyncQuery[T, F]:
        """Sort results."""
        return self.query().sort(**kwargs)

    def group_by(self, *keys: str) -> AsyncQuery[T, F]:
        """Group results by keys."""
        return self.query().group_by(*keys)

    def select(self, fields: list[str] | str) -> AsyncQuery[T, F]:
        """Select specific fields."""
        return self.query().select(fields)

    def sample(self, n: int, seed: int | None = None) -> AsyncQuery[T, F]:
        """Sample random results."""
        return self.query().sample(n, seed)

    def paginate(
        self, per_page: int = 25, max_results: int | None = None, **kwargs: Any
    ):
        """Get async paginator for results."""
        from .utils.pagination import AsyncPaginator

        params = kwargs

        async def fetch_page(page_params: dict[str, Any]):
            all_params = {**params, **page_params}
            return await self.list(**all_params)

        return AsyncPaginator(
            fetch_func=fetch_page,
            params=params,
            per_page=per_page,
            max_results=max_results,
        )

    async def all(
        self, per_page: int = 1, max_results: int | None = None, **kwargs: Any
    ):
        """Iterate over all results."""
        paginator = self.paginate(per_page, max_results, **kwargs)
        yielded_count = 0
        async for item in paginator:
            if max_results and yielded_count >= max_results:
                return
            yield item
            yielded_count += 1

    async def count(self) -> int:
        """Count results."""
        result = await self.list(per_page=1)
        return result.meta.count

    async def first(self):
        """Get first result."""
        results = await self.list(per_page=1)
        return results.results[0] if results.results else None

    async def warm_cache(
        self,
        ids: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        **params: Any,
    ) -> dict[str, T | None]:
        """Warm the cache with frequently accessed data."""
        results: dict[str, T | None] = {}

        if ids:
            for entity_id in ids:
                try:
                    entity = await self._get_single_entity(entity_id, params)
                    results[entity_id] = entity
                except Exception as e:
                    logger.warning(
                        "Failed to warm cache for %s: %s", entity_id, e
                    )
                    results[entity_id] = None

        if filters:
            try:
                list_params = {**params}
                if filters:
                    list_params["filter"] = filters
                list_params = self._prepare_params(list_params)
                url = self._build_url()
                await self._execute_request(url, list_params, operation="list")
            except Exception as e:
                logger.warning("Failed to warm cache for filters: %s", e)

        return results
