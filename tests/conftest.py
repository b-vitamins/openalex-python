"""Pytest configuration and fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from httpx import Response

from openalex import OpenAlexConfig


@pytest.fixture
def config() -> OpenAlexConfig:
    """Create test configuration."""
    return OpenAlexConfig(
        email="test@example.com",
        retry_count=0,  # Disable retries in tests
        timeout=5.0,
    )


@pytest.fixture
def mock_work_response() -> dict[str, Any]:
    """Mock work API response."""
    return {
        "id": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.1103/physrevlett.77.3865",
        "title": "Generalized Gradient Approximation Made Simple",
        "display_name": "Generalized Gradient Approximation Made Simple",
        "publication_year": 1996,
        "publication_date": "1996-10-28",
        "type": "article",
        "cited_by_count": 50000,
        "is_retracted": False,
        "is_paratext": False,
        "institution_assertions": [],
        "open_access": {
            "is_oa": True,
            "oa_status": "bronze",
            "oa_url": "https://example.com/paper.pdf",
        },
        "authorships": [
            {
                "author_position": "first",
                "author": {
                    "id": "https://openalex.org/A123456",
                    "display_name": "John P. Perdew",
                    "orcid": "https://orcid.org/0000-0003-4237-824X",
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I456789",
                        "display_name": "Tulane University",
                        "ror": "https://ror.org/04v7hvq31",
                        "country_code": "US",
                        "type": "education",
                    }
                ],
                "countries": ["US"],
                "is_corresponding": True,
                "affiliations": [
                    {
                        "raw_affiliation_string": "Tulane University",
                        "institution_ids": ["https://openalex.org/I456789"],
                    }
                ],
            }
        ],
        "counts_by_year": [
            {"year": 2023, "cited_by_count": 2500},
            {"year": 2022, "cited_by_count": 2400},
        ],
        "created_date": "2016-06-24",
        "ids": {
            "openalex": "https://openalex.org/W2741809807",
            "doi": "https://doi.org/10.1103/physrevlett.77.3865",
            "pmid": "https://pubmed.ncbi.nlm.nih.gov/10062328",
            "pmcid": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567",
            "mag": "2741809807",
        },
    }


@pytest.fixture
def mock_author_response() -> dict[str, Any]:
    """Mock author API response."""
    return {
        "id": "https://openalex.org/A123456",
        "display_name": "John P. Perdew",
        "orcid": "https://orcid.org/0000-0003-4237-824X",
        "works_count": 500,
        "cited_by_count": 100000,
        "summary_stats": {
            "2yr_mean_citedness": 5.2,
            "h_index": 120,
            "i10_index": 450,
        },
        "affiliations": [
            {
                "institution": {
                    "id": "https://openalex.org/I456789",
                    "display_name": "Tulane University",
                    "ror": "https://ror.org/04v7hvq31",
                    "country_code": "US",
                    "type": "education",
                },
                "years": [2020, 2021, 2022, 2023],
            }
        ],
        "counts_by_year": [
            {"year": 2023, "works_count": 10, "cited_by_count": 5000},
            {"year": 2022, "works_count": 8, "cited_by_count": 4800},
        ],
        "created_date": "2023-01-01",
        "updated_date": "2024-01-01T00:00:00.000000",
        "ids": {
            "openalex": "https://openalex.org/A123456",
            "orcid": "https://orcid.org/0000-0003-4237-824X",
            "scopus": "6701655816",
        },
    }


@pytest.fixture
def mock_list_response(mock_work_response: dict[str, Any]) -> dict[str, Any]:
    """Mock list API response."""
    return {
        "meta": {
            "count": 100,
            "db_response_time_ms": 25,
            "page": 1,
            "per_page": 25,
        },
        "results": [mock_work_response],
        "group_by": None,
    }


@pytest.fixture
def mock_autocomplete_response() -> dict[str, Any]:
    """Mock autocomplete API response."""
    return {
        "meta": {
            "count": 3,
            "db_response_time_ms": 10,
            "page": 1,
            "per_page": 25,
        },
        "results": [
            {
                "id": "https://openalex.org/W2741809807",
                "display_name": "Generalized Gradient Approximation Made Simple",
                "entity_type": "work",
                "cited_by_count": 50000,
                "works_count": None,
            },
            {
                "id": "https://openalex.org/A123456",
                "display_name": "John P. Perdew",
                "entity_type": "author",
                "cited_by_count": 100000,
                "works_count": 500,
            },
        ],
    }


@pytest.fixture
def mock_error_response() -> dict[str, Any]:
    """Mock error API response."""
    return {
        "error": "Bad Request",
        "message": "Invalid filter parameter",
    }


# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


def load_json_fixture(filename: str) -> dict[str, Any]:
    """Load JSON fixture from test data directory."""
    path = TEST_DATA_DIR / filename
    if path.exists():
        return json.loads(path.read_text())
    return {}


class MockHTTPXClient:
    """Mock HTTPX client for testing."""

    def __init__(self, responses: dict[str, Any]) -> None:
        """Initialize with canned responses."""
        self.responses = responses
        self.requests: list[tuple[str, str, dict[str, Any]]] = []

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        """Mock request method."""
        self.requests.append((method, url, params or {}))

        # Find matching response
        for pattern, response_data in self.responses.items():
            if pattern in url:
                return Response(
                    status_code=200,
                    json=response_data,
                    headers={"content-type": "application/json"},
                )

        # Default 404
        return Response(
            status_code=404,
            json={"error": "Not Found", "message": "Resource not found"},
        )
