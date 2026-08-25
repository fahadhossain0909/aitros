"""Operational health checks for the Event Bus."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class HealthReport:
    status: HealthStatus
    queue_depth: int
    workers: int
    running: bool


class HealthManager:
    """Builds health snapshots from runtime state."""

    def report(self, *, queue_depth: int, workers: int, running: bool) -> HealthReport:
        if not running:
            status = HealthStatus.UNAVAILABLE
        elif queue_depth > 0 and workers <= 0:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY
        return HealthReport(status, queue_depth, workers, running)
