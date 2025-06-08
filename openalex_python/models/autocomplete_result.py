"""Single autocomplete suggestion returned from the API."""
from __future__ import annotations


class AutocompleteResult:
    """Details of an individual autocomplete match."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        entity_type: str,
        hint: str | None = None,
        cited_by_count: int | None = None,
        works_count: int | None = None,
        external_id: str | None = None,
        filter_key: str | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.hint = hint
        self.cited_by_count = cited_by_count
        self.works_count = works_count
        self.entity_type = entity_type
        self.external_id = external_id
        self.filter_key = filter_key
