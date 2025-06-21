import time
from unittest.mock import Mock, patch

import pytest

from openalex import Works, OpenAlexConfig
from openalex.models import Work


class TestCacheWarming:
    def test_warming_cache_with_10_ids(self):
        """Test warming cache with 10 IDs populates cache."""
        config = OpenAlexConfig(cache_enabled=True)
        works = Works(config=config)

        ids = [f"W200000000{i}" for i in range(10)]

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "id": f"https://openalex.org/{i}",
                            "title": str(i),
                        }
                    ),
                )
                for i in ids
            ]
            results = works.warm_cache(ids)

        assert all(results.values())
        assert mock_request.call_count == len(ids)

    def test_second_fetch_is_instant(self):
        """Test fetching warmed IDs is much faster."""
        config = OpenAlexConfig(cache_enabled=True)
        works = Works(config=config)

        id = "W2000000001"

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(
                    return_value={
                        "id": f"https://openalex.org/{id}",
                        "title": "x",
                    }
                ),
            )
            works.warm_cache([id])

        start = time.time()
        with patch("httpx.Client.request") as mock_request:
            work = works.get(id)
            mock_request.assert_not_called()
        duration = time.time() - start

        assert duration < 0.01

    def test_cache_stats_show_hits(self):
        """Test cache stats reflect warmed entries."""
        config = OpenAlexConfig(cache_enabled=True)
        works = Works(config=config)

        ids = ["W2000000001", "W2000000002"]
        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = [
                Mock(
                    status_code=200,
                    json=Mock(
                        return_value={
                            "id": f"https://openalex.org/{i}",
                            "title": "x",
                        }
                    ),
                )
                for i in ids
            ]
            works.warm_cache(ids)

        with patch("httpx.Client.request") as mock_request:
            works.get(ids[0])
            works.get(ids[1])
            mock_request.assert_not_called()

        stats = works.cache_stats()
        assert stats["hits"] >= 2
