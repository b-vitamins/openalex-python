"""Configuration for documentation tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import json


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--docs",
        action="store_true",
        default=False,
        help="Run documentation tests",
    )
    parser.addoption(
        "--no-mock-api",
        action="store_true",
        default=False,
        help="Run documentation tests with real API calls",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "docs: mark test as documentation test")

    if config.getoption("--docs"):
        config.option.markexpr = ""


def pytest_collection_modifyitems(config, items):
    """Skip docs tests unless --docs flag is used."""
    if config.getoption("--docs"):
        return

    skip_docs = pytest.mark.skip(reason="need --docs option to run")
    for item in items:
        if "docs" in item.keywords:
            item.add_marker(skip_docs)


@pytest.fixture
def mock_api_responses(request, monkeypatch):
    """Mock API responses unless --no-mock-api is used."""
    if request.config.getoption("--no-mock-api"):
        yield
        return

    test_data = {
        "work": {
            "id": "W2741809807",
            "title": "The structure of scientific revolutions",
            "publication_year": 1962,
            "cited_by_count": 50000,
            "type": "book",
            "doi": "https://doi.org/10.7208/chicago/9780226458106.001.0001",
            "open_access": {"is_oa": True, "oa_status": "green"},
            "authorships": [
                {
                    "author": {"id": "A5023888391", "display_name": "Thomas S. Kuhn"},
                    "author_position": "first",
                    "institutions": [],
                }
            ],
            "referenced_works": [],
            "topics": [],
            "abstract": None,
        },
        "author": {
            "id": "A5023888391",
            "display_name": "Thomas S. Kuhn",
            "orcid": "https://orcid.org/0000-0000-0000-0000",
            "works_count": 50,
            "cited_by_count": 100000,
            "last_known_institution": {
                "id": "I44113856",
                "display_name": "Massachusetts Institute of Technology",
            },
            "summary_stats": {"h_index": 25, "i10_index": 40},
        },
        "institution": {
            "id": "I136199984",
            "display_name": "Harvard University",
            "country_code": "US",
            "type": "education",
            "works_count": 500000,
            "cited_by_count": 10000000,
            "geo": {
                "city": "Cambridge",
                "region": "Massachusetts",
                "country": "United States",
                "country_code": "US",
                "latitude": 42.3736,
                "longitude": -71.1097,
            },
        },
        "source": {
            "id": "S137773608",
            "display_name": "Nature",
            "type": "journal",
            "issn": ["0028-0836", "1476-4687"],
            "is_oa": False,
            "works_count": 300000,
            "cited_by_count": 50000000,
            "summary_stats": {
                "two_year_mean_citedness": 42.0,
                "h_index": 1096,
                "i10_index": 100000,
            },
            "host_organization": "Springer Nature",
            "host_organization_name": "Springer Nature",
        },
        "topic": {
            "id": "T10017",
            "display_name": "Machine Learning",
            "works_count": 500000,
            "cited_by_count": 10000000,
            "description": "Study of algorithms that improve through experience",
            "keywords": ["artificial intelligence", "neural networks", "deep learning"],
            "domain": {"id": "D3", "display_name": "Physical Sciences"},
            "field": {"id": "F17", "display_name": "Computer Science"},
            "subfield": {"id": "S119", "display_name": "Artificial Intelligence"},
            "siblings": [],
        },
    }

    def mock_sync_request(self, method, url, **kwargs):
        """Mock synchronous HTTP requests."""
        parts = url.rstrip("/").split("/")

        if len(parts) >= 2 and parts[-2] in ["works", "authors", "institutions", "sources", "topics"]:
            entity_type = parts[-2]
            entity_id = parts[-1]

            if entity_type == "works" and entity_id == "W2741809807":
                return Mock(status_code=200, json=lambda: test_data["work"])
            if entity_type == "authors" and entity_id == "A5023888391":
                return Mock(status_code=200, json=lambda: test_data["author"])
            if entity_type == "institutions" and entity_id in ["I136199984", "I44113856"]:
                return Mock(status_code=200, json=lambda: test_data["institution"])
            if entity_type == "sources" and entity_id == "S137773608":
                return Mock(status_code=200, json=lambda: test_data["source"])
            if entity_type == "topics" and entity_id == "T10017":
                return Mock(status_code=200, json=lambda: test_data["topic"])

        if any(entity in url for entity in ["works", "authors", "institutions", "sources", "topics"]):
            params = kwargs.get("params", {})
            per_page = int(params.get("per-page", 25))
            page = int(params.get("page", 1))
            results = []
            for i in range(min(per_page, 5)):
                if "works" in url:
                    results.append(
                        {
                            "id": f"W{1000+i}",
                            "display_name": f"Example work {i+1}",
                            "title": f"Example work {i+1}",
                            "publication_year": 2023,
                            "cited_by_count": i * 10,
                            "relevance_score": round(1.0 - i * 0.1, 2),
                            "open_access": {"is_oa": True},
                        }
                    )
                elif "authors" in url:
                    results.append(
                        {
                            "id": f"A{1000+i}",
                            "display_name": f"Test Author {i+1}",
                            "works_count": 50 + i * 10,
                            "cited_by_count": 1000 + i * 100,
                        }
                    )
                elif "institutions" in url:
                    results.append(
                        {
                            "id": f"I{1000+i}",
                            "display_name": f"Institution {i+1}",
                            "works_count": 200 + i * 20,
                            "cited_by_count": 5000 + i * 500,
                        }
                    )
            return Mock(
                status_code=200,
                json=lambda: {
                    "results": results,
                    "meta": {
                        "count": 100,
                        "db_response_time_ms": 50,
                        "page": page,
                        "per_page": per_page,
                    },
                    "group_by": [],
                },
            )

        return Mock(status_code=200, json=lambda: {"results": [], "meta": {"count": 0, "page": 1, "per_page": 25}})

    async def mock_async_request(self, method, url, **kwargs):
        return mock_sync_request(self, method, url, **kwargs)

    monkeypatch.setattr("httpx.Client.request", mock_sync_request)
    monkeypatch.setattr("httpx.AsyncClient.request", mock_async_request)
    yield
