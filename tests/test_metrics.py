import httpx
import pytest
from unittest.mock import patch

from openalex import OpenAlexConfig, Works
from tests.base import IsolatedTestCase


class TestMetrics(IsolatedTestCase):
    @pytest.mark.isolated
    def test_metrics_collection_when_enabled(self):

        config = OpenAlexConfig(
            collect_metrics=True,
            retry_enabled=False,
            cache_enabled=False,
            email="enabled@example.com",
        )
        works = Works(config=config)

        resp1 = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001", "title": "x"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )
        resp2 = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000002", "title": "y"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000002"
            ),
        )

        with patch("httpx.Client.request", side_effect=[resp1, resp2]):
            works.get("W2000000001")
            works.get("W2000000002")

        report = works.get_metrics()

        assert report is not None
        assert report.total_requests == 2
        assert report.requests_by_endpoint["works"] == 2

    def test_no_metrics_when_disabled(self):
        config = OpenAlexConfig(
            collect_metrics=False,
            retry_enabled=False,
            email="disabled@example.com",
        )
        works = Works(config=config)

        resp = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )

        with patch("httpx.Client.request", return_value=resp):
            works.get("W2000000001")

        report = works.get_metrics()
        assert report is None

    @pytest.mark.isolated
    def test_cache_metrics_tracked(self):

        config = OpenAlexConfig(
            collect_metrics=True,
            cache_enabled=True,
            retry_enabled=False,
            email="cache@example.com",
        )
        works = Works(config=config)

        resp = httpx.Response(
            200,
            json={"id": "https://openalex.org/W2000000001"},
            request=httpx.Request(
                "GET", "https://api.openalex.org/works/W2000000001"
            ),
        )

        with patch("httpx.Client.request", return_value=resp) as mock_request:
            works.get("W2000000001")
            works.get("W2000000001")
            assert mock_request.call_count == 1

        report = works.get_metrics()
        assert report.cache_hits == 1
        assert report.cache_misses == 1
        assert report.cache_hit_rate == 0.5


class TestMetrics:
    def test_performance_metrics_tracking(self):
        """Test complete performance metrics collection."""
        from openalex.metrics.performance import MetricsCollector, get_collector
        import time
        import threading

        collector = MetricsCollector()
        collector.enable()

        operations = [
            ("works", 0.1, True),
            ("authors", 0.2, True),
            ("works", 0.15, True),
            ("works", 0.5, False),
            ("authors", 0.3, True),
        ]

        for endpoint, duration, success in operations:
            collector.record_request(endpoint, duration * 1000, success=success)

        collector.record_cache_hit()
        collector.record_cache_hit()
        collector.record_cache_miss()
        collector.record_retry()
        collector.record_rate_limit()
        collector.record_error("TimeoutError")
        collector.record_error("NetworkError")
        collector.record_error("TimeoutError")

        metrics = collector.get_metrics()

        assert metrics.total_requests == 5
        assert metrics.successful_requests == 4
        assert metrics.failed_requests == 1
        assert metrics.success_rate == 0.8
        assert metrics.requests_by_endpoint["works"] == 3
        assert metrics.requests_by_endpoint["authors"] == 2
        assert abs(metrics.avg_response_time - 230.0) < 0.1
        assert metrics.p95_response_time == 500.0
        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 1
        assert metrics.cache_hit_rate == 2/3
        assert metrics.total_retries == 1
        assert metrics.rate_limit_hits == 1
        assert metrics.errors_by_type["TimeoutError"] == 2
        assert metrics.errors_by_type["NetworkError"] == 1

        results = []

        def record_many():
            for i in range(100):
                collector.record_request("test", i, success=True)
                if i % 2 == 0:
                    collector.record_cache_hit()
            results.append(collector.get_metrics().total_requests)

        threads = [threading.Thread(target=record_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final_metrics = collector.get_metrics()
        assert final_metrics.total_requests == 505

        collector.reset()
        reset_metrics = collector.get_metrics()
        assert reset_metrics.total_requests == 0
        assert len(reset_metrics.response_times) == 0

        collector.disable()
        collector.record_request("test", 100, success=True)
        assert collector.get_metrics().total_requests == 0
