"""Publishers resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..constants import Resource
from ..models import BaseFilter, Publisher
from .base import AsyncBaseResource, BaseResource

__all__ = ["AsyncPublishersResource", "PublishersResource"]

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class PublishersResource(BaseResource[Publisher, BaseFilter]):
    """Resource for accessing publishers endpoints."""

    endpoint = Resource.PUBLISHERS.value
    model_class = Publisher
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize publishers resource."""
        super().__init__(client)


class AsyncPublishersResource(AsyncBaseResource[Publisher, BaseFilter]):
    """Async resource for accessing publishers endpoints."""

    endpoint = Resource.PUBLISHERS.value
    model_class = Publisher
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async publishers resource."""
        super().__init__(client)
