"""Test cache performance and effectiveness."""

import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest

from openalex import Works
from openalex.cache.memory import MemoryCache
from tests.helpers.base import CachePatchingTestCase
from tests.fixtures.api_responses import APIResponseFixtures


@pytest.mark.integration
@pytest.mark.modifies_global_state
class TestCachePerformance(CachePatchingTestCase):
    """Test cache performance in integration scenarios."""

    @pytest.fixture
    def fixtures(self):
        return APIResponseFixtures()

    def test_cache_hit_performance(self, fixtures):
        """Test performance improvement from cache hits."""
        work_response = fixtures.work_response()

        with self.isolated_cache() as cache:
            with self.patch_cache_manager(cache=cache, cache_enabled=True):
                with patch("httpx.Client.request") as mock_request:
                    mock_request.return_value = Mock(
                        json=lambda: work_response, status_code=200
                    )
                    start = time.time()
                    Works()["W2755950973"]
                    first_time = time.time() - start

                    start = time.time()
                    Works()["W2755950973"]
                    second_time = time.time() - start

                    assert second_time < first_time
                    assert mock_request.call_count == 1

                    stats = cache.stats()
                    assert stats["hits"] >= 1
                    assert stats["misses"] >= 1

    def test_cache_with_filters(self, fixtures):
        """Test cache works correctly with different filter combinations."""
        search_response1 = fixtures.search_response("AI", page=1)
        search_response2 = fixtures.search_response("ML", page=1)

        with self.isolated_cache() as cache:
            with self.patch_cache_manager(cache=cache, cache_enabled=True):
                with patch("httpx.Client.request") as mock_request:
                    mock_request.side_effect = [
                        Mock(json=lambda: search_response1, status_code=200),
                        Mock(json=lambda: search_response2, status_code=200),
                        Mock(json=lambda: search_response1, status_code=200),
                    ]
                    results1 = (
                        Works().search("AI").filter(publication_year=2023).get()
                    )
                    results2 = (
                        Works().search("ML").filter(publication_year=2023).get()
                    )
                    results3 = (
                        Works().search("AI").filter(publication_year=2023).get()
                    )

                    assert (
                        results1.results[0].display_name
                        != results2.results[0].display_name
                    )
                    assert (
                        results1.results[0].display_name
                        == results3.results[0].display_name
                    )
                    assert mock_request.call_count == 2

    def test_cache_expiration(self, fixtures):
        """Test cache respects TTL."""
        work_response = fixtures.work_response()
        with self.isolated_cache() as short_ttl_cache:
            with self.patch_cache_manager(
                cache=short_ttl_cache, cache_enabled=True
            ):
                with patch("httpx.Client.request") as mock_request:
                    mock_request.return_value = Mock(
                        json=lambda: work_response, status_code=200
                    )
                    cache_key = "test_key"
                    short_ttl_cache.set(cache_key, work_response, ttl=0.1)

                    assert short_ttl_cache.get(cache_key) is not None
                    time.sleep(0.2)
                    assert short_ttl_cache.get(cache_key) is None

    def test_cache_size_limits(self, fixtures):
        """Test cache eviction when size limit reached."""
        small_cache = MemoryCache(max_size=3)

        responses = []
        for i in range(5):
            response = {
                "id": f"W{i}",
                "display_name": f"Work {i}",
                "publication_year": 2020 + i,
            }
            responses.append(Mock(json=lambda r=response: r, status_code=200))

        with self.patch_cache_manager(cache=small_cache, cache_enabled=True):
            with patch("httpx.Client.request") as mock_request:
                mock_request.side_effect = responses
                for i in range(5):
                    Works()[f"W{i}"]

                stats = small_cache.stats()
                assert stats["size"] <= 3
                assert stats["evictions"] >= 2

    def test_concurrent_cache_access(self, fixtures):
        """Test cache thread safety under concurrent access."""
        work_response = fixtures.work_response()

        errors: list[Exception] = []
        results: list[str] = []

        # Set up mock outside of thread pool to ensure it's available to all threads
        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                json=lambda: work_response, status_code=200
            )

            with self.isolated_cache() as cache:

                def fetch_work(work_id: str) -> None:
                    try:
                        with self.patch_cache_manager(
                            cache=cache, cache_enabled=True
                        ):
                            work = Works()[work_id]
                            results.append(work.id)
                    except Exception as e:  # pragma: no cover - defensive
                        errors.append(e)

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [
                        executor.submit(fetch_work, "W2755950973")
                        for _ in range(20)
                    ]
                    for future in futures:
                        future.result()

        assert len(errors) == 0
        assert len(results) == 20
        assert results.count("https://openalex.org/W2755950973") == 20
