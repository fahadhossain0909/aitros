"""Controlled extension lifecycle for Event Bus plugins."""

from __future__ import annotations

from typing import Protocol


class EventBusPlugin(Protocol):
    """Plugin contract for controlled runtime extensions."""

    async def initialize(self) -> None:
        ...

    async def shutdown(self) -> None:
        ...


class PluginManager:
    """Owns plugin lifecycle and prevents duplicate registration."""

    def __init__(self) -> None:
        self._plugins: dict[str, EventBusPlugin] = {}

    async def register(self, name: str, plugin: EventBusPlugin) -> None:
        if not name.strip():
            raise ValueError("plugin name must not be empty")
        if name in self._plugins:
            raise ValueError(f"plugin already registered: {name}")
        await plugin.initialize()
        self._plugins[name] = plugin

    async def shutdown(self) -> None:
        for plugin in reversed(tuple(self._plugins.values())):
            await plugin.shutdown()
        self._plugins.clear()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._plugins))
