import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class AsyncQueuedRequest:
    func: Callable[..., Awaitable[Any]]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    future: asyncio.Future[Any]


class AsyncRequestQueue:
    """Async version of request queue."""

    def __init__(self, max_size: int = 1000) -> None:
        self._queue: asyncio.Queue[AsyncQueuedRequest] = asyncio.Queue(maxsize=max_size)
        self._worker_task: asyncio.Task[None] | None = None
        self._rate_limiter = None
        self._stop_event = asyncio.Event()

    def set_rate_limiter(self, rate_limiter: Any) -> None:
        self._rate_limiter = rate_limiter

    def start(self) -> None:
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._process_queue())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._worker_task:
            await self._worker_task

    async def enqueue(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        future: asyncio.Future[Any] = asyncio.Future()
        request = AsyncQueuedRequest(
            func=func,
            args=args,
            kwargs=kwargs,
            future=future,
        )

        try:
            await asyncio.wait_for(
                self._queue.put(request), timeout=5.0
            )
        except TimeoutError:
            msg = "Request queue is full"
            raise RuntimeError(msg) from None

        return await future

    async def _process_queue(self) -> None:
        while not self._stop_event.is_set():
            try:
                request = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
            except TimeoutError:
                continue

            if self._rate_limiter:
                wait_time = await self._rate_limiter.acquire()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            try:
                result = await request.func(*request.args, **request.kwargs)
                request.future.set_result(result)
            except Exception as exc:  # pragma: no cover - unexpected
                request.future.set_exception(exc)
