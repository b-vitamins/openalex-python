from __future__ import annotations

from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from .collector import MetricsCollector

if TYPE_CHECKING:
    from ..config import OpenAlexConfig

_metrics_collectors: WeakKeyDictionary[OpenAlexConfig, MetricsCollector] = WeakKeyDictionary()


def get_metrics_collector(config: OpenAlexConfig) -> MetricsCollector:
    """Get or create metrics collector for ``config``."""
    collector = _metrics_collectors.get(config)
    if collector is None:
        collector = MetricsCollector()
        _metrics_collectors[config] = collector
    return collector
