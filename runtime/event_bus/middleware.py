"""Composable middleware pipeline for Event Bus publication."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from .models import Event


Next = Callable[[Event], Awaitable[None]]
Middleware = Callable[[Event, Next], Awaitable[None]]


class MiddlewarePipeline:
    """Executes middleware in registration order around the terminal handler."""

    def __init__(self, middleware: Sequence[Middleware] = ()) -> None:
        self._middleware = tuple(middleware)

    async def execute(self, event: Event, terminal: Next) -> None:
        async def invoke(index: int, current: Event) -> None:
            if index >= len(self._middleware):
                await terminal(current)
                return
            handler = self._middleware[index]
            await handler(current, lambda next_event: invoke(index + 1, next_event))

        await invoke(0, event)
