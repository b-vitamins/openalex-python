from __future__ import annotations

import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

from structlog import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["CircuitBreaker", "CircuitState"]

logger = get_logger(__name__)


class CircuitState(Enum):
    """Possible states of a :class:`CircuitBreaker`."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._failure_count = 0
        self._last_failure_time: datetime | None = None
        self._state = CircuitState.CLOSED
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Return current circuit state."""
        with self._lock:
            if (
                self._state == CircuitState.OPEN
                and self._last_failure_time
                and datetime.now() - self._last_failure_time
                > timedelta(seconds=self.recovery_timeout)
            ):
                self._state = CircuitState.HALF_OPEN
            return self._state

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``func`` protected by the circuit breaker."""
        if self.state == CircuitState.OPEN:
            msg = "Circuit breaker is open - API is unavailable"
            raise RuntimeError(msg)

        try:
            result = func(*args, **kwargs)
        except self.expected_exception:  # pragma: no cover - protective
            self._on_failure()
            raise
        else:
            self._on_success()
            return result

    def _on_success(self) -> None:
        """Handle a successful call."""
        with self._lock:
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                logger.info("circuit_breaker_closed", recovered=True)
                self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Handle a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            if self._failure_count >= self.failure_threshold:
                logger.warning(
                    "circuit_breaker_opened",
                    failure_count=self._failure_count,
                    threshold=self.failure_threshold,
                )
                self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Reset the circuit to the ``CLOSED`` state."""
        with self._lock:
            self._failure_count = 0
            self._state = CircuitState.CLOSED
            self._last_failure_time = None
