"""Pytest configuration and fixtures for OpenAlex tests."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest
import requests

DATA_DIR = Path(__file__).parent / "fixtures" / "data"


def _load_data(filename: str) -> dict[str, Any]:
    """Load JSON fixture data."""
    with (DATA_DIR / filename).open(encoding="utf-8") as fh:
        return json.load(fh)


# Basic entity data fixtures -------------------------------------------------


@pytest.fixture
def mock_s137773608_data() -> dict[str, Any]:
    """Mock data for source S137773608."""
    return _load_data("S137773608.json")


@pytest.fixture
def mock_a5023888391_data() -> dict[str, Any]:
    """Mock data for author A5023888391."""
    return _load_data("A5023888391.json")


@pytest.fixture
def mock_i27837315_data() -> dict[str, Any]:
    """Mock data for institution I27837315."""
    return _load_data("I27837315.json")


@pytest.fixture
def mock_w2741809807_data() -> dict[str, Any]:
    """Mock data for work W2741809807."""
    return _load_data("W2741809807.json")


@pytest.fixture
def mock_c71924100_data() -> dict[str, Any]:
    """Mock data for concept C71924100."""
    return _load_data("C71924100.json")


@pytest.fixture
def mock_t11636_data() -> dict[str, Any]:
    """Mock data for topic T11636."""
    return _load_data("T11636.json")


@pytest.fixture
def mock_cardiac_imaging_data() -> dict[str, Any]:
    """Mock data for keyword cardiac-imaging."""
    return _load_data("cardiac-imaging.json")


@pytest.fixture
def mock_p4310319965_data() -> dict[str, Any]:
    """Mock data for publisher P4310319965."""
    return _load_data("P4310319965.json")


@pytest.fixture
def mock_f4320332161_data() -> dict[str, Any]:
    """Mock data for funder F4320332161."""
    return _load_data("F4320332161.json")


# Common fixtures for API mocking -------------------------------------------


@pytest.fixture
def mock_http_get():
    """Mock HTTP GET requests without external dependencies."""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_api_response():
    """Create mock API response objects."""

    def create_response(
        json_data: Any | None = None,
        status_code: int = 200,
        text: str = "",
        headers: dict[str, str] | None = None,
    ):
        response = Mock()
        response.status_code = status_code
        response.text = text
        response.headers = headers or {}
        response.json.return_value = json_data
        response.raise_for_status = Mock()
        if status_code >= 400:
            response.raise_for_status.side_effect = Exception(
                f"HTTP {status_code}"
            )
        return response

    return create_response


@pytest.fixture
def setup_mock_api(mock_http_get, mock_api_response):
    """Setup mock API responses for common endpoints."""

    def setup(responses_dict: dict[str, Any]):
        def side_effect(url: str, *args: Any, **kwargs: Any):
            for pattern, response_data in responses_dict.items():
                if pattern in url:
                    if isinstance(response_data, dict):
                        return mock_api_response(json_data=response_data)
                    if isinstance(response_data, int):
                        return mock_api_response(status_code=response_data)
                    return response_data
            return mock_api_response(status_code=404)

        mock_http_get.side_effect = side_effect
        return mock_http_get

    return setup


# Full entity data fixtures --------------------------------------------------


@pytest.fixture
def mock_work_data(mock_w2741809807_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock work data."""
    return mock_w2741809807_data


@pytest.fixture
def mock_author_data(mock_a5023888391_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock author data."""
    return mock_a5023888391_data


@pytest.fixture
def mock_institution_data(
    mock_i27837315_data: dict[str, Any],
) -> dict[str, Any]:
    """Comprehensive mock institution data."""
    return mock_i27837315_data


@pytest.fixture
def mock_source_data(mock_s137773608_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock source data."""
    return mock_s137773608_data


@pytest.fixture
def mock_publisher_data(
    mock_p4310319965_data: dict[str, Any],
) -> dict[str, Any]:
    """Comprehensive mock publisher data."""
    return mock_p4310319965_data


@pytest.fixture
def mock_funder_data(mock_f4320332161_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock funder data."""
    return mock_f4320332161_data


@pytest.fixture
def mock_topic_data(mock_t11636_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock topic data."""
    return mock_t11636_data


@pytest.fixture
def mock_concept_data(mock_c71924100_data: dict[str, Any]) -> dict[str, Any]:
    """Comprehensive mock concept data."""
    return mock_c71924100_data


@pytest.fixture
def mock_keyword_data(
    mock_cardiac_imaging_data: dict[str, Any],
) -> dict[str, Any]:
    """Comprehensive mock keyword data."""
    return mock_cardiac_imaging_data


# Entity-specific mock fixtures ---------------------------------------------


@pytest.fixture
def mock_work_entity(mock_work_data: dict[str, Any]):
    """Mock Work entity with methods."""
    mock = Mock()
    mock.id = mock_work_data["id"]
    mock.doi = mock_work_data["doi"]
    mock.title = mock_work_data["title"]
    mock.publication_year = mock_work_data["publication_year"]
    mock.cited_by_count = mock_work_data["cited_by_count"]
    mock.authorships = mock_work_data["authorships"]
    mock.to_dict.return_value = mock_work_data
    return mock


@pytest.fixture
def mock_author_entity(mock_author_data: dict[str, Any]):
    """Mock Author entity with methods."""
    mock = Mock()
    mock.id = mock_author_data["id"]
    mock.display_name = mock_author_data["display_name"]
    mock.orcid = mock_author_data.get("orcid")
    mock.works_count = mock_author_data["works_count"]
    mock.cited_by_count = mock_author_data["cited_by_count"]
    mock.to_dict.return_value = mock_author_data
    return mock


@pytest.fixture
def mock_institution_entity(mock_institution_data: dict[str, Any]):
    """Mock Institution entity with methods."""
    mock = Mock()
    mock.id = mock_institution_data["id"]
    mock.display_name = mock_institution_data["display_name"]
    mock.ror = mock_institution_data.get("ror")
    mock.country_code = mock_institution_data["country_code"]
    mock.type = mock_institution_data["type"]
    mock.works_count = mock_institution_data["works_count"]
    mock.to_dict.return_value = mock_institution_data
    return mock


@pytest.fixture
def mock_paginated_response():
    """Mock paginated API response structure."""

    def create_response(
        results: list[dict[str, Any]] | None = None,
        meta: dict[str, Any] | None = None,
        group_by: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if results is None:
            results = []
        if meta is None:
            meta = {
                "count": len(results),
                "db_response_time_ms": 23,
                "page": 1,
                "per_page": 25,
                "per_page_options": [25, 50, 100, 200],
                "group_count": None,
            }
        return {"results": results, "meta": meta, "group_by": group_by or []}

    return create_response


@pytest.fixture
def mock_api_client():
    """Mock OpenAlex API client."""
    client = Mock()
    client.base_url = "https://api.openalex.org"
    client.email = "test@example.com"
    client.api_key = None
    client.user_agent = "openalex-python"
    client.session = Mock()

    def mock_get(endpoint: str, params: dict[str, Any] | None = None):
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"results": [], "meta": {"count": 0}}
        return response

    client.get = mock_get
    return client


# Fixtures for testing different API endpoints -------------------------------


@pytest.fixture
def setup_all_api_mocks(
    setup_mock_api,
    mock_work_data,
    mock_author_data,
    mock_institution_data,
    mock_source_data,
    mock_paginated_response,
):
    """Setup common API mock calls."""
    base_url = "https://api.openalex.org"

    responses = {
        f"{base_url}/works/W2741809807": mock_work_data,
        f"{base_url}/authors/A5023888391": mock_author_data,
        f"{base_url}/institutions/I27837315": mock_institution_data,
        f"{base_url}/sources/S137773608": mock_source_data,
        f"{base_url}/works?": mock_paginated_response([mock_work_data]),
        f"{base_url}/authors?": mock_paginated_response([mock_author_data]),
        f"{base_url}/institutions?": mock_paginated_response(
            [mock_institution_data]
        ),
        f"{base_url}/sources?": mock_paginated_response([mock_source_data]),
    }

    return setup_mock_api(responses)


# Fixtures for testing edge cases -------------------------------------------


@pytest.fixture
def mock_empty_response() -> dict[str, Any]:
    """Mock empty API response."""
    return {
        "results": [],
        "meta": {
            "count": 0,
            "db_response_time_ms": 15,
            "page": 1,
            "per_page": 25,
        },
        "group_by": [],
    }


@pytest.fixture
def mock_error_response() -> dict[str, Any]:
    """Mock API error response."""
    return {"error": "Bad Request", "message": "Invalid filter specified"}


@pytest.fixture
def mock_rate_limit_response() -> dict[str, Any]:
    """Mock rate limit response."""
    return {
        "error": "Too Many Requests",
        "message": "Rate limit exceeded. Please retry after 60 seconds.",
    }


@pytest.fixture
def mock_not_found_response() -> dict[str, Any]:
    """Mock 404 not found response."""
    return {"error": "Not Found", "message": "Entity not found"}


# Utility fixtures ----------------------------------------------------------


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Temporary directory for cache testing."""
    cache_dir = tmp_path / "openalex_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


@pytest.fixture
def mock_datetime_now():
    """Mock datetime.now() for consistent testing."""
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
        mock_dt.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt


# Configuration fixtures ----------------------------------------------------


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    config = Mock()
    config.api_key = "test-api-key"
    config.email = "test@example.com"
    config.user_agent = "openalex-python-tests"
    config.retries = 3
    config.retry_backoff_factor = 0.1
    config.retry_status_codes = [429, 500, 502, 503, 504]
    config.timeout = 30
    return config


@pytest.fixture
def mock_session():
    """Mock requests session."""
    session = Mock()
    session.get = Mock()
    session.post = Mock()
    session.headers = {}
    return session


# Helper fixtures for common test patterns ---------------------------------


@pytest.fixture
def mock_http_response():
    """Create mock HTTP responses with consistent structure."""

    def create_response(
        json_data: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> Mock:
        response = Mock()
        response.status_code = status_code
        response.headers = headers or {}

        if json_data is not None:
            response.json.return_value = json_data
        else:
            response.json.side_effect = Exception("No JSON data")

        if status_code >= 400:
            response.raise_for_status.side_effect = Exception(
                f"HTTP {status_code}"
            )
        else:
            response.raise_for_status.return_value = None

        return response

    return create_response


@pytest.fixture
def mock_entity_factory():
    """Factory for creating test entities with overrides."""

    def create_entity(
        entity_type: str, entity_id: str | None = None, **overrides: Any
    ) -> dict[str, Any]:
        """Create entity data with defaults and overrides."""
        base_data = {
            "work": {
                "id": f"https://openalex.org/W{entity_id or '12345'}",
                "doi": "https://doi.org/10.1000/test",
                "display_name": "Test Work",
                "publication_year": 2023,
                "cited_by_count": 10,
                "type": "article",
            },
            "author": {
                "id": f"https://openalex.org/A{entity_id or '12345'}",
                "display_name": "Test Author",
                "orcid": None,
                "works_count": 5,
                "cited_by_count": 50,
            },
            "institution": {
                "id": f"https://openalex.org/I{entity_id or '12345'}",
                "display_name": "Test Institution",
                "ror": None,
                "country_code": "US",
                "type": "education",
                "works_count": 100,
            },
            "source": {
                "id": f"https://openalex.org/S{entity_id or '12345'}",
                "display_name": "Test Source",
                "issn_l": "1234-5678",
                "is_oa": False,
                "works_count": 200,
            },
            "funder": {
                "id": f"https://openalex.org/F{entity_id or '12345'}",
                "display_name": "Test Funder",
                "grants_count": 50,
                "works_count": 100,
            },
        }

        if entity_type not in base_data:
            msg = f"Unsupported entity type: {entity_type}"
            raise ValueError(msg)

        data = base_data[entity_type].copy()
        data.update(overrides)
        return data

    return create_entity


@pytest.fixture
def assert_valid_openalex_id():
    """Helper to assert valid OpenAlex ID format."""

    def assert_id(entity_id: str, entity_type: str) -> None:
        prefixes = {
            "work": "W",
            "author": "A",
            "institution": "I",
            "source": "S",
            "publisher": "P",
            "funder": "F",
            "topic": "T",
            "concept": "C",
            "keyword": "keywords/",
        }
        prefix = prefixes.get(entity_type)
        if prefix and prefix != "keywords/":
            assert entity_id.startswith(f"https://openalex.org/{prefix}")
        elif prefix == "keywords/":
            assert "/keywords/" in entity_id
        else:
            assert entity_id.startswith("https://openalex.org/")

    return assert_id


@pytest.fixture
def sample_filter_params() -> dict[str, str]:
    """Sample filter parameters for testing."""
    return {
        "display_name.search": "climate change",
        "publication_year": ">2020",
        "is_oa": "true",
        "type": "article",
        "institutions.country_code": "US",
    }


@pytest.fixture
def sample_search_params() -> dict[str, Any]:
    """Sample search parameters for testing."""
    return {
        "page": 1,
        "per_page": 25,
        "filter": "display_name.search:machine learning",
        "sort": "cited_by_count:desc",
        "sample": 100,
        "seed": 42,
    }


@pytest.fixture(autouse=True)
def _reset_global_state():
    """Ensure cache and connection state do not leak between tests."""
    from openalex.cache.manager import (
        clear_cache,
        _cache_managers,
        get_cache_manager as original_get_cache_manager,
    )
    from openalex.api import _connection_pool
    from openalex.metrics.utils import _metrics_collectors

    import openalex.cache.manager
    import openalex.entities

    if not hasattr(_reset_global_state, "_original_get_cache_manager"):
        _reset_global_state._original_get_cache_manager = (
            original_get_cache_manager
        )

    openalex.cache.manager.get_cache_manager = (
        _reset_global_state._original_get_cache_manager
    )
    openalex.entities.get_cache_manager = (
        _reset_global_state._original_get_cache_manager
    )

    clear_cache()
    _cache_managers.clear()
    _connection_pool.clear()
    _metrics_collectors.clear()
    yield
    clear_cache()
    _cache_managers.clear()
    _connection_pool.clear()
    _metrics_collectors.clear()


# Network blocking fixture (moved from helpers/network.py to avoid pytest assertion rewrite warnings)


class NetworkAccessError(RuntimeError):
    """Raised when a test attempts to access the real network."""


# Synchronous and asynchronous blockers


def _fail(*_args: Any, **_kwargs: Any) -> None:
    raise NetworkAccessError("Network access blocked during tests")


async def _async_fail(*_args: Any, **_kwargs: Any) -> None:
    raise NetworkAccessError("Network access blocked during tests")


@pytest.fixture(autouse=True)
def no_network(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    """Disable outbound network access unless a test uses ``requires_api``."""

    if "requires_api" in request.keywords:
        yield
        return

    monkeypatch.setattr(requests, "get", _fail)
    monkeypatch.setattr(requests, "post", _fail)
    monkeypatch.setattr(httpx.Client, "request", _fail)
    monkeypatch.setattr(httpx.Client, "send", _fail)
    monkeypatch.setattr(httpx.AsyncClient, "request", _async_fail)
    monkeypatch.setattr(httpx.AsyncClient, "send", _async_fail)
    yield
