"""Buckets produced by a group-by query."""
from __future__ import annotations

from collections.abc import Iterable

from .group_by_result_inner import GroupByResultInner


class GroupByResult:
    """Collection of grouped results."""

    def __init__(self, buckets: Iterable[GroupByResultInner] | None = None) -> None:
        self.buckets = list(buckets) if buckets is not None else []
