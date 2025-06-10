"""Shared fixtures for resource tests."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def sample_filters() -> dict[str, Any]:
    """Common filter scenarios for testing."""
    return {
        "simple": {"is_oa": True},
        "complex": {
            "publication_year": [2020, 2021, 2022],
            "type": "article",
            "is_oa": True,
            "cited_by_count": ">100",
        },
        "negation": {"is_oa": False, "type": "!article"},
        "range": {"publication_year": "2020-2022", "cited_by_count": "10-100"},
        "search_and_filter": {
            "search": "machine learning",
            "filter": {"publication_year": 2023},
        },
    }


@pytest.fixture
def error_scenarios() -> dict[str, dict[str, Any]]:
    """Common error scenarios for testing."""
    return {
        "not_found": {"status": 404, "message": "Resource not found"},
        "rate_limit": {"status": 429, "retry_after": "60"},
        "server_error": {"status": 500, "message": "Internal server error"},
        "bad_request": {"status": 400, "message": "Invalid filter parameter"},
        "auth_error": {"status": 401, "message": "Invalid API key"},
        "timeout": {"type": "timeout", "message": "Request timed out"},
        "network": {"type": "network", "message": "Network error"},
    }


@pytest.fixture
def pagination_scenarios() -> dict[str, dict[str, Any]]:
    """Pagination test scenarios."""
    return {
        "basic": {"page": 1, "per_page": 25, "total": 100},
        "cursor": {
            "cursor": "*",
            "per_page": 200,
            "total": 50000,
            "next_cursor": "encoded_cursor_string",
        },
        "last_page": {"page": 4, "per_page": 25, "total": 100},
        "empty": {"page": 1, "per_page": 25, "total": 0},
        "single_item": {"page": 1, "per_page": 25, "total": 1},
    }
