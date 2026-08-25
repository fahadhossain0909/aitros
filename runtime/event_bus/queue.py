"""Queue abstractions used by Event Bus dispatchers."""

from __future__ import annotations

import asyncio
from typing import Generic, TypeVar


T = TypeVar("T")


class QueueFullError(RuntimeError):
    """Raised when a non-blocking enqueue exceeds queue capacity."""


class AsyncQueue(Generic[T]):
    """Small dependency-free queue abstraction."""

    def __init__(self, maxsize: int = 10_000) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=maxsize)

    async def put(self, item: T) -> None:
        await self._queue.put(item)

    def put_nowait(self, item: T) -> None:
        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull as exc:
            raise QueueFullError("event queue is full") from exc

    async def get(self) -> T:
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()

    def qsize(self) -> int:
        return self._queue.qsize()
