"""Test async functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openalex import AsyncAuthors, AsyncWorks


@pytest.mark.asyncio
class TestAsyncEntities:
    """Test async entity classes."""

    async def test_async_get_single_work(self, mock_work_response):
        """Test getting a single work asynchronously."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_work_response
            mock_request.return_value = mock_response

            works = AsyncWorks()
            work = await works.get("W2741809807")

            assert work.id == "https://openalex.org/W2741809807"
            assert (
                work.title == "Generalized Gradient Approximation Made Simple"
            )

    async def test_async_search(self, mock_list_response):
        """Test async search functionality."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            works = AsyncWorks()
            results = await works.search("machine learning").get()

            assert results.meta.count == 100
            assert len(results.results) == 1

    async def test_async_filter(self, mock_list_response):
        """Test async filter functionality."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            authors = AsyncAuthors()
            results = await (
                authors.filter(works_count=">100")
                .filter(cited_by_count=">1000")
                .get()
            )

            assert results.meta.count == 100

    async def test_async_pagination(self, mock_list_response):
        """Test async pagination."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            # First page has results
            mock_response1 = MagicMock()
            mock_response1.status_code = 200
            mock_response1.json.return_value = mock_list_response

            # Second page is empty
            mock_response2 = MagicMock()
            mock_response2.status_code = 200
            mock_response2.json.return_value = {
                "meta": {
                    "count": 100,
                    "db_response_time_ms": 25,
                    "page": 2,
                    "per_page": 25,
                },
                "results": [],
                "group_by": None,
            }

            mock_request.side_effect = [mock_response1, mock_response2]

            works = AsyncWorks()
            all_works = []

            async for work in works.all():
                all_works.append(work)

            assert len(all_works) == 1
            assert mock_request.call_count == 2

    async def test_async_autocomplete(self):
        """Test async autocomplete."""
        mock_autocomplete = {
            "meta": {
                "count": 2,
                "db_response_time_ms": 10,
                "page": 1,
                "per_page": 25,
            },
            "results": [
                {
                    "id": "https://openalex.org/W123",
                    "display_name": "Machine Learning",
                    "entity_type": "work",
                    "cited_by_count": 1000,
                },
                {
                    "id": "https://openalex.org/A456",
                    "display_name": "Machine Learning Expert",
                    "entity_type": "author",
                    "works_count": 50,
                },
            ],
        }

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_autocomplete
            mock_request.return_value = mock_response

            works = AsyncWorks()
            results = await works.autocomplete("machine")

            assert len(results.results) == 2
            assert results.results[0].display_name == "Machine Learning"

    async def test_async_random(self, mock_work_response):
        """Test getting random entity asynchronously."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_work_response
            mock_request.return_value = mock_response

            works = AsyncWorks()
            work = await works.random()

            assert work.id == "https://openalex.org/W2741809807"

    async def test_connection_cleanup(self):
        """Test async connection cleanup."""
        from openalex import close_all_async_connections

        works = AsyncWorks()
        authors = AsyncAuthors()

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "meta": {
                    "count": 0,
                    "db_response_time_ms": 10,
                    "page": 1,
                    "per_page": 25,
                },
                "results": [],
                "group_by": None,
            }
            mock_request.return_value = mock_response

            await works.filter(is_oa=True).count()
            await authors.filter(works_count=">10").count()

        await close_all_async_connections()

        from openalex.connection import _async_connections

        assert len(_async_connections) == 0


@pytest.mark.asyncio
class TestAsyncQuery:
    """Test async query functionality."""

    async def test_query_building(self):
        """Test building complex async queries."""
        works = AsyncWorks()

        query = (
            works.filter(publication_year=2023)
            .filter(is_oa=True)
            .search("climate change")
            .sort("cited_by_count", "desc")
            .select("id", "title", "cited_by_count")
        )

        assert query._params["filter"]["publication_year"] == 2023
        assert query._params["filter"]["is_oa"] is True
        assert query._params["search"] == "climate change"
        assert query._params["sort"] == "cited_by_count:desc"
        assert query._params["select"] == "id,title,cited_by_count"

    async def test_first_helper(self, mock_list_response):
        """Test getting first result."""
        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_list_response
            mock_request.return_value = mock_response

            works = AsyncWorks()
            first_work = await works.filter(is_oa=True).first()

            assert first_work is not None
            assert first_work.id == "https://openalex.org/W2741809807"
