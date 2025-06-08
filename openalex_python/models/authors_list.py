"""Model representing a list of authors returned from the API."""
from __future__ import annotations

from collections.abc import Iterable

from .author import Author
from .group_by_result import GroupByResult
from .meta import Meta


class AuthorsList:
    """A collection of authors with associated metadata."""

    def __init__(
        self,
        *,
        meta: Meta,
        results: Iterable[Author],
        group_by: GroupByResult | None = None,
    ) -> None:
        self.meta = meta
        self.results = list(results)
        self.group_by = group_by
