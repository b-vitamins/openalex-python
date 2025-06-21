"""Performance benchmarks for OpenAlex client."""

import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("pytest_benchmark")

from openalex import Works
from openalex.cache.memory import MemoryCache
from openalex.models import Work
from tests.fixtures.api_responses import APIResponseFixtures


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.fixture
    def mock_fast_api(self):
        """Mock API with consistent fast response times."""
        fixtures = APIResponseFixtures()

        def mock_get(*_args: Any, **_kwargs: Any) -> Mock:
            time.sleep(0.05)
            return Mock(
                json=lambda: fixtures.work_response(),
                status_code=200,
            )

        mock_client = Mock()
        mock_client.get = mock_get
        return mock_client

    @pytest.mark.benchmark
    def test_single_request_performance(self, mock_fast_api, benchmark):
        """Benchmark single API request."""
        with patch("httpx.Client.get", return_value=mock_fast_api.get()):
            result = benchmark(lambda: Works()["W2755950973"])
            assert result.id is not None

    @pytest.mark.benchmark
    def test_cache_performance(self, mock_fast_api, benchmark):
        """Benchmark cache hit vs miss performance."""
        cache = MemoryCache()

        with (
            patch("httpx.Client.get", return_value=mock_fast_api.get()),
            patch(
                "openalex.cache.manager.get_cache_manager", return_value=cache
            ),
        ):
            Works()["W2755950973"]

            def cache_hit() -> Work:
                return Works()["W2755950973"]

            result = benchmark(cache_hit)
            assert result.id is not None

    @pytest.mark.benchmark
    def test_filter_building_performance(self, benchmark):
        """Benchmark query filter building."""

        def build_complex_filter():
            return (
                Works()
                .search("machine learning")
                .filter(publication_year=2023)
                .filter(is_open_access=True)
                .filter(institutions={"country_code": "US"})
                .filter(type="article")
                .filter(has_doi=True)
                .sort(cited_by_count="desc")
                .select(["id", "display_name", "doi", "publication_year"])
            )

        query = benchmark(build_complex_filter)
        filters = query.params.get("filter", {})
        assert query.params.get("search") == "machine learning"
        assert len(filters) >= 5

    @pytest.mark.benchmark
    def test_response_parsing_performance(self, benchmark):
        """Benchmark response parsing performance."""
        fixtures = APIResponseFixtures()
        large_response = {
            "meta": {"count": 1000, "page": 1, "per_page": 100},
            "results": [fixtures.work_response() for _ in range(100)],
        }

        def parse_response():
            from openalex.models import Work

            return [Work(**item) for item in large_response["results"]]

        results = benchmark(parse_response)
        assert len(results) == 100
        assert all(isinstance(w, Work) for w in results)
