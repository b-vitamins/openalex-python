"""Tests to verify that our isolation mechanisms work correctly."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from openalex import Works
from openalex.cache.manager import _cache_managers, get_cache_manager
from openalex.config import OpenAlexConfig
from tests.base import CachePatchingTestCase


class TestIsolationMechanisms:
    """Verify that our test isolation mechanisms work properly."""

    def test_cache_disabled_truly_disables_caching(self) -> None:
        config = OpenAlexConfig(cache_enabled=False)
        manager = get_cache_manager(config)

        assert manager.enabled is False
        assert manager.cache is None

        works = Works(config=config)

        with patch("httpx.Client.request") as mock_request:
            mock_request.return_value = Mock(
                status_code=200,
                json=Mock(return_value={"id": "W123", "title": "Test"}),
            )
            for _ in range(3):
                work = works.get("W123")
                assert work.title == "Test"

            assert mock_request.call_count == 3

    def test_cache_managers_isolated_by_config(self) -> None:
        config1 = OpenAlexConfig(cache_enabled=True, email="user1@example.com")
        config2 = OpenAlexConfig(cache_enabled=False, email="user2@example.com")

        manager1 = get_cache_manager(config1)
        manager2 = get_cache_manager(config2)

        assert manager1 is not manager2
        assert manager1.enabled is True
        assert manager2.enabled is False

    def test_patch_cleanup_works(self) -> None:
        test_case = CachePatchingTestCase()
        import openalex.cache.manager as cm

        original_get_cache_manager = cm.get_cache_manager

        with test_case.patch_cache_manager(cache_enabled=True) as mock_manager:
            config = OpenAlexConfig()
            manager = cm.get_cache_manager(config)
            assert manager is mock_manager

        assert cm.get_cache_manager is original_get_cache_manager

        _cache_managers.clear()
        config2 = OpenAlexConfig(cache_enabled=False)
        manager2 = cm.get_cache_manager(config2)
        assert manager2 is not mock_manager
