"""Configuration primitives for the Event Bus runtime."""

from __future__ import annotations

from dataclasses import dataclass

from .models import RetryPolicy


@dataclass(frozen=True, slots=True)
class EventBusConfig:
    """Validated runtime configuration with safe operational defaults."""

    queue_maxsize: int = 10_000
    dispatch_timeout_ms: int = 5_000
    worker_count: int = 4
    retry_policy: RetryPolicy = RetryPolicy()

    def __post_init__(self) -> None:
        if self.queue_maxsize <= 0:
            raise ValueError("queue_maxsize must be positive")
        if self.dispatch_timeout_ms <= 0:
            raise ValueError("dispatch_timeout_ms must be positive")
        if self.worker_count <= 0:
            raise ValueError("worker_count must be positive")
