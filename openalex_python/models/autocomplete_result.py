"""Single autocomplete suggestion returned from the API."""

from __future__ import annotations

from dataclasses import dataclass


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
