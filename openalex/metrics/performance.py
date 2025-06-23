"""Performance metrics collection for OpenAlex client."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Any

from structlog import get_logger

__all__ = [
    "MetricType",
    "MetricsCollector",
    "PerformanceMetrics",
    "get_collector",
    "get_metrics",
    "reset_metrics",
]

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of metrics collected."""

    API_CALL = "api_call"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    RETRY = "retry"
    ERROR = "error"
    RATE_LIMIT = "rate_limit"


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_retries: int = 0
    rate_limit_hits: int = 0

    response_times: list[float] = field(default_factory=lambda: [])
    errors_by_type: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    requests_by_endpoint: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    start_time: datetime = field(default_factory=datetime.now)

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache = self.cache_hits + self.cache_misses
        return self.cache_hits / total_cache if total_cache > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Calculate request success rate."""
        return (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time in milliseconds."""
        return (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0.0
        )

    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time."""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return (
            sorted_times[index]
            if index < len(sorted_times)
            else sorted_times[-1]
        )

    @property
    def uptime(self) -> timedelta:
        """Get time since metrics collection started."""
        return datetime.now() - self.start_time

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for reporting."""
        return {
            "summary": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": f"{self.success_rate:.2%}",
                "uptime_seconds": self.uptime.total_seconds(),
            },
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": f"{self.cache_hit_rate:.2%}",
            },
            "performance": {
                "avg_response_time_ms": f"{self.avg_response_time:.2f}",
                "p95_response_time_ms": f"{self.p95_response_time:.2f}",
                "total_retries": self.total_retries,
                "rate_limit_hits": self.rate_limit_hits,
            },
            "endpoints": dict(self.requests_by_endpoint),
            "errors": dict(self.errors_by_type),
        }


class MetricsCollector:
    """Thread-safe metrics collector."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self._metrics = PerformanceMetrics()
        self._lock = Lock()
        self._enabled = True

    def record_request(
        self, endpoint: str, response_time: float, *, success: bool
    ) -> None:
        """Record an API request."""
        if not self._enabled:
            return

        with self._lock:
            self._metrics.total_requests += 1
            self._metrics.response_times.append(response_time)
            self._metrics.requests_by_endpoint[endpoint] += 1

            if success:
                self._metrics.successful_requests += 1
            else:
                self._metrics.failed_requests += 1

            if len(self._metrics.response_times) > 1000:
                self._metrics.response_times = self._metrics.response_times[
                    -1000:
                ]

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        if not self._enabled:
            return
        with self._lock:
            self._metrics.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        if not self._enabled:
            return
        with self._lock:
            self._metrics.cache_misses += 1

    def record_retry(self) -> None:
        """Record a retry attempt."""
        if not self._enabled:
            return
        with self._lock:
            self._metrics.total_retries += 1

    def record_error(self, error_type: str) -> None:
        """Record an error by type."""
        if not self._enabled:
            return
        with self._lock:
            self._metrics.errors_by_type[error_type] += 1

    def record_rate_limit(self) -> None:
        """Record a rate limit hit."""
        if not self._enabled:
            return
        with self._lock:
            self._metrics.rate_limit_hits += 1

    def get_metrics(self) -> PerformanceMetrics:
        """Get a copy of current metrics."""
        with self._lock:
            return PerformanceMetrics(
                total_requests=self._metrics.total_requests,
                successful_requests=self._metrics.successful_requests,
                failed_requests=self._metrics.failed_requests,
                cache_hits=self._metrics.cache_hits,
                cache_misses=self._metrics.cache_misses,
                total_retries=self._metrics.total_retries,
                rate_limit_hits=self._metrics.rate_limit_hits,
                response_times=self._metrics.response_times.copy(),
                errors_by_type=dict(self._metrics.errors_by_type),
                requests_by_endpoint=dict(self._metrics.requests_by_endpoint),
                start_time=self._metrics.start_time,
            )

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics = PerformanceMetrics()

    def enable(self) -> None:
        """Enable metrics collection."""
        self._enabled = True

    def disable(self) -> None:
        """Disable metrics collection."""
        self._enabled = False


_metrics_collector = MetricsCollector()


def get_metrics() -> PerformanceMetrics:
    """Get current performance metrics."""
    return _metrics_collector.get_metrics()


def reset_metrics() -> None:
    """Reset all performance metrics."""
    _metrics_collector.reset()


def get_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics_collector
