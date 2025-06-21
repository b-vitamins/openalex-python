"""Fixtures for mocked API responses."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class APIResponseFixtures:
    """Container for API response fixtures."""

    @staticmethod
    def _load_fixture(filename: str) -> dict[str, Any]:
        """Load fixture data from JSON file."""
        fixture_path = Path(__file__).parent / "data" / filename
        with fixture_path.open() as f:
            return json.load(f)

    @staticmethod
    def work_response(work_id: str = "W2755950973") -> dict[str, Any]:
        """Create a realistic work response."""
        data = APIResponseFixtures._load_fixture("W-api-response.json")
        data["id"] = f"https://openalex.org/{work_id}"
        return data

    @staticmethod
    def author_response(author_id: str = "A2150889177") -> dict[str, Any]:
        """Create a realistic author response."""
        data = APIResponseFixtures._load_fixture("A-api-response.json")
        data["id"] = f"https://openalex.org/{author_id}"
        return data

    @staticmethod
    def search_response(
        query: str, page: int = 1, per_page: int = 25
    ) -> dict[str, Any]:
        """Create a search response with pagination."""
        total_results = 150  # Simulate 150 total results
        results = []
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_results)

        for i in range(start_idx, end_idx):
            results.append(
                {
                    "id": f"https://openalex.org/W{1000000 + i}",
                    "display_name": f"Result {i + 1} for query: {query}",
                    "publication_year": 2020 + (i % 4),
                    "cited_by_count": 100 - i,
                    "type": "article" if i % 3 != 0 else "preprint",
                }
            )

        return {
            "meta": {
                "count": total_results,
                "db_response_time_ms": 42,
                "page": page,
                "per_page": per_page,
            },
            "results": results,
            "group_by": [],
        }

    @staticmethod
    def group_by_response(field: str) -> dict[str, Any]:
        """Create a group-by response."""
        groups: list[dict[str, Any]] = []

        if field == "publication_year":
            for year in range(2020, 2024):
                groups.append(
                    {
                        "key": str(year),
                        "key_display_name": str(year),
                        "count": 1000 - (year - 2020) * 100,
                    }
                )
        elif field == "open_access.is_oa":
            groups = [
                {
                    "key": "true",
                    "key_display_name": "Open Access",
                    "count": 6543,
                },
                {
                    "key": "false",
                    "key_display_name": "Closed Access",
                    "count": 3457,
                },
            ]
        elif field == "type":
            groups = [
                {
                    "key": "article",
                    "key_display_name": "Article",
                    "count": 7500,
                },
                {
                    "key": "preprint",
                    "key_display_name": "Preprint",
                    "count": 1500,
                },
                {
                    "key": "book",
                    "key_display_name": "Book",
                    "count": 1000,
                },
            ]

        return {
            "meta": {
                "count": sum(g["count"] for g in groups),
                "db_response_time_ms": 35,
                "page": 1,
                "per_page": 200,
            },
            "results": [],
            "group_by": groups,
        }

    @staticmethod
    def error_response(
        status_code: int, error_type: str = "Bad Request"
    ) -> dict[str, Any]:
        """Create an error response."""
        messages = {
            400: "Invalid filter parameter",
            401: "Invalid API key",
            403: "Access forbidden",
            404: "Entity not found",
            429: "Rate limit exceeded",
            500: "Internal server error",
            503: "Service temporarily unavailable",
        }

        return {
            "error": error_type,
            "message": messages.get(status_code, "Unknown error"),
            "status_code": status_code,
        }

    @staticmethod
    def rate_limit_headers(
        remaining: int = 0, reset_time: int | None = None
    ) -> dict[str, str]:
        """Create rate limit headers."""
        if reset_time is None:
            reset_time = int(
                (datetime.now() + timedelta(seconds=60)).timestamp()
            )

        headers: dict[str, str] = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }
        if remaining == 0:
            headers["Retry-After"] = "60"
        return headers
