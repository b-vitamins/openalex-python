"""Test the new template classes for DRY implementation."""

import pytest
from unittest.mock import Mock, patch
from openalex.templates import (
    SyncEntityTemplate,
    AsyncEntityTemplate,
    EntityLogicBase,
)
from openalex.models import BaseFilter, Work
from openalex.config import OpenAlexConfig


class DummySyncEntity(SyncEntityTemplate[Work, BaseFilter]):
    """Test entity using sync template."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = "works"
        self.model_class = Work


class DummyAsyncEntity(AsyncEntityTemplate[Work, BaseFilter]):
    """Test entity using async template."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = "works"
        self.model_class = Work


class TestEntityLogicBase:
    """Test shared business logic base class."""

    def test_base_logic_initialization(self):
        """Test that base logic initializes correctly."""
        config = OpenAlexConfig()
        logic = EntityLogicBase[Work, BaseFilter](config=config)

        assert logic._config == config
        assert logic.endpoint == ""
        assert logic.model_class is None

    def test_build_url_basic(self):
        """Test URL building functionality."""
        logic = EntityLogicBase[Work, BaseFilter]()
        logic.endpoint = "works"

        url = logic._build_url()
        assert url.endswith("/works")

    def test_build_url_with_path(self):
        """Test URL building with path."""
        logic = EntityLogicBase[Work, BaseFilter]()
        logic.endpoint = "works"

        url = logic._build_url("W123456")
        assert url.endswith("/works/W123456")

    def test_normalize_and_validate_id(self):
        """Test ID normalization and validation."""
        logic = EntityLogicBase[Work, BaseFilter]()
        logic.endpoint = "works"

        # Mock the validation function
        with patch("openalex.templates.validate_entity_id") as mock_validate:
            mock_validate.return_value = "W123456"

            result = logic._normalize_and_validate_id("W123456")

            assert result == "W123456"
            mock_validate.assert_called_once_with("W123456", "work")

    def test_parse_response(self, mock_work_data):
        """Test response parsing."""
        logic = EntityLogicBase[Work, BaseFilter]()
        logic.model_class = Work

        parsed = logic._parse_response(mock_work_data)

        assert isinstance(parsed, Work)
        assert parsed.id == mock_work_data["id"]

    def test_parse_list_response(self, mock_work_data):
        """Test list response parsing."""
        logic = EntityLogicBase[Work, BaseFilter]()
        logic.model_class = Work

        list_data = {"results": [mock_work_data], "meta": {"count": 1}}

        result = logic._parse_list_response(list_data)

        assert len(result.results) == 1
        assert isinstance(result.results[0], Work)
        assert result.meta.count == 1


class TestSyncEntityTemplate:
    """Test synchronous entity template."""

    @patch("openalex.connection.get_connection")
    def test_sync_template_initialization(self, mock_get_connection):
        """Test that sync template initializes correctly."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummySyncEntity()

        assert entity._connection == mock_connection
        assert entity.endpoint == "works"
        assert entity.model_class == Work

    @patch("openalex.connection.get_connection")
    def test_execute_request(self, mock_get_connection):
        """Test HTTP request execution."""
        mock_connection = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_connection.request.return_value = mock_response
        mock_get_connection.return_value = mock_connection

        entity = DummySyncEntity()

        with patch("openalex.templates.raise_for_status"):
            result = entity._execute_request("http://test.com", {})

        assert result == {"test": "data"}
        mock_connection.request.assert_called_once()

    @patch("openalex.connection.get_connection")
    @patch("openalex.templates.get_cache_manager")
    def test_get_single_entity(
        self, mock_get_cache, mock_get_connection, mock_work_data
    ):
        """Test getting a single entity."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        mock_cache = Mock()
        mock_cache.get_or_fetch.return_value = mock_work_data
        mock_get_cache.return_value = mock_cache

        entity = DummySyncEntity()

        with patch.object(
            entity, "_normalize_and_validate_id", return_value="W123"
        ):
            result = entity._get_single_entity("W123")

        assert isinstance(result, Work)
        mock_cache.get_or_fetch.assert_called_once()

    @patch("openalex.connection.get_connection")
    def test_query_creation(self, mock_get_connection):
        """Test query object creation."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummySyncEntity()

        with patch("openalex.query.Query") as mock_query_class:
            mock_query = Mock()
            mock_query_class.return_value = mock_query

            result = entity.query()

            assert result == mock_query
            mock_query_class.assert_called_once_with(entity, {})


@pytest.mark.asyncio
class TestAsyncEntityTemplate:
    """Test asynchronous entity template."""

    @patch("openalex.connection.get_async_connection")
    async def test_async_template_initialization(self, mock_get_connection):
        """Test that async template initializes correctly."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummyAsyncEntity()

        # Async connection is lazily loaded, so initially None
        assert entity._connection is None
        assert entity.endpoint == "works"
        assert entity.model_class == Work

        # After calling _get_connection, it should be set
        await entity._get_connection()
        assert entity._connection == mock_connection

    @patch("openalex.connection.get_async_connection")
    async def test_async_execute_request(self, mock_get_connection):
        """Test async HTTP request execution."""
        from unittest.mock import AsyncMock

        mock_connection = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_connection.request = AsyncMock(return_value=mock_response)
        mock_get_connection.return_value = mock_connection

        entity = DummyAsyncEntity()

        with patch("openalex.templates.raise_for_status"):
            result = await entity._execute_request("http://test.com", {})

        assert result == {"test": "data"}

    @patch("openalex.connection.get_async_connection")
    async def test_async_get_single_entity(
        self, mock_get_connection, mock_work_data
    ):
        """Test getting a single entity asynchronously."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummyAsyncEntity()

        with patch.object(
            entity, "_normalize_and_validate_id", return_value="W123"
        ):
            with patch.object(
                entity, "_execute_request", return_value=mock_work_data
            ):
                result = await entity._get_single_entity("W123")

        assert isinstance(result, Work)

    @patch("openalex.connection.get_async_connection")
    async def test_async_query_creation(self, mock_get_connection):
        """Test async query object creation."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummyAsyncEntity()

        with patch("openalex.query.AsyncQuery") as mock_query_class:
            mock_query = Mock()
            mock_query_class.return_value = mock_query

            result = entity.query()

            assert result == mock_query
            mock_query_class.assert_called_once_with(
                entity, entity.model_class, entity._config
            )

    @patch("openalex.connection.get_async_connection")
    async def test_async_get_many(self, mock_get_connection, mock_work_data):
        """Test getting multiple entities asynchronously."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection

        entity = DummyAsyncEntity()

        with patch.object(
            entity,
            "_normalize_and_validate_id",
            side_effect=lambda x: x.upper(),
        ):
            with patch.object(
                entity,
                "_get_single_entity",
                return_value=Work.model_validate(mock_work_data),
            ):
                results = await entity.get_many(["w1", "w2"])

        assert len(results) == 2
        assert all(isinstance(r, Work) for r in results)


class TestTemplateComparison:
    """Test that templates provide equivalent functionality."""

    @patch("openalex.connection.get_connection")
    @patch("openalex.connection.get_async_connection")
    def test_sync_and_async_have_same_methods(
        self, mock_async_conn, mock_sync_conn
    ):
        """Test that sync and async templates have equivalent public methods."""
        mock_sync_conn.return_value = Mock()
        mock_async_conn.return_value = Mock()

        sync_entity = DummySyncEntity()
        async_entity = DummyAsyncEntity()

        # Get public methods (excluding private and dunder methods)
        sync_methods = {
            name
            for name in dir(sync_entity)
            if not name.startswith("_") and callable(getattr(sync_entity, name))
        }
        async_methods = {
            name
            for name in dir(async_entity)
            if not name.startswith("_")
            and callable(getattr(async_entity, name))
        }

        # Both should have the same set of public methods
        assert sync_methods == async_methods

    def test_shared_business_logic_methods(self):
        """Test that both templates inherit shared business logic."""
        sync_entity = DummySyncEntity()
        async_entity = DummyAsyncEntity()

        # Both should have inherited methods from EntityLogicBase
        shared_methods = [
            "_build_url",
            "_parse_response",
            "_parse_list_response",
            "_normalize_and_validate_id",
            "_prepare_params",
            "clear_cache",
            "cache_stats",
            "metrics",
        ]

        for method in shared_methods:
            assert hasattr(sync_entity, method)
            assert hasattr(async_entity, method)
            # Should be the same method implementation (from base class)
            assert (
                getattr(sync_entity, method).__func__
                == getattr(async_entity, method).__func__
            )
