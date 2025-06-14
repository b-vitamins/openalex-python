"""
Test caching behavior based on expected functionality.
Tests what caching should do, not how it's implemented.
"""

import pytest
import time
from unittest.mock import Mock, patch


class TestCacheBehavior:
    """Test caching functionality from a behavior perspective."""

    def test_cache_prevents_duplicate_api_calls(self):
        """Cache should prevent duplicate API calls for same request."""
        from openalex import Works, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True, retry_enabled=False)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "id": "https://openalex.org/W123",
                    "title": "Cached Work"
                })
            )

            works = Works(config=config)

            # First call
            work1 = works.get("W123")
            assert work1.title == "Cached Work"

            # Second call (should be cached)
            work2 = works.get("W123")
            assert work2.title == "Cached Work"

            # Only one API call made
            assert mock_request.call_count == 1

    def test_cache_disabled_always_fetches(self):
        """When cache is disabled, every request should hit API."""
        from openalex import Authors, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=False)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "id": "https://openalex.org/A123",
                    "display_name": "Test Author"
                })
            )

            authors = Authors(config=config)

            # Multiple identical requests
            for _ in range(3):
                author = authors.get("A123")
                assert author.display_name == "Test Author"

            # All requests hit the API
            assert mock_request.call_count == 3

    def test_cache_expires_after_ttl(self):
        """Cache entries should expire after TTL."""
        from openalex import Institutions, OpenAlexConfig

        # Short TTL for testing
        config = OpenAlexConfig(cache_enabled=True, cache_ttl=0.1)

        with patch("httpx.Client.request") as mock_request:
            # Return different data on each call
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": "https://openalex.org/I123",
                        "display_name": "Original Name"
                    })
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": "https://openalex.org/I123",
                        "display_name": "Updated Name"
                    })
                )
            ]

            institutions = Institutions(config=config)

            # First call
            inst1 = institutions.get("I123")
            assert inst1.display_name == "Original Name"

            # Wait for cache to expire
            time.sleep(0.2)

            # Second call (cache expired)
            inst2 = institutions.get("I123")
            assert inst2.display_name == "Updated Name"

            assert mock_request.call_count == 2

    def test_cache_key_includes_all_parameters(self):
        """Cache should create different keys for different parameters."""
        from openalex import Works, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True, retry_enabled=False)

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "W1", "title": "OA Work"}],
                        "meta": {"count": 1}
                    })
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "W2", "title": "Non-OA Work"}],
                        "meta": {"count": 1}
                    })
                )
            ]

            works = Works(config=config)

            # Different filters should not share cache
            oa_results = works.filter(is_oa=True).get()
            non_oa_results = works.filter(is_oa=False).get()

            assert oa_results.results[0].title == "OA Work"
            assert non_oa_results.results[0].title == "Non-OA Work"
            assert mock_request.call_count == 2

    def test_cache_handles_pagination_correctly(self):
        """Cache should store different pages separately."""
        from openalex import Authors, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True, retry_enabled=False)

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "A1", "display_name": "Author 1"}],
                        "meta": {"count": 10, "page": 1}
                    })
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "results": [{"id": "A2", "display_name": "Author 2"}],
                        "meta": {"count": 10, "page": 2}
                    })
                )
            ]

            authors = Authors(config=config)

            # Get different pages
            page1 = authors.get(page=1)
            page2 = authors.get(page=2)

            assert page1.results[0].display_name == "Author 1"
            assert page2.results[0].display_name == "Author 2"

            # Fetch page 1 again (should be cached)
            page1_again = authors.get(page=1)
            assert page1_again.results[0].display_name == "Author 1"

            # Only 2 API calls (page 1 cached on second access)
            assert mock_request.call_count == 2

    def test_cache_not_used_for_random_endpoint(self):
        """Random endpoint should never be cached."""
        from openalex import Works, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True)

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": "W1",
                        "title": "Random Work 1"
                    })
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": "W2",
                        "title": "Random Work 2"
                    })
                )
            ]

            works = Works(config=config)

            # Multiple random calls
            work1 = works.random()
            work2 = works.random()

            # Should get different works (not cached)
            assert work1.id != work2.id
            assert mock_request.call_count == 2

    def test_cache_size_limit_evicts_old_entries(self):
        """Cache should evict old entries when size limit reached."""
        from openalex import Sources, OpenAlexConfig

        # Small cache for testing
        config = OpenAlexConfig(cache_enabled=True, cache_maxsize=2)

        with patch("httpx.Client.request") as mock_request:
            def make_response(id_num):
                return Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": f"https://openalex.org/S{id_num}",
                        "display_name": f"Source {id_num}"
                    })
                )

            mock_request.side_effect = [
                make_response(1),
                make_response(2),
                make_response(3),
                make_response(1),  # This will be fetched again
            ]

            sources = Sources(config=config)

            # Fill cache
            s1 = sources.get("S1")
            s2 = sources.get("S2")

            # This should evict S1
            s3 = sources.get("S3")

            # This should hit API again (S1 was evicted)
            s1_again = sources.get("S1")

            assert s1_again.display_name == "Source 1"
            assert mock_request.call_count == 4

    def test_cache_statistics_track_hits_and_misses(self):
        """Cache should track hit/miss statistics."""
        from openalex import Concepts, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "id": "https://openalex.org/C123",
                    "display_name": "Test Concept"
                })
            )

            concepts = Concepts(config=config)

            # First call (miss)
            concepts.get("C123")

            # Second and third calls (hits)
            concepts.get("C123")
            concepts.get("C123")

            # Get cache stats
            stats = concepts.cache_stats()

            assert stats["hits"] == 2
            assert stats["misses"] == 1
            assert stats["hit_rate"] == 2/3

    def test_cache_handles_errors_gracefully(self):
        """Cache should not cache error responses."""
        from openalex import Publishers, OpenAlexConfig

        config = OpenAlexConfig(cache_enabled=True, retry_enabled=False)

        with patch("httpx.Client.request") as mock_request:
            # First call fails
            mock_request.side_effect = [
                Mock(
                    status_code=500,
                    json=Mock(return_value={"error": "Server error"})
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "id": "https://openalex.org/P123",
                        "display_name": "Test Publisher"
                    })
                )
            ]

            publishers = Publishers(config=config)

            # First call should fail
            with pytest.raises(Exception):
                publishers.get("P123")

            # Second call should succeed (error not cached)
            publisher = publishers.get("P123")
            assert publisher.display_name == "Test Publisher"

            # Both calls hit the API
            assert mock_request.call_count == 2

    def test_cache_thread_safe_concurrent_access(self):
        """Cache should handle concurrent access safely."""
        from openalex import Works, OpenAlexConfig
        import threading

        config = OpenAlexConfig(cache_enabled=True)
        results = []

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={
                    "id": "https://openalex.org/W123",
                    "title": "Concurrent Work"
                })
            )

            works = Works(config=config)

            def fetch_work():
                work = works.get("W123")
                results.append(work.title)

            # Start multiple threads
            threads = []
            for _ in range(5):
                t = threading.Thread(target=fetch_work)
                threads.append(t)
                t.start()

            # Wait for all threads
            for t in threads:
                t.join()

            # All should get the same result
            assert len(results) == 5
            assert all(r == "Concurrent Work" for r in results)

            # But only one API call should be made
            assert mock_request.call_count == 1
