"""PyAlex - A Python library for OpenAlex."""

from __future__ import annotations

from structlog import get_logger

# Version is managed here and in pyproject.toml
# Keep both in sync when releasing
__version__ = "0.1.0"
__author__ = "OpenAlex Python Contributors"
__license__ = "MIT"

from .client import OpenAlexClient
from .config import OpenAlexConfig
from .connection import close_all_async_connections
from .entities import (
    AsyncAuthors,
    AsyncConcepts,
    AsyncFunders,
    AsyncInstitutions,
    AsyncKeywords,
    AsyncPublishers,
    AsyncSources,
    AsyncTopics,
    AsyncWorks,
    Authors,
    Concepts,
    Funders,
    Institutions,
    Keywords,
    Publishers,
    Sources,
    Topics,
    Works,
)
from .exceptions import (
    APIError,
    NetworkError,
    NotFoundError,
    OpenAlexError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .models import (
    Author,
    Concept,
    Funder,
    Institution,
    Keyword,
    Publisher,
    Source,
    Topic,
    Work,
)
from .query import Query, gt_, gte_, lt_, lte_, not_, or_

logger = get_logger(__name__)

__all__ = [
    "APIError",
    "AsyncAuthors",
    "AsyncConcepts",
    "AsyncFunders",
    "AsyncInstitutions",
    "AsyncKeywords",
    "AsyncPublishers",
    "AsyncSources",
    "AsyncTopics",
    "AsyncWorks",
    "Author",
    "Authors",
    "Concept",
    "Concepts",
    "Funder",
    "Funders",
    "Institution",
    "Institutions",
    "Keyword",
    "Keywords",
    "NetworkError",
    "NotFoundError",
    "OpenAlexClient",
    "OpenAlexConfig",
    "OpenAlexError",
    "Publisher",
    "Publishers",
    "Query",
    "RateLimitError",
    "Source",
    "Sources",
    "TimeoutError",
    "Topic",
    "Topics",
    "ValidationError",
    "Work",
    "Works",
    "__version__",
    "close_all_async_connections",
    "gt_",
    "gte_",
    "lt_",
    "lte_",
    "not_",
    "or_",
]
