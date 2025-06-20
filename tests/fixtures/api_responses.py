"""Fixtures for mocked API responses."""

from datetime import datetime, timedelta
from typing import Any


class APIResponseFixtures:
    """Container for API response fixtures."""

    @staticmethod
    def work_response(work_id: str = "W2755950973") -> dict[str, Any]:
        """Create a realistic work response."""
        return {
            "id": f"https://openalex.org/{work_id}",
            "doi": "https://doi.org/10.1103/physrevlett.118.091101",
            "display_name": (
                "GW170104: Observation of a 50-Solar-Mass Binary Black Hole Coalescence at Redshift 0.2"
            ),
            "publication_year": 2017,
            "publication_date": "2017-06-01",
            "type": "article",
            "cited_by_count": 850,
            "is_retracted": False,
            "is_paratext": False,
            "open_access": {
                "is_oa": True,
                "oa_status": "gold",
                "oa_url": (
                    "https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.118.221101"
                ),
                "any_repository_has_fulltext": True,
            },
            "authorships": [
                {
                    "author_position": "first",
                    "author": {
                        "id": "https://openalex.org/A2150889177",
                        "display_name": "B. P. Abbott",
                        "orcid": None,
                    },
                    "institutions": [
                        {
                            "id": "https://openalex.org/I157725225",
                            "display_name": "California Institute of Technology",
                            "ror": "https://ror.org/05dxps055",
                            "country_code": "US",
                            "type": "education",
                        }
                    ],
                    "raw_affiliation_strings": [
                        "LIGO, California Institute of Technology, Pasadena, CA 91125, USA"
                    ],
                }
            ],
            "locations": [
                {
                    "is_primary": True,
                    "source": {
                        "id": "https://openalex.org/S16175027",
                        "display_name": "Physical Review Letters",
                        "issn_l": "0031-9007",
                        "is_oa": False,
                        "is_in_doaj": False,
                    },
                }
            ],
            "primary_location": {
                "is_primary": True,
                "source": {
                    "id": "https://openalex.org/S16175027",
                    "display_name": "Physical Review Letters",
                    "issn_l": "0031-9007",
                    "is_oa": False,
                    "is_in_doaj": False,
                },
            },
            "referenced_works": [
                "https://openalex.org/W2126385722",
                "https://openalex.org/W2170499123",
            ],
            "referenced_works_count": 95,
            "related_works": [
                "https://openalex.org/W2755951606",
                "https://openalex.org/W2736953509",
            ],
            "counts_by_year": [
                {"year": 2023, "cited_by_count": 125},
                {"year": 2022, "cited_by_count": 143},
                {"year": 2021, "cited_by_count": 156},
            ],
            "updated_date": "2023-08-01T00:00:00",
        }

    @staticmethod
    def author_response(author_id: str = "A2150889177") -> dict[str, Any]:
        """Create a realistic author response."""
        return {
            "id": f"https://openalex.org/{author_id}",
            "orcid": "https://orcid.org/0000-0002-3666-1234",
            "display_name": "B. P. Abbott",
            "display_name_alternatives": [
                "Barry P. Abbott",
                "B.P. Abbott",
                "Abbott, B.P.",
            ],
            "works_count": 523,
            "cited_by_count": 28451,
            "last_known_institution": {
                "id": "https://openalex.org/I157725225",
                "display_name": "California Institute of Technology",
                "ror": "https://ror.org/05dxps055",
                "country_code": "US",
                "type": "education",
            },
            "counts_by_year": [
                {"year": 2023, "works_count": 15, "cited_by_count": 2150},
                {"year": 2022, "works_count": 18, "cited_by_count": 2543},
            ],
            "updated_date": "2023-08-01T00:00:00",
        }

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
