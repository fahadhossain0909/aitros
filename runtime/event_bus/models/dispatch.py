"""Dispatch domain models for the AITOS Event Bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from .event import DeliveryMode, Event


class AckStatus(StrEnum):
    ACK = "ack"
    NACK = "nack"
    TIMEOUT = "timeout"


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    subscriber: str
    status: AckStatus
    completed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    error_code: str | None = None
    error_message: str | None = None
    attempt: int = 1

    def __post_init__(self) -> None:
        if not self.subscriber.strip():
            raise ValueError("subscriber must not be empty")
        if self.attempt < 1:
            raise ValueError("delivery attempt must be >= 1")
        if self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class DispatchPlan:
    event: Event
    subscribers: Sequence[str]
    delivery_mode: DeliveryMode
    timeout_ms: int
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if self.timeout_ms <= 0:
            raise ValueError("dispatch timeout must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        normalized = tuple(self.subscribers)
        if any(not subscriber.strip() for subscriber in normalized):
            raise ValueError("subscriber identifiers must not be empty")
        object.__setattr__(self, "subscribers", normalized)


@dataclass(frozen=True, slots=True)
class DispatchSummary:
    results: tuple[DeliveryResult, ...]
    started_at: datetime
    completed_at: datetime

    @property
    def successful(self) -> bool:
        return bool(self.results) and all(
            result.status is AckStatus.ACK for result in self.results
        )

    @property
    def failed(self) -> bool:
        return any(result.status is not AckStatus.ACK for result in self.results)
