"""Container for a funder search response."""
from __future__ import annotations

from collections.abc import Iterable

from .funder import Funder
from .group_by_result import GroupByResult
from .meta import Meta


class FundersList:
    """List of funders returned by the API."""

    def __init__(
        self,
        *,
        meta: Meta,
        results: Iterable[Funder],
        group_by: GroupByResult | None = None,
    ) -> None:
        self.meta = meta
        self.results = list(results)
        self.group_by = group_by
