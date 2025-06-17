from __future__ import annotations

from typing import TYPE_CHECKING

from .collector import MetricsCollector

if TYPE_CHECKING:
    from ..config import OpenAlexConfig

_metrics_collectors: dict[int, MetricsCollector] = {}


def get_metrics_collector(config: OpenAlexConfig) -> MetricsCollector:
    """Get or create metrics collector for config."""
    key = id(config)
    if key not in _metrics_collectors:
        _metrics_collectors[key] = MetricsCollector()
    return _metrics_collectors[key]
