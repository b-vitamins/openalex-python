"""Keywords resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Keyword
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncKeywordsResource", "KeywordsResource"]

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class KeywordsResource(BaseResource[Keyword, BaseFilter]):
    """Resource for accessing keywords endpoints."""

    endpoint = "keywords"
    model_class = Keyword
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize keywords resource."""
        super().__init__(client)


class AsyncKeywordsResource(AsyncBaseResource[Keyword, BaseFilter]):
    """Async resource for accessing keywords endpoints."""

    endpoint = "keywords"
    model_class = Keyword
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async keywords resource."""
        super().__init__(client)
