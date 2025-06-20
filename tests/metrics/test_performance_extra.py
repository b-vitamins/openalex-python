import pytest

from openalex.metrics.performance import (
    get_collector,
    get_metrics,
    reset_metrics,
)


@pytest.fixture(autouse=True)
def _reset_metrics():
    reset_metrics()
    yield
    reset_metrics()


def test_metrics_collector_records_and_resets() -> None:
    collector = get_collector()
    collector.record_request("works", 0.5, success=True)
    collector.record_request("works", 0.2, success=False)
    collector.record_cache_hit()
    collector.record_cache_miss()
    collector.record_retry()
    collector.record_error("HTTPError")
    collector.record_rate_limit()

    metrics = get_metrics()
    assert metrics.total_requests == 2
    assert metrics.successful_requests == 1
    assert metrics.failed_requests == 1
    assert metrics.cache_hits == 1
    assert metrics.cache_misses == 1
    assert metrics.total_retries == 1
    assert metrics.rate_limit_hits == 1
    assert metrics.errors_by_type["HTTPError"] == 1
    assert metrics.requests_by_endpoint["works"] == 2
    assert pytest.approx(metrics.avg_response_time, rel=1e-3) == 0.35

    report = metrics.to_dict()
    assert report["summary"]["total_requests"] == 2

    reset_metrics()
    assert get_metrics().total_requests == 0


def test_metrics_collector_disable_enable() -> None:
    collector = get_collector()
    collector.disable()
    collector.record_request("works", 0.1, success=True)
    collector.record_cache_hit()

    metrics = get_metrics()
    assert metrics.total_requests == 0
    assert metrics.cache_hits == 0

    collector.enable()
    collector.record_request("works", 0.1, success=True)
    assert get_metrics().total_requests == 1
