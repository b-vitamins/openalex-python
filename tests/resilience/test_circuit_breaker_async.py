"""Tests for async circuit breaker implementation."""

import asyncio
from datetime import datetime, timedelta

import pytest

from openalex.resilience.circuit_breaker import AsyncCircuitBreaker, CircuitState


class TestAsyncCircuitBreaker:
    """Test AsyncCircuitBreaker implementation."""

    @pytest.mark.asyncio
    async def test_circuit_states(self):
        """Test circuit breaker state transitions."""
        breaker = AsyncCircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        # Initial state should be CLOSED
        assert await breaker.state == CircuitState.CLOSED
        
        # First failure
        with pytest.raises(ValueError):
            await breaker.call(self._failing_async_func)
        assert await breaker.state == CircuitState.CLOSED
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            await breaker.call(self._failing_async_func)
        assert await breaker.state == CircuitState.OPEN
        
        # Circuit is open - should raise immediately
        with pytest.raises(RuntimeError, match="Circuit breaker is open"):
            await breaker.call(self._failing_async_func)
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        assert await breaker.state == CircuitState.HALF_OPEN
        
        # Successful call should close circuit
        result = await breaker.call(self._successful_async_func)
        assert result == "success"
        assert await breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test circuit breaker as async context manager."""
        breaker = AsyncCircuitBreaker(failure_threshold=3)
        
        # Test successful operation
        async with breaker:
            result = await self._successful_async_func()
            assert result == "success"
        
        # Test failed operations
        for _ in range(3):
            with pytest.raises(ValueError):
                async with breaker:
                    await self._failing_async_func()
        
        # Circuit should be open
        assert await breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_reset(self):
        """Test manual circuit reset."""
        breaker = AsyncCircuitBreaker(failure_threshold=1)
        
        # Open the circuit
        with pytest.raises(ValueError):
            await breaker.call(self._failing_async_func)
        assert await breaker.state == CircuitState.OPEN
        
        # Reset circuit
        await breaker.reset()
        assert await breaker.state == CircuitState.CLOSED
        
        # Should work again
        result = await breaker.call(self._successful_async_func)
        assert result == "success"

    @staticmethod
    async def _failing_async_func():
        """Async function that always fails."""
        await asyncio.sleep(0.01)
        raise ValueError("Intentional failure")

    @staticmethod
    async def _successful_async_func():
        """Async function that always succeeds."""
        await asyncio.sleep(0.01)
        return "success"
