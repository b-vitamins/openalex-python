import tracemalloc
from unittest.mock import AsyncMock, Mock, patch

import pytest

from openalex import AsyncWorks, Works


class TestStreaming:
    def test_streaming_yields_individual_items(self):
        works = Works()
        page1 = {
            "results": [
                {"id": "https://openalex.org/W1", "display_name": "W1"},
                {"id": "https://openalex.org/W2", "display_name": "W2"},
            ],
            "meta": {"count": 3, "page": 1, "per_page": 2, "next_cursor": "c2"},
        }
        page2 = {
            "results": [
                {"id": "https://openalex.org/W3", "display_name": "W3"}
            ],
            "meta": {"count": 3, "page": 2, "per_page": 1, "next_cursor": None},
        }
        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(status_code=200, json=Mock(return_value=page1)),
                Mock(status_code=200, json=Mock(return_value=page2)),
            ]
            query = works.filter(publication_year=2023)
            results = list(query.stream(per_page=2, max_results=3))

        assert len(results) == 3
        assert results[0].id.endswith("W1")
        assert results[2].id.endswith("W3")

    def test_memory_efficient_large_results(self):
        works = Works()
        responses = []
        for i in range(5):
            page = {
                "results": [
                    {
                        "id": f"https://openalex.org/W{i}",
                        "display_name": f"W{i}",
                    }
                ],
                "meta": {
                    "count": 5,
                    "page": i + 1,
                    "per_page": 1,
                    "next_cursor": "c" if i < 4 else None,
                },
            }
            responses.append(
                Mock(status_code=200, json=Mock(return_value=page))
            )

        with patch("httpx.Client.request", side_effect=responses):
            tracemalloc.start()
            count = 0
            for _ in works.filter(year=2023).stream(per_page=1, max_results=5):
                count += 1
                current, _ = tracemalloc.get_traced_memory()
                assert current < 5 * 1024 * 1024
            tracemalloc.stop()

        assert count == 5

    @pytest.mark.asyncio
    async def test_async_streaming_works(self):
        works = AsyncWorks()

        async def async_response(*args, **kwargs):
            cursor = kwargs["params"].get("cursor", "*")
            if cursor == "*":
                return Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "results": [
                                {
                                    "id": "https://openalex.org/W1",
                                    "display_name": "W1",
                                }
                            ],
                            "meta": {
                                "count": 2,
                                "page": 1,
                                "per_page": 1,
                                "next_cursor": "c2",
                            },
                        }
                    ),
                )
            return Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "results": [
                            {
                                "id": "https://openalex.org/W2",
                                "display_name": "W2",
                            }
                        ],
                        "meta": {
                            "count": 2,
                            "page": 2,
                            "per_page": 1,
                            "next_cursor": None,
                        },
                    }
                ),
            )

        with patch(
            "httpx.AsyncClient.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = async_response
            query = works.filter(publication_year=2023)
            paginator = await query.stream(per_page=1, max_results=2)
            count = 0
            async for work in paginator:
                count += 1
                assert work.id

        assert count == 2
