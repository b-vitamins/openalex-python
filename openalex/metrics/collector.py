from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricsReport:
    total_requests: int = 0
    total_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    requests_by_endpoint: dict[str, int] = field(default_factory=dict)
    average_response_time: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests: defaultdict[str, int] = defaultdict(int)
        self._errors: defaultdict[str, int] = defaultdict(int)
        self._response_times: list[float] = []
        self._cache_hits = 0
        self._cache_misses = 0

    def record_request(self, endpoint: str, duration: float, success: bool = True) -> None:
        with self._lock:
            self._requests[endpoint] += 1
            self._response_times.append(duration)
            if not success:
                self._errors[endpoint] += 1

    def record_cache_hit(self, _endpoint: str) -> None:
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self, _endpoint: str) -> None:
        with self._lock:
            self._cache_misses += 1

    def get_report(self) -> MetricsReport:
        with self._lock:
            total_requests = sum(self._requests.values())
            total_errors = sum(self._errors.values())
            avg_time = (
                sum(self._response_times) / len(self._response_times)
                if self._response_times
                else 0
            )
            return MetricsReport(
                total_requests=total_requests,
                total_errors=total_errors,
                cache_hits=self._cache_hits,
                cache_misses=self._cache_misses,
                requests_by_endpoint=dict(self._requests),
                average_response_time=avg_time,
                error_rate=(total_errors / total_requests) if total_requests > 0 else 0,
                cache_hit_rate=(
                    self._cache_hits / (self._cache_hits + self._cache_misses)
                    if (self._cache_hits + self._cache_misses) > 0
                    else 0
                ),
            )

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._requests.clear()
            self._errors.clear()
            self._response_times.clear()
            self._cache_hits = 0
            self._cache_misses = 0
