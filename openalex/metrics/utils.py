from __future__ import annotations

from ..config import OpenAlexConfig
from .collector import MetricsCollector

_metrics_collectors: dict[int, MetricsCollector] = {}


def get_metrics_collector(config: OpenAlexConfig) -> MetricsCollector:
    """Get or create metrics collector for config."""
    key = id(config)
    if key not in _metrics_collectors:
        _metrics_collectors[key] = MetricsCollector()
    return _metrics_collectors[key]
