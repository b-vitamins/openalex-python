from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from .collector import MetricsCollector

if TYPE_CHECKING:
    from ..config import OpenAlexConfig

_metrics_collectors: dict[int, tuple[weakref.ReferenceType[OpenAlexConfig], MetricsCollector]] = {}


def get_metrics_collector(config: OpenAlexConfig) -> MetricsCollector:
    """Get or create metrics collector for config."""
    key = id(config)
    entry = _metrics_collectors.get(key)
    if entry is not None:
        ref, collector = entry
        if ref() is config:
            return collector
        if ref() is None:
            del _metrics_collectors[key]
    collector = MetricsCollector()
    _metrics_collectors[key] = (weakref.ref(config), collector)
    return collector
