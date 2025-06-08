"""Topics resource for OpenAlex API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BaseFilter, Topic
from .base import AsyncBaseResource, BaseResource

if TYPE_CHECKING:
    from ..client import AsyncOpenAlex, OpenAlex


class TopicsResource(BaseResource[Topic, BaseFilter]):
    """Resource for accessing topics endpoints."""

    endpoint = "topics"
    model_class = Topic
    filter_class = BaseFilter

    def __init__(self, client: OpenAlex) -> None:
        """Initialize topics resource."""
        super().__init__(client)


class AsyncTopicsResource(AsyncBaseResource[Topic, BaseFilter]):
    """Async resource for accessing topics endpoints."""

    endpoint = "topics"
    model_class = Topic
    filter_class = BaseFilter

    def __init__(self, client: AsyncOpenAlex) -> None:
        """Initialize async topics resource."""
        super().__init__(client)
