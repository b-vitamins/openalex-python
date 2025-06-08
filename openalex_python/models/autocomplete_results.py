"""Container for a set of autocomplete suggestions."""
from __future__ import annotations
from collections.abc import Iterable
from .autocomplete_result import AutocompleteResult
from .meta import Meta


class AutocompleteResults:
    """List of :class:`AutocompleteResult` objects returned with metadata."""
    def __init__(self, *, meta: Meta, results: Iterable[AutocompleteResult]) -> None:
        self.results = list(results)
