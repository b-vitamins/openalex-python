"""Async entities - now using DRY templates."""

from structlog import get_logger

from .entities import (
    AsyncAuthors,
    AsyncBaseEntity,
    AsyncConcepts,
    AsyncFunders,
    AsyncInstitutions,
    AsyncKeywords,
    AsyncPublishers,
    AsyncSources,
    AsyncTopics,
    AsyncWorks,
)

logger = get_logger(__name__)

__all__ = [
    "AsyncAuthors",
    "AsyncBaseEntity",
    "AsyncConcepts",
    "AsyncFunders",
    "AsyncInstitutions",
    "AsyncKeywords",
    "AsyncPublishers",
    "AsyncSources",
    "AsyncTopics",
    "AsyncWorks",
]
