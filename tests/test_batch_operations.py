import time
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from openalex import AsyncWorks, Works
from openalex.models import Work


class TestBatchOperations:
    def test_get_many_returns_all_valid_entities(self, mock_work_data):
        works = Works()
        ids = [f"W{i}" for i in range(2000000000, 2000000050)]

        def side_effect(entity_id, params=None):
            return Work(id=f"https://openalex.org/{entity_id}", display_name="x")

        with patch.object(Works, "_get_single_entity", side_effect=side_effect):
            results = works.get_many(ids)

        assert len(results) == len(ids)
        assert all(isinstance(w, Work) for w in results)

    def test_invalid_ids_skipped_with_warning(self):
        works = Works()
        ids = ["W123", "invalid-id", "W456"]

        def side_effect(entity_id, params=None):
            return Work(id=f"https://openalex.org/{entity_id}", display_name=entity_id)

        with patch.object(Works, "_get_single_entity", side_effect=side_effect), patch(
            "openalex.entities.logger.warning"
        ) as mock_warn:
            results = works.get_many(ids)

        assert len(results) == 2
        mock_warn.assert_called_with(
            "Skipping invalid ID %s: %s", "invalid-id", ANY
        )

    def test_concurrent_limit_respected(self):
        works = Works()
        ids = [f"W{i}" for i in range(4)]
        call_times: list[float] = []

        def side_effect(entity_id, params=None):
            call_times.append(time.time())
            time.sleep(0.1)
            return Work(id=f"https://openalex.org/{entity_id}", display_name="x")

        with patch.object(Works, "_get_single_entity", side_effect=side_effect):
            start = time.time()
            works.get_many(ids, max_concurrent=2)
            duration = time.time() - start

        assert len(call_times) == len(ids)
        assert duration < 0.3
        assert duration > 0.19

    @pytest.mark.asyncio
    async def test_async_version_works(self):
        works = AsyncWorks()
        ids = [f"W{i}" for i in range(2000000000, 2000000010)]

        async def async_side_effect(entity_id):
            return Work(id=f"https://openalex.org/{entity_id}", display_name="x")

        with patch.object(AsyncWorks, "get", new=AsyncMock(side_effect=async_side_effect)):
            results = await works.get_many(ids)

        assert len(results) == len(ids)
        assert all(isinstance(w, Work) for w in results)
