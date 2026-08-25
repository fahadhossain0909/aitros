"""Dependency-free metrics sink for the reference runtime."""

from __future__ import annotations

from collections import defaultdict


class InMemoryMetrics:
    """Thread-compatible-by-convention metrics collector for tests and local runs."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = defaultdict(int)
        self.observations: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1) -> None:
        if value < 0:
            raise ValueError("counter increment must be non-negative")
        self.counters[name] += value

    def observe(self, name: str, value: float) -> None:
        self.observations[name].append(float(value))
