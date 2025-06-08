"""Container for a set of autocomplete suggestions."""

from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from .autocomplete_result import AutocompleteResult
from .meta import Meta


@dataclass(slots=True)
class AutocompleteResults:
    """List of :class:`AutocompleteResult` objects returned with metadata."""
    meta: Meta
    results: Iterable[AutocompleteResult]

    def __post_init__(self) -> None:
        """Normalize results iterable to a list."""
        self.results = list(self.results)
