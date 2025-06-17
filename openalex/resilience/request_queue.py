from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["QueuedRequest", "RequestQueue"]


@dataclass(slots=True)
class QueuedRequest:
    """Internal representation of a queued request."""

    func: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    result_future: threading.Event
    result: Any | None = None
    exception: Exception | None = None


class RequestQueue:
    """Queue requests and process them respecting rate limits."""

    def __init__(self, max_size: int = 1000) -> None:
        self._queue: queue.Queue[QueuedRequest] = queue.Queue(maxsize=max_size)
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._rate_limiter = None

    def set_rate_limiter(self, rate_limiter: Any) -> None:
        """Set the rate limiter used to throttle requests."""
        self._rate_limiter = rate_limiter

    def start(self) -> None:
        """Start background worker thread."""
        if self._worker_thread is None:
            self._worker_thread = threading.Thread(
                target=self._process_queue, daemon=True
            )
            self._worker_thread.start()

    def stop(self) -> None:
        """Stop the background worker."""
        self._stop_event.set()
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=5)

    def enqueue(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Add a request to the queue and wait for the result."""
        request = QueuedRequest(
            func=func,
            args=args,
            kwargs=kwargs,
            result_future=threading.Event(),
        )
        try:
            self._queue.put(request, timeout=5)
        except queue.Full:  # pragma: no cover - defensive
            msg = "Request queue is full"
            raise RuntimeError(msg) from None

        request.result_future.wait()

        if request.exception:
            raise request.exception
        return request.result

    def _process_queue(self) -> None:
        """Worker thread processing queued requests."""
        while not self._stop_event.is_set():
            try:
                request = self._queue.get(timeout=1)
            except queue.Empty:
                continue

            if self._rate_limiter is not None:
                wait_time = self._rate_limiter.acquire()
                if wait_time > 0:
                    time.sleep(wait_time)

            try:
                request.result = request.func(*request.args, **request.kwargs)
            except Exception as exc:  # pragma: no cover - unexpected
                request.exception = exc
            finally:
                request.result_future.set()
