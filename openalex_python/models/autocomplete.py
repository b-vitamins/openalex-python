"""Models for the autocomplete API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .common import Meta


@dataclass(slots=True)
class AutocompleteResult:
    """Details of an individual autocomplete match."""

    id: str
    display_name: str
    entity_type: str
    hint: str | None = None
    cited_by_count: int | None = None
    works_count: int | None = None
    external_id: str | None = None
    filter_key: str | None = None


@dataclass(slots=True)
class AutocompleteResults:
    """List of :class:`AutocompleteResult` objects returned with metadata."""

    meta: Meta
    results: list[AutocompleteResult] | Iterable[AutocompleteResult]

    def __post_init__(self) -> None:
        self.results = list(self.results)
