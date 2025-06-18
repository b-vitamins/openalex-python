import time
from unittest.mock import Mock, patch
import asyncio

import pytest

from openalex import Works, OpenAlexConfig
from tests.base import IsolatedTestCase
from openalex.exceptions import ServerError
from openalex.resilience import CircuitBreaker, CircuitState


class TestResilience(IsolatedTestCase):
    @pytest.mark.isolated
    def test_circuit_breaker_opens_after_failures(self):

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

    @pytest.mark.asyncio
    async def test_async_circuit_breaker_lifecycle(self):
        """Test async circuit breaker state transitions."""
        from openalex.resilience import AsyncCircuitBreaker
        from openalex.resilience.async_circuit_breaker import CircuitState
        import asyncio

        breaker = AsyncCircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.1,
            expected_exception=ServerError,
        )

        assert await breaker.state() == CircuitState.CLOSED

        async def failing_call():
            raise ServerError("Service unavailable")

        for _ in range(2):
            with pytest.raises(ServerError):
                await breaker.call(failing_call)

        assert await breaker.state() == CircuitState.OPEN

        with pytest.raises(RuntimeError, match="Circuit breaker is open"):
            await breaker.call(failing_call)

        await asyncio.sleep(0.2)
        assert await breaker.state() == CircuitState.HALF_OPEN

        async def success_call():
            return "success"

        result = await breaker.call(success_call)
        assert result == "success"
        assert await breaker.state() == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_async_request_queue(self):
        """Test async request queue with rate limiting."""
        from openalex.resilience import AsyncRequestQueue
        from openalex.utils import AsyncRateLimiter

        queue = AsyncRequestQueue(max_size=10)
        rate_limiter = AsyncRateLimiter(calls_per_second=5)
        queue.set_rate_limiter(rate_limiter)

        await queue.start()

        try:
            execution_times = []

            async def timed_request():
                start = time.time()
                await asyncio.sleep(0.01)
                execution_times.append(time.time())
                return start

            tasks = [queue.enqueue(timed_request) for _ in range(10)]
            results = await asyncio.gather(*tasks)

            total_time = max(execution_times) - min(execution_times)
            assert total_time >= 1.5
            assert len(results) == 10
        finally:
            await queue.stop()
