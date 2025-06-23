"""Test backwards compatibility of the refactored entity classes."""

import pytest
from unittest.mock import Mock, patch


# Test that the old API still works
def test_sync_entity_backwards_compatibility():
    """Test that sync entities maintain backwards compatibility."""
    from openalex import Works, Authors

    # Should be able to instantiate without issues
    works = Works()
    authors = Authors()

    # Should have the same public interface
    assert hasattr(works, "get")
    assert hasattr(works, "get_many")
    assert hasattr(works, "search")
    assert hasattr(works, "filter")
    assert hasattr(works, "query")
    assert hasattr(works, "autocomplete")
    assert hasattr(works, "random")
    assert hasattr(works, "clear_cache")
    assert hasattr(works, "cache_stats")
    assert hasattr(works, "warm_cache")
    assert hasattr(works, "metrics")

    # Works should have ngrams method
    assert hasattr(works, "ngrams")

    # Authors should not have ngrams method
    assert not hasattr(authors, "ngrams")


def test_async_entity_backwards_compatibility():
    """Test that async entities maintain backwards compatibility."""
    from openalex import AsyncWorks, AsyncAuthors

    # Should be able to instantiate without issues
    works = AsyncWorks()
    authors = AsyncAuthors()

    # Should have the same public interface
    assert hasattr(works, "get")
    assert hasattr(works, "get_many")
    assert hasattr(works, "search")
    assert hasattr(works, "filter")
    assert hasattr(works, "query")
    assert hasattr(works, "autocomplete")
    assert hasattr(works, "random")
    assert hasattr(works, "clear_cache")
    assert hasattr(works, "cache_stats")
    assert hasattr(works, "warm_cache")
    assert hasattr(works, "metrics")

    # AsyncWorks should have ngrams method
    assert hasattr(works, "ngrams")

    # AsyncAuthors should not have ngrams method
    assert not hasattr(authors, "ngrams")


def test_old_import_paths_still_work():
    """Test that old import paths still work for backwards compatibility."""
    # These should not raise ImportError
    from openalex.entities import BaseEntity, AsyncBaseEntity
    from openalex.async_entities import AsyncWorks, AsyncAuthors

    # Should be able to create instances
    base = BaseEntity()
    async_base = AsyncBaseEntity()
    async_works = AsyncWorks()
    async_authors = AsyncAuthors()

    assert base is not None
    assert async_base is not None
    assert async_works is not None
    assert async_authors is not None


def test_legacy_function_compatibility():
    """Test that legacy utility functions still work."""
    from openalex.entities import _build_list_result
    from openalex.models import Work

    # Mock work data
    mock_data = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "title": "Test Work",
                "publication_year": 2023,
                "cited_by_count": 0,
                "display_name": "Test Work",
                "doi": "https://doi.org/10.1000/test123",
                "is_oa": False,
                "is_paratext": False,
                "is_retracted": False,
                "language": "en",
                "updated_date": "2023-01-01",
                "created_date": "2023-01-01",
            }
        ],
        "meta": {"count": 1, "page": 1, "per_page": 25},
    }

    result = _build_list_result(mock_data, Work)

    assert len(result.results) == 1
    assert isinstance(result.results[0], Work)
    assert result.results[0].id == "https://openalex.org/W123"
    assert result.meta.count == 1


@patch("openalex.connection.get_connection")
def test_sync_entity_uses_templates(mock_get_connection):
    """Test that sync entities are using the new template architecture."""
    from openalex import Works
    from openalex.templates import SyncEntityTemplate

    mock_connection = Mock()
    mock_get_connection.return_value = mock_connection

    works = Works()

    # Should be instance of the template
    assert isinstance(works, SyncEntityTemplate)
    assert works.endpoint == "works"
    assert works.model_class.__name__ == "Work"


@patch("openalex.connection.get_async_connection")
def test_async_entity_uses_templates(mock_get_async_connection):
    """Test that async entities are using the new template architecture."""
    from openalex import AsyncWorks
    from openalex.templates import AsyncEntityTemplate

    mock_connection = Mock()
    mock_get_async_connection.return_value = mock_connection

    works = AsyncWorks()

    # Should be instance of the template
    assert isinstance(works, AsyncEntityTemplate)
    assert works.endpoint == "works"
    assert works.model_class.__name__ == "Work"


def test_entity_endpoints_are_correct():
    """Test that all entities have correct endpoints set."""
    from openalex import (
        Works,
        Authors,
        Institutions,
        Sources,
        Topics,
        Publishers,
        Funders,
        Keywords,
        Concepts,
    )

    # Test sync entities
    assert Works().endpoint == "works"
    assert Authors().endpoint == "authors"
    assert Institutions().endpoint == "institutions"
    assert Sources().endpoint == "sources"
    assert Topics().endpoint == "topics"
    assert Publishers().endpoint == "publishers"
    assert Funders().endpoint == "funders"
    assert Keywords().endpoint == "keywords"
    assert Concepts().endpoint == "concepts"


def test_async_entity_endpoints_are_correct():
    """Test that all async entities have correct endpoints set."""
    from openalex import (
        AsyncWorks,
        AsyncAuthors,
        AsyncInstitutions,
        AsyncSources,
        AsyncTopics,
        AsyncPublishers,
        AsyncFunders,
        AsyncKeywords,
        AsyncConcepts,
    )

    # Test async entities
    assert AsyncWorks().endpoint == "works"
    assert AsyncAuthors().endpoint == "authors"
    assert AsyncInstitutions().endpoint == "institutions"
    assert AsyncSources().endpoint == "sources"
    assert AsyncTopics().endpoint == "topics"
    assert AsyncPublishers().endpoint == "publishers"
    assert AsyncFunders().endpoint == "funders"
    assert AsyncKeywords().endpoint == "keywords"
    assert AsyncConcepts().endpoint == "concepts"


def test_shared_logic_is_actually_shared():
    """Test that shared business logic is actually shared between sync/async."""
    from openalex import Works, AsyncWorks
    from openalex.templates import EntityLogicBase

    works = Works()
    async_works = AsyncWorks()

    # Both should inherit core methods from EntityLogicBase
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
        sync_method = getattr(works, method)
        async_method = getattr(async_works, method)

        # Should be the same method implementation (from base class)
        assert sync_method.__func__ == async_method.__func__, (
            f"Method {method} not shared"
        )
