"""Keywords extracted from a text body."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .text_keyword import TextKeyword
from .text_keywords_results_meta import TextKeywordsResultsMeta


@dataclass(slots=True)
class TextKeywordsResults:
    """List of keywords with associated metadata."""

    meta: TextKeywordsResultsMeta | None = None
    keywords: Iterable[TextKeyword] | None = None

    def __post_init__(self) -> None:
        """Ensure keywords are stored as a list."""
        if self.keywords is not None:
            self.keywords = list(self.keywords)
