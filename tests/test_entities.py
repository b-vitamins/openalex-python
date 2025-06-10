"""Test convenience entity classes."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from openalex import Authors, Institutions, Works
from openalex.models import ListResult


class TestEntityClasses:
    """Test entity convenience wrappers."""

    def test_direct_id_access(self):
        """Test direct access by ID."""
        with patch("openalex.entities.OpenAlex") as mock_client_class:
            mock_client = Mock()
            mock_resource = Mock()
            mock_query = Mock()
            mock_client_class.return_value = mock_client
            mock_client.works = mock_resource
            mock_resource.query.return_value = mock_query
            mock_query.__getitem__ = Mock(
                return_value={"id": "W123", "title": "Test"}
            )
            works = Works()
            result = works["W123"]
            assert result["id"] == "W123"
            mock_query.__getitem__.assert_called_once_with("W123")

    def test_filter_chain(self):
        """Test filter method chaining."""
        with patch("openalex.entities.OpenAlex") as mock_client_class:
            mock_client = Mock()
            mock_resource = Mock()
            mock_query = Mock()
            mock_client_class.return_value = mock_client
            mock_client.authors = mock_resource
            mock_resource.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.search.return_value = mock_query
            mock_query.sort.return_value = mock_query
            mock_query.get.return_value = ListResult(
                meta={
                    "count": 10,
                    "db_response_time_ms": 1,
                    "page": 1,
                    "per_page": 25,
                },
                results=[],
            )
            authors = Authors()
            result = (
                authors.filter(is_oa=True)
                .search("einstein")
                .sort(cited_by_count="desc")
                .get()
            )
            assert result.meta.count == 10
            mock_query.filter.assert_called_once_with(is_oa=True)
            mock_query.search.assert_called_once_with("einstein")
            mock_query.sort.assert_called_once_with(cited_by_count="desc")

    def test_convenience_methods(self):
        """Test all convenience methods create queries."""
        with patch("openalex.entities.OpenAlex") as mock_client_class:
            mock_client = Mock()
            mock_resource = Mock()
            mock_query = Mock()
            mock_client_class.return_value = mock_client
            mock_client.institutions = mock_resource
            mock_resource.query.return_value = mock_query
            mock_query.filter_or.return_value = mock_query
            mock_query.filter_not.return_value = mock_query
            mock_query.filter_gt.return_value = mock_query
            mock_query.filter_lt.return_value = mock_query
            mock_query.search_filter.return_value = mock_query
            mock_query.group_by.return_value = mock_query
            mock_query.select.return_value = mock_query
            mock_query.sample.return_value = mock_query
            inst = Institutions()
            inst.filter_or(country="US")
            mock_query.filter_or.assert_called_once()
            inst.filter_not(type="company")
            mock_query.filter_not.assert_called_once()
            inst.filter_gt(works_count=1000)
            mock_query.filter_gt.assert_called_once()
            inst.filter_lt(works_count=100)
            mock_query.filter_lt.assert_called_once()
            inst.search_filter(display_name="MIT")
            mock_query.search_filter.assert_called_once()
            inst.group_by("type")
            mock_query.group_by.assert_called_once()
            inst.select(["id", "display_name"])
            mock_query.select.assert_called_once()
            inst.sample(10, seed=42)
            mock_query.sample.assert_called_once_with(10, 42)

    def test_direct_methods(self):
        """Test direct execution methods."""
        with patch("openalex.entities.OpenAlex") as mock_client_class:
            mock_client = Mock()
            mock_resource = Mock()
            mock_client_class.return_value = mock_client
            mock_client.works = mock_resource
            mock_resource.get.return_value = {"id": "W123"}
            mock_resource.random.return_value = {"id": "W789"}
            mock_resource.autocomplete.return_value = ListResult(
                meta={
                    "count": 0,
                    "db_response_time_ms": 1,
                    "page": 1,
                    "per_page": 25,
                },
                results=[],
            )
            works = Works()
            result = works.get("W123")
            assert result["id"] == "W123"
            mock_resource.get.assert_called_once_with("W123")
            random_work = works.random()
            assert random_work["id"] == "W789"
            works.autocomplete("climate")
            mock_resource.autocomplete.assert_called_once_with("climate")

    def test_config_propagation(self):
        """Test configuration is properly passed to client."""
        with patch("openalex.entities.OpenAlex") as mock_client_class:
            Works(email="test@example.com").list()
            mock_client_class.assert_called_with(
                config=None,
                email="test@example.com",
                api_key=None,
            )
            mock_client_class.reset_mock()
            Authors(api_key="test-key").list()
            mock_client_class.assert_called_with(
                config=None,
                email=None,
                api_key="test-key",
            )

    def test_aliases(self):
        """Test entity aliases work correctly."""
        from openalex import Journals, People

        assert People.resource_name == "authors"
        assert Journals.resource_name == "sources"

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager support."""
        with patch(
            "openalex.entities.AsyncOpenAlex"
        ) as mock_async_client_class:
            mock_async_client = AsyncMock()
            mock_async_client.__aenter__.return_value = mock_async_client
            mock_async_client.__aexit__.return_value = None
            mock_async_client_class.return_value = mock_async_client
            async with Works() as works:
                assert works is not None
            mock_async_client.__aenter__.assert_called_once()
            mock_async_client.__aexit__.assert_called_once()
