from __future__ import annotations

from typing import TypeVar, cast

from structlog import get_logger

from .entities import AsyncBaseEntity as _AsyncBaseEntity
from .models import BaseFilter
from .utils.validation import validate_entity_id

T = TypeVar("T")
F = TypeVar("F", bound=BaseFilter)

logger = get_logger(__name__)


class AsyncBaseEntity(_AsyncBaseEntity[T, F]):
    async def get_many(self, ids: list[str], max_concurrent: int = 10) -> list[T]:
        """Fetch multiple entities efficiently using concurrent requests."""
        import asyncio

        validated_ids: list[str] = []
        for id in ids:
            try:
                validated_id = validate_entity_id(id, self.endpoint.rstrip("s"))
                validated_ids.append(validated_id)
            except ValueError as e:
                logger.warning("Skipping invalid ID %s: %s", id, e)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(id: str) -> T | None:
            async with semaphore:
                try:
                    return cast(T, await _AsyncBaseEntity.get(self, id))
                except Exception:
                    logger.exception("Failed to fetch %s", id)
                    return None

        results = await asyncio.gather(
            *[fetch_with_semaphore(id) for id in validated_ids]
        )
        return [r for r in results if r is not None]
