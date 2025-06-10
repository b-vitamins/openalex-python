"""Base test class for resource testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

import pytest

from openalex.exceptions import APIError, NotFoundError, RateLimitError
from openalex.models import ListResult

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from openalex import AsyncOpenAlex, OpenAlex
    from openalex.resources.base import AsyncBaseResource, BaseResource

T = TypeVar("T")


class BaseResourceTest(Generic[T]):
    """Base class for resource testing with common test patterns."""

    resource_name: ClassVar[str] = ""
    entity_class: ClassVar[type[Any]] = None  # type: ignore
    sample_id: ClassVar[str] = ""
    sample_ids: ClassVar[list[str]] = []

    # Override these in subclasses
    def get_resource(self, client: OpenAlex) -> BaseResource[T, Any]:
        """Get the resource from client."""
        raise NotImplementedError

    def get_async_resource(
        self, client: AsyncOpenAlex
    ) -> AsyncBaseResource[T, Any]:
        """Get the async resource from client."""
        raise NotImplementedError

    def get_sample_entity(self) -> dict[str, Any]:
        """Get a sample entity for testing."""
        raise NotImplementedError

    def get_list_response(self, **kwargs: Any) -> dict[str, Any]:
        """Get a sample list response."""
        meta_data = {
            "count": kwargs.get("count", 100),
            "db_response_time_ms": 25,
            "page": kwargs.get("page", 1),
            "per_page": kwargs.get("per_page", 25),
            "groups_count": kwargs.get("groups_count", 0),
            "next_cursor": kwargs.get("next_cursor"),
        }

        return {
            "meta": meta_data,
            "results": kwargs.get("results", [self.get_sample_entity()]),
            "group_by": kwargs.get("group_by"),
        }

    # Common test methods
    def test_get_single_entity(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single entity."""
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            json=entity_data,
        )

        resource = self.get_resource(client)
        entity = resource.get(self.sample_id)

        assert isinstance(entity, self.entity_class)
        assert entity.id == entity_data["id"]

    def test_get_with_full_url(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting entity with full OpenAlex URL."""
        entity_data = self.get_sample_entity()
        full_url = f"https://openalex.org/{self.sample_id}"

        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            json=entity_data,
        )

        resource = self.get_resource(client)
        entity = resource.get(full_url)
        assert entity.id == entity_data["id"]

    def test_get_not_found(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test 404 error handling."""
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/INVALID123?mailto=test%40example.com",
            status_code=404,
            json={
                "error": "Not found",
                "message": f"{self.resource_name} not found",
            },
        )

        resource = self.get_resource(client)
        with pytest.raises(NotFoundError):
            resource.get("INVALID123")

    def test_list_entities(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test listing entities."""
        list_response = self.get_list_response()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?mailto=test%40example.com",
            json=list_response,
        )

        resource = self.get_resource(client)
        result = resource.list()

        assert isinstance(result, ListResult)
        assert result.meta.count == 100
        assert len(result.results) == 1
        assert isinstance(result.results[0], self.entity_class)

    def test_search(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test search functionality."""
        search_response = self.get_list_response(count=50)
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?search=test+query&mailto=test%40example.com",
            json=search_response,
        )

        resource = self.get_resource(client)
        result = resource.search("test query")

        assert result.meta.count == 50

    def test_filter_simple(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        sample_filters: dict[str, Any],
    ) -> None:
        """Test simple filtering."""
        filter_response = self.get_list_response(count=25)
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?filter=is_oa%3Atrue&mailto=test%40example.com",
            json=filter_response,
        )

        resource = self.get_resource(client)
        result = resource.list(filter=sample_filters["simple"])

        assert result.meta.count == 25

    def test_filter_complex(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
        sample_filters: dict[str, Any],
    ) -> None:
        """Test complex filtering with multiple conditions."""
        # Complex filter string construction
        filter_str = "publication_year:2020|2021|2022,type:article,is_oa:true,cited_by_count:>100"

        filter_response = self.get_list_response(count=15)
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?filter={filter_str}&mailto=test%40example.com",
            json=filter_response,
        )

        resource = self.get_resource(client)
        result = resource.list(filter=sample_filters["complex"])

        assert result.meta.count == 15

    def test_pagination_basic(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test basic pagination."""
        # Page 1
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?per-page=10&page=1&mailto=test%40example.com",
            json=self.get_list_response(page=1, per_page=10, count=100),
        )

        # Page 2
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?per-page=10&page=2&mailto=test%40example.com",
            json=self.get_list_response(page=2, per_page=10, count=100),
        )

        resource = self.get_resource(client)
        paginator = resource.paginate(per_page=10, max_results=20)

        results = list(paginator)
        assert len(results) == 20

    def test_pagination_cursor(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test cursor-based pagination."""
        # First page with cursor
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?cursor=%2A&per-page=200&mailto=test%40example.com",
            json=self.get_list_response(
                per_page=200,
                count=50000,
                next_cursor="cursor123",
                results=[self.get_sample_entity()] * 200,
            ),
        )

        # Second page
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?cursor=cursor123&per-page=200&mailto=test%40example.com",
            json=self.get_list_response(
                per_page=200,
                count=50000,
                next_cursor=None,
                results=[],
            ),
        )

        resource = self.get_resource(client)
        paginator = resource.paginate(per_page=200, cursor="*")

        page_count = 0
        for _ in paginator.pages():
            page_count += 1
            if page_count >= 2:
                break

        assert page_count == 2

    def test_autocomplete(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test autocomplete functionality."""
        autocomplete_response = {
            "meta": {
                "count": 5,
                "db_response_time_ms": 10,
                "page": 1,
                "per_page": 10,
            },
            "results": [
                {
                    "id": self.sample_ids[0]
                    if self.sample_ids
                    else self.sample_id,
                    "display_name": "Test Result 1",
                    "entity_type": self.resource_name.rstrip("s"),
                    "cited_by_count": 100,
                    "works_count": 50,
                },
            ],
        }

        httpx_mock.add_response(
            url=f"https://api.openalex.org/autocomplete/{self.resource_name}?q=test&mailto=test%40example.com",
            json=autocomplete_response,
        )

        resource = self.get_resource(client)
        result = resource.autocomplete("test")

        assert result.meta.count == 5
        assert len(result.results) == 1

    def test_random(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting random entity."""
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/random?mailto=test%40example.com",
            json=entity_data,
        )

        resource = self.get_resource(client)
        entity = resource.random()

        assert isinstance(entity, self.entity_class)

    def test_field_selection(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test field selection with select parameter."""
        selected_fields = ["id", "display_name", "works_count"]

        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?select=id%2Cdisplay_name%2Cworks_count&mailto=test%40example.com",
            json=self.get_list_response(),
        )

        resource = self.get_resource(client)
        result = resource.list(select=selected_fields)

        assert result.meta.count == 100

    def test_group_by(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test group-by functionality."""
        group_response = {
            "meta": {"count": 5, "db_response_time_ms": 30, "groups_count": 5},
            "group_by": [
                {
                    "key": "article",
                    "key_display_name": "Article",
                    "count": 1000,
                },
                {"key": "book", "key_display_name": "Book", "count": 500},
            ],
        }

        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}?group-by=type&mailto=test%40example.com",
            json=group_response,
        )

        resource = self.get_resource(client)
        # Note: Implementation might need adjustment based on actual API
        result = resource.list(group_by="type")

        assert result.group_by is not None
        assert len(result.group_by) == 2

    def test_rate_limit_handling(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test rate limit error handling."""
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            status_code=429,
            headers={"Retry-After": "60"},
            json={"error": "Rate limit exceeded"},
        )

        resource = self.get_resource(client)
        with pytest.raises(RateLimitError) as exc_info:
            resource.get(self.sample_id)

        assert exc_info.value.retry_after == 60

    def test_server_error_handling(
        self,
        client: OpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test server error handling."""
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            status_code=500,
            json={"error": "Internal server error"},
        )

        resource = self.get_resource(client)
        with pytest.raises(APIError) as exc_info:
            resource.get(self.sample_id)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_async_get(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test async get operation."""
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            json=entity_data,
        )

        resource = self.get_async_resource(async_client)
        entity = await resource.get(self.sample_id)

        assert isinstance(entity, self.entity_class)

    @pytest.mark.asyncio
    async def test_async_pagination(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test async pagination."""
        for page in range(1, 3):
            httpx_mock.add_response(
                url=f"https://api.openalex.org/{self.resource_name}?per-page=5&page={page}&mailto=test%40example.com",
                json=self.get_list_response(page=page, per_page=5, count=10),
            )

        resource = self.get_async_resource(async_client)
        paginator = resource.paginate(per_page=5, max_results=10)

        results = []
        async for item in paginator:
            results.append(item)

        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_async_random(
        self, async_client: AsyncOpenAlex, httpx_mock: HTTPXMock
    ) -> None:
        entity_data = self.get_sample_entity()
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/random?mailto=test%40example.com",
            json=entity_data,
        )
        resource = self.get_async_resource(async_client)
        entity = await resource.random()
        assert isinstance(entity, self.entity_class)

    @pytest.mark.asyncio
    async def test_async_autocomplete(
        self, async_client: AsyncOpenAlex, httpx_mock: HTTPXMock
    ) -> None:
        autocomplete_response = {
            "meta": {
                "count": 3,
                "db_response_time_ms": 1,
                "page": 1,
                "per_page": 5,
            },
            "results": [
                {
                    "id": self.sample_id,
                    "display_name": "Test Result",
                    "entity_type": self.resource_name.rstrip("s"),
                    "cited_by_count": 1,
                    "works_count": 1,
                }
            ],
        }
        httpx_mock.add_response(
            url=f"https://api.openalex.org/autocomplete/{self.resource_name}?q=test&mailto=test%40example.com",
            json=autocomplete_response,
        )
        resource = self.get_async_resource(async_client)
        result = await resource.autocomplete("test")
        assert result.meta.count == 3
        assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_async_get_with_full_url(
        self,
        async_client: AsyncOpenAlex,
        httpx_mock: HTTPXMock,
    ) -> None:
        entity_data = self.get_sample_entity()
        full_url = f"https://openalex.org/{self.sample_id}"
        httpx_mock.add_response(
            url=f"https://api.openalex.org/{self.resource_name}/{self.sample_id}?mailto=test%40example.com",
            json=entity_data,
        )
        resource = self.get_async_resource(async_client)
        entity = await resource.get(full_url)
        assert entity.id == entity_data["id"]
