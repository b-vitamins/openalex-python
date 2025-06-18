import time
from unittest.mock import Mock, patch

import pytest

from openalex import Works, OpenAlexConfig
from openalex.exceptions import ServerError
from openalex.resilience import CircuitBreaker, CircuitState


class TestResilience:
    def test_circuit_breaker_opens_after_failures(self):
        # Force clear any existing cache managers and patches
        from openalex.cache.manager import _cache_managers, get_cache_manager as original_get_cache_manager
        import openalex.cache.manager
        import openalex.entities

        _cache_managers.clear()
        openalex.cache.manager.get_cache_manager = original_get_cache_manager
        openalex.entities.get_cache_manager = original_get_cache_manager

        config = OpenAlexConfig(
            circuit_breaker_enabled=True,
            circuit_breaker_failure_threshold=3,
            cache_enabled=False,
        )

        with patch("httpx.Client.request") as mock_request:
            mock_request.side_effect = ServerError("Server error")
            works = Works(config=config)

            for _ in range(3):
                with pytest.raises(ServerError):
                    works.get("W123")

            with pytest.raises(Exception, match="Circuit breaker is open"):
                works.get("W123")

    def test_circuit_breaker_recovers(self):
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
        )

        for _ in range(2):
            with pytest.raises(Exception):
                breaker.call(lambda: 1 / 0)

        assert breaker.state == CircuitState.OPEN

        time.sleep(0.2)
        assert breaker.state == CircuitState.HALF_OPEN

        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED

    def test_request_queue_during_rate_limit(self):
        pass
